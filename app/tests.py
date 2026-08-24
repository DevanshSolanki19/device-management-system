from datetime import date
from io import StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import (
    Bank,
    DMSUserProfile,
    DeviceDetails,
    OfficeDetails,
    PaymentMode,
    Role,
    StateOffice,
    StockEntry,
    Vendor,
)


class DMSProjectTests(TestCase):
    def setUp(self):
        self.role = Role.objects.create(role="Admin")
        self.user = get_user_model().objects.create_user(
            username="devansh", password="StrongTestPass123!"
        )
        self.user.dms_profile.role = self.role
        self.user.dms_profile.save(update_fields=["role"])

    def test_password_is_hashed_and_role_login_creates_session(self):
        self.assertNotEqual(self.user.password, "StrongTestPass123!")
        response = self.client.post(
            reverse("select"),
            {
                "Role": "Admin",
                "username": "devansh",
                "password": "StrongTestPass123!",
            },
        )
        self.assertRedirects(response, reverse("Home"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_wrong_role_does_not_login(self):
        response = self.client.post(
            reverse("select"),
            {
                "Role": "Executive(H.O.)",
                "username": "devansh",
                "password": "StrongTestPass123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_protected_page_redirects_anonymous_user(self):
        response = self.client.get(reverse("vendor"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('vendor')}")

    def test_vendor_post_uses_orm(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("vendor_info"),
            {
                "v_name": "Test Vendor",
                "address": "MG Road",
                "city": "Indore",
                "state": "Madhya Pradesh",
                "pin": "452001",
                "mobile": "9000000000",
                "gstin": "23ABCDE1234F1Z5",
            },
        )
        self.assertRedirects(response, reverse("vendor"))
        self.assertTrue(Vendor.objects.filter(v_name="Test Vendor").exists())

    def test_stock_entry_uses_device_foreign_key(self):
        device = DeviceDetails.objects.create(device_name="Laptop")
        stock = StockEntry.objects.create(
            purchase_order_number="123456789",
            device_type=device,
            device_received_date=date(2026, 8, 23),
            device_number="LAP-001",
        )
        self.assertEqual(stock.device_type, device)

    def test_state_office_template_compatibility_property(self):
        state = StateOffice.objects.create(state="Madhya Pradesh", state_iso_code="MP")
        self.assertEqual(state.state_id, state.pk)

    def test_all_original_pages_render_with_orm_data(self):
        state = StateOffice.objects.create(state="Madhya Pradesh", state_iso_code="MP")
        office = OfficeDetails.objects.create(
            name="Indore Office",
            state=state,
            division="Indore",
            district="Indore",
            city="Indore",
            address="Vijay Nagar",
            pin="452010",
            phone_no="07314000000",
            mobile_no="9000000000",
        )
        self.user.dms_profile.office = office
        self.user.dms_profile.save(update_fields=["office"])
        vendor = Vendor.objects.create(
            v_name="Vendor",
            address="MG Road",
            city="Indore",
            state="Madhya Pradesh",
            pin="452001",
            mobile="9111111111",
            gstin="23ABCDE1234F1Z5",
        )
        bank = Bank.objects.create(name="SBI")
        payment_mode = PaymentMode.objects.create(mode="Bank Transfer")
        device = DeviceDetails.objects.create(device_name="Laptop")
        stock = StockEntry.objects.create(
            purchase_order_number="123456789",
            device_type=device,
            device_received_date=date(2026, 8, 23),
            device_number="LAP-001",
        )

        self.client.force_login(self.user)
        urls = [
            reverse("Home"),
            reverse("vendor"),
            reverse("vendorinfo"),
            reverse("vendor_Edit", args=[vendor.pk]),
            reverse("Bank_Details"),
            reverse("categoryEdit", args=[bank.pk]),
            reverse("Stateoffice"),
            reverse("Stateofficeinfo"),
            reverse("Stateoffice_Edit", args=[state.pk]),
            reverse("Device_details"),
            reverse("Device_Edit", args=[device.pk]),
            reverse("User"),
            reverse("User_list"),
            reverse("User_Edit", args=[self.user.pk]),
            reverse("pay_mode"),
            reverse("pay_mode_Edit", args=[payment_mode.pk]),
            reverse("role_details"),
            reverse("role_Edit", args=[self.role.pk]),
            reverse("stock_entry_details"),
            reverse("stock_entry_Edit", args=[stock.pk]),
            reverse("office_details"),
            reverse("office_details_list"),
            reverse("office_details_Edit", args=[office.pk]),
            reverse("issue_state_office"),
            reverse("Device"),
            reverse("get_offices") + f"?state_id={state.pk}",
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_original_form_posts_create_related_models(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse("Stateofficeadd"),
            {"state": "Madhya Pradesh", "state_iso_code": "MP"},
        )
        state = StateOffice.objects.get(state_iso_code="MP")

        self.client.post(
            reverse("office_details_info"),
            {
                "name": "Indore Office",
                "state_id": state.pk,
                "division": "Indore",
                "district": "Indore",
                "city": "Indore",
                "address": "Vijay Nagar",
                "pin": "452010",
                "phone_no": "07314000000",
                "mobile_no": "9000000000",
            },
        )
        office = OfficeDetails.objects.get(name="Indore Office")

        self.client.post(reverse("Device_info"), {"device_name": "Laptop"})
        device = DeviceDetails.objects.get(device_name="Laptop")
        self.client.post(
            reverse("stock_entry_info"),
            {
                "purchase_order_number": "123456789",
                "Device_type": device.device_name,
                "Device_received_date": "2026-08-23",
                "Device_number": "LAP-001",
            },
        )
        self.assertTrue(StockEntry.objects.filter(device_number="LAP-001").exists())

        self.client.post(reverse("Bank_info"), {"name": "SBI"})
        self.client.post(reverse("pay_mode_info"), {"mode": "Bank Transfer"})
        self.assertTrue(Bank.objects.filter(name="SBI").exists())
        self.assertTrue(PaymentMode.objects.filter(mode="Bank Transfer").exists())

        self.client.post(
            reverse("User_info"),
            {
                "login_id": "stock_manager",
                "password": "StrongManagerPass123!",
                "office_id": office.pk,
                "role": "Stock Manager(H.O.)",
                "login_status": "on",
                "create_at": "2026-08-23",
                "updated_at": "2026-08-23",
                "token": "demo-token",
            },
        )
        profile = DMSUserProfile.objects.select_related("user", "office", "role").get(
            user__username="stock_manager"
        )
        self.assertTrue(profile.user.check_password("StrongManagerPass123!"))
        self.assertEqual(profile.office, office)
        self.assertEqual(profile.role.role, "Stock Manager(H.O.)")


class LegacyImportTests(TestCase):
    legacy_dump = """\
INSERT INTO `state_dt` VALUES (1,'Madhya Pradesh','IN-MP');
INSERT INTO `office_dt` VALUES (1,'Indore Office',1,'Indore','Indore','Indore','MG Road','452001','07314000000','9000000000');
INSERT INTO `role_dt` VALUES (1,'Admin'),(2,'Admin');
INSERT INTO `bank_dt` VALUES (1,'State Bank of India');
INSERT INTO `pay_mode` VALUES (1,'Online mode');
INSERT INTO `device_dt` VALUES (1,'Laptop'),(2,'Printer');
INSERT INTO `vendor_dt` VALUES (1,'Vendor One','Address 1','Indore','Madhya Pradesh','452001','9000000000','GST-1'),(2,'Vendor Two','Address 2','Indore','Madhya Pradesh','452001','9111111111','GST-1');
INSERT INTO `stock_entry` VALUES (1,123,'Laptop','2024-05-01','DEVICE-1'),(2,456,'Printer','2024-05-02','DEVICE-1');
INSERT INTO `hello` VALUES ('Admin','legacy-user','plain-text-password');
"""

    def run_import(self, *, dry_run=False):
        with NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as dump_file:
            dump_file.write(self.legacy_dump)
            dump_path = Path(dump_file.name)
        try:
            stdout = StringIO()
            stderr = StringIO()
            call_command(
                "import_legacy_dms",
                str(dump_path),
                dry_run=dry_run,
                stdout=stdout,
                stderr=stderr,
            )
            return stdout.getvalue(), stderr.getvalue()
        finally:
            dump_path.unlink(missing_ok=True)

    def test_legacy_import_maps_relationships_and_skips_insecure_users(self):
        stdout, stderr = self.run_import()

        self.assertEqual(StateOffice.objects.count(), 1)
        self.assertEqual(OfficeDetails.objects.count(), 1)
        self.assertEqual(Role.objects.count(), 1)
        self.assertEqual(Bank.objects.count(), 1)
        self.assertEqual(PaymentMode.objects.count(), 1)
        self.assertEqual(DeviceDetails.objects.count(), 2)
        self.assertEqual(Vendor.objects.count(), 1)
        self.assertEqual(StockEntry.objects.count(), 1)
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(
            StockEntry.objects.get().device_type.device_name,
            "Laptop",
        )
        self.assertIn("Skipped 1 legacy account rows", stdout)
        self.assertIn("existing GSTIN", stderr)
        self.assertIn("existing device number", stderr)

    def test_legacy_import_dry_run_does_not_save_changes(self):
        stdout, _ = self.run_import(dry_run=True)

        self.assertEqual(StateOffice.objects.count(), 0)
        self.assertEqual(DeviceDetails.objects.count(), 0)
        self.assertIn("Dry run complete", stdout)
