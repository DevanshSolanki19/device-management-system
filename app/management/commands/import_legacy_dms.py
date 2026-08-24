import re
from collections import defaultdict
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from app.models import (
    Bank,
    DeviceDetails,
    OfficeDetails,
    PaymentMode,
    Role,
    StateOffice,
    StockEntry,
    Vendor,
)


INSERT_RE = re.compile(r"INSERT INTO\s+`([^`]+)`\s+VALUES\s+(.+);$")
MYSQL_ESCAPES = {
    "0": "\0",
    "b": "\b",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "Z": "\x1a",
    "\\": "\\",
    "'": "'",
    '"': '"',
}


class LegacyDumpError(ValueError):
    pass


def _skip_space(text, index):
    while index < len(text) and text[index].isspace():
        index += 1
    return index


def _parse_quoted(text, index):
    index += 1
    characters = []

    while index < len(text):
        character = text[index]
        if character == "\\":
            index += 1
            if index >= len(text):
                raise LegacyDumpError("Incomplete escape sequence in SQL string.")
            escaped = text[index]
            characters.append(MYSQL_ESCAPES.get(escaped, escaped))
            index += 1
            continue

        if character == "'":
            if index + 1 < len(text) and text[index + 1] == "'":
                characters.append("'")
                index += 2
                continue
            return "".join(characters), index + 1

        characters.append(character)
        index += 1

    raise LegacyDumpError("Unterminated SQL string.")


def _parse_value(text, index):
    index = _skip_space(text, index)
    if index >= len(text):
        raise LegacyDumpError("A SQL value was expected.")

    if text[index] == "'":
        return _parse_quoted(text, index)

    start = index
    while index < len(text) and text[index] not in ",)":
        index += 1
    token = text[start:index].strip()
    if not token:
        raise LegacyDumpError("An empty unquoted SQL value was found.")
    if token.upper() == "NULL":
        return None, index
    if re.fullmatch(r"-?\d+", token):
        return int(token), index
    if re.fullmatch(r"-?\d+\.\d+", token):
        return float(token), index
    return token, index


def parse_mysql_value_list(text):
    """Parse the VALUES part produced by mysqldump without executing SQL."""
    rows = []
    index = 0

    while True:
        index = _skip_space(text, index)
        if index >= len(text):
            return rows
        if text[index] == ",":
            index += 1
            continue
        if text[index] != "(":
            raise LegacyDumpError(f"Expected '(' at character {index + 1}.")

        index += 1
        row = []
        while True:
            index = _skip_space(text, index)
            if index < len(text) and text[index] == ")":
                index += 1
                break

            value, index = _parse_value(text, index)
            row.append(value)
            index = _skip_space(text, index)

            if index >= len(text):
                raise LegacyDumpError("Unterminated SQL row.")
            if text[index] == ",":
                index += 1
                continue
            if text[index] == ")":
                index += 1
                break
            raise LegacyDumpError(f"Expected ',' or ')' at character {index + 1}.")

        rows.append(tuple(row))


def read_legacy_dump(dump_path):
    rows_by_table = defaultdict(list)
    insert_count = 0

    try:
        content = dump_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        content = dump_path.read_text(encoding="latin-1")
    except OSError as error:
        raise CommandError(f"Could not read the dump file: {error}") from error

    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line.startswith("INSERT INTO"):
            continue

        match = INSERT_RE.fullmatch(line)
        if not match:
            raise CommandError(
                f"Unsupported INSERT statement format at line {line_number}."
            )

        table_name, values_text = match.groups()
        try:
            rows_by_table[table_name].extend(parse_mysql_value_list(values_text))
        except LegacyDumpError as error:
            raise CommandError(
                f"Could not parse table '{table_name}' at line {line_number}: {error}"
            ) from error
        insert_count += 1

    if insert_count == 0:
        raise CommandError("No mysqldump INSERT statements were found in this file.")

    return rows_by_table


class Command(BaseCommand):
    help = "Safely import supported records from the original DMS MySQL data dump."

    model_order = [
        "State offices",
        "Offices",
        "Roles",
        "Banks",
        "Payment modes",
        "Devices",
        "Vendors",
        "Stock entries",
    ]

    def add_arguments(self, parser):
        parser.add_argument("dump_file", help="Path to the old mysqldump .sql file")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and show the result without saving any database changes",
        )

    def handle(self, *args, **options):
        dump_path = Path(options["dump_file"]).expanduser().resolve()
        if not dump_path.is_file():
            raise CommandError(f"Dump file does not exist: {dump_path}")

        rows_by_table = read_legacy_dump(dump_path)
        self.stats = {
            label: {"created": 0, "existing": 0, "skipped": 0}
            for label in self.model_order
        }
        self.warnings = []

        with transaction.atomic():
            self._import_rows(rows_by_table)
            if options["dry_run"]:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS("Legacy DMS import summary"))
        for label in self.model_order:
            stats = self.stats[label]
            self.stdout.write(
                f"  {label}: {stats['created']} created, "
                f"{stats['existing']} already present, {stats['skipped']} skipped"
            )

        for warning in self.warnings:
            self.stderr.write(self.style.WARNING(f"Warning: {warning}"))

        old_account_rows = sum(
            len(rows_by_table.get(table_name, []))
            for table_name in ("user", "hello", "auth_user")
        )
        if old_account_rows:
            self.stdout.write(
                self.style.WARNING(
                    f"Skipped {old_account_rows} legacy account rows. "
                    "Create secure Django users with createsuperuser or the User page."
                )
            )

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING("Dry run complete; no database changes were saved.")
            )
        else:
            self.stdout.write(self.style.SUCCESS("Legacy business data import completed."))

    def _mark(self, label, created=None, skipped=False):
        if skipped:
            self.stats[label]["skipped"] += 1
        elif created:
            self.stats[label]["created"] += 1
        else:
            self.stats[label]["existing"] += 1

    def _warn_bad_row(self, table_name, row, expected_columns, label):
        legacy_id = row[0] if row else "unknown"
        self._mark(label, skipped=True)
        self.warnings.append(
            f"{table_name} row {legacy_id} has {len(row)} columns; "
            f"expected {expected_columns}."
        )

    def _import_rows(self, rows_by_table):
        states_by_legacy_id = {}

        for row in rows_by_table.get("state_dt", []):
            if len(row) != 3:
                self._warn_bad_row("state_dt", row, 3, "State offices")
                continue
            legacy_id, state_name, iso_code = row
            state_name = str(state_name).strip()
            iso_code = str(iso_code).strip().upper()
            state = StateOffice.objects.filter(state_iso_code=iso_code).first()
            if state is None:
                state = StateOffice.objects.filter(state=state_name).first()
            created = state is None
            if created:
                state = StateOffice.objects.create(
                    state=state_name, state_iso_code=iso_code
                )
            states_by_legacy_id[int(legacy_id)] = state
            self._mark("State offices", created=created)

        for row in rows_by_table.get("office_dt", []):
            if len(row) != 10:
                self._warn_bad_row("office_dt", row, 10, "Offices")
                continue
            (
                legacy_id,
                name,
                legacy_state_id,
                division,
                district,
                city,
                address,
                pin,
                phone_no,
                mobile_no,
            ) = row
            state = states_by_legacy_id.get(int(legacy_state_id))
            if state is None:
                self._mark("Offices", skipped=True)
                self.warnings.append(
                    f"office_dt row {legacy_id} refers to missing state "
                    f"{legacy_state_id}."
                )
                continue
            _, created = OfficeDetails.objects.get_or_create(
                name=str(name).strip(),
                state=state,
                city=str(city).strip(),
                defaults={
                    "division": str(division).strip(),
                    "district": str(district).strip(),
                    "address": str(address).strip(),
                    "pin": str(pin).strip(),
                    "phone_no": str(phone_no).strip(),
                    "mobile_no": str(mobile_no).strip(),
                },
            )
            self._mark("Offices", created=created)

        for row in rows_by_table.get("role_dt", []):
            if len(row) != 2:
                self._warn_bad_row("role_dt", row, 2, "Roles")
                continue
            _, role_name = row
            _, created = Role.objects.get_or_create(role=str(role_name).strip())
            self._mark("Roles", created=created)

        for row in rows_by_table.get("bank_dt", []):
            if len(row) != 2:
                self._warn_bad_row("bank_dt", row, 2, "Banks")
                continue
            _, bank_name = row
            _, created = Bank.objects.get_or_create(name=str(bank_name).strip())
            self._mark("Banks", created=created)

        for row in rows_by_table.get("pay_mode", []):
            if len(row) != 2:
                self._warn_bad_row("pay_mode", row, 2, "Payment modes")
                continue
            _, mode = row
            _, created = PaymentMode.objects.get_or_create(mode=str(mode).strip())
            self._mark("Payment modes", created=created)

        devices_by_name = {}
        for row in rows_by_table.get("device_dt", []):
            if len(row) != 2:
                self._warn_bad_row("device_dt", row, 2, "Devices")
                continue
            _, device_name = row
            device_name = str(device_name).strip()
            device, created = DeviceDetails.objects.get_or_create(
                device_name=device_name
            )
            devices_by_name[device_name.casefold()] = device
            self._mark("Devices", created=created)

        for row in rows_by_table.get("vendor_dt", []):
            if len(row) != 8:
                self._warn_bad_row("vendor_dt", row, 8, "Vendors")
                continue
            (
                legacy_id,
                vendor_name,
                address,
                city,
                state_name,
                pin,
                mobile,
                gstin,
            ) = row
            values = {
                "v_name": str(vendor_name).strip(),
                "address": str(address).strip(),
                "city": str(city).strip(),
                "state": str(state_name).strip(),
                "pin": str(pin).strip(),
                "mobile": str(mobile).strip(),
                "gstin": str(gstin).strip().upper(),
            }
            existing = Vendor.objects.filter(gstin=values["gstin"]).first()
            if existing is not None:
                comparable_fields = (
                    "v_name",
                    "address",
                    "city",
                    "state",
                    "pin",
                    "mobile",
                )
                if all(getattr(existing, field) == values[field] for field in comparable_fields):
                    self._mark("Vendors", created=False)
                else:
                    self._mark("Vendors", skipped=True)
                    self.warnings.append(
                        f"vendor_dt row {legacy_id} uses an existing GSTIN with "
                        "different vendor details."
                    )
                continue
            Vendor.objects.create(**values)
            self._mark("Vendors", created=True)

        for row in rows_by_table.get("stock_entry", []):
            if len(row) != 5:
                self._warn_bad_row("stock_entry", row, 5, "Stock entries")
                continue
            (
                legacy_id,
                purchase_order_number,
                device_name,
                received_date,
                device_number,
            ) = row
            normalized_device_name = str(device_name).strip()
            device = devices_by_name.get(normalized_device_name.casefold())
            if device is None:
                device = DeviceDetails.objects.filter(
                    device_name__iexact=normalized_device_name
                ).first()
            if device is None:
                self._mark("Stock entries", skipped=True)
                self.warnings.append(
                    f"stock_entry row {legacy_id} refers to unknown device "
                    f"'{normalized_device_name}'."
                )
                continue
            try:
                parsed_date = date.fromisoformat(str(received_date))
            except ValueError:
                self._mark("Stock entries", skipped=True)
                self.warnings.append(
                    f"stock_entry row {legacy_id} has an invalid received date."
                )
                continue

            values = {
                "purchase_order_number": str(purchase_order_number),
                "device_type": device,
                "device_received_date": parsed_date,
                "device_number": str(device_number).strip(),
            }
            existing = StockEntry.objects.filter(
                device_number=values["device_number"]
            ).first()
            if existing is not None:
                comparable_fields = (
                    "purchase_order_number",
                    "device_type",
                    "device_received_date",
                )
                if all(getattr(existing, field) == values[field] for field in comparable_fields):
                    self._mark("Stock entries", created=False)
                else:
                    self._mark("Stock entries", skipped=True)
                    self.warnings.append(
                        f"stock_entry row {legacy_id} uses an existing device "
                        "number with different stock details."
                    )
                continue
            StockEntry.objects.create(**values)
            self._mark("Stock entries", created=True)
