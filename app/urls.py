from django.urls import path

from . import views


urlpatterns = [
    path("", views.login, name="login"),
    path("login/", views.login, name="login_page"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup, name="signup"),
    path("Insert/", views.Insert, name="Insert"),
    path("select/", views.select, name="select"),
    path("Home/", views.Home, name="Home"),
    path("vendor/", views.vendor, name="vendor"),
    path("vendor_info/", views.vendor_info, name="vendor_info"),
    path("vendorinfo/", views.vendorinfo, name="vendorinfo"),
    path("vendor_delete/<int:id>/", views.vendor_delete, name="vendor_delete"),
    path("vendor_Edit/<int:id>/", views.vendor_Edit, name="vendor_Edit"),
    path("vendor_update/", views.vendor_update, name="vendor_update"),
    path("Bank_Details/", views.bank_details, name="Bank_Details"),
    path("Bank_info/", views.Bank_info, name="Bank_info"),
    path("Delete/<int:id>/", views.Delete, name="Delete"),
    path("categoryEdit/<int:id>/", views.categoryEdit, name="categoryEdit"),
    path("categoryupdate/", views.categoryupdate, name="categoryupdate"),
    path("Stateoffice/", views.Stateoffice, name="Stateoffice"),
    path("Stateofficeadd/", views.Stateofficeadd, name="Stateofficeadd"),
    path("Stateofficeinfo/", views.Stateofficeinfo, name="Stateofficeinfo"),
    path(
        "Stateoffice_delete/<int:id>/",
        views.Stateoffice_delete,
        name="Stateoffice_delete",
    ),
    path(
        "Stateoffice_Edit/<int:id>/", views.Stateoffice_Edit, name="Stateoffice_Edit"
    ),
    path("Stateoffice_update/", views.Stateoffice_update, name="Stateoffice_update"),
    path("Device_details/", views.Device_details, name="Device_details"),
    path("Device_info/", views.Device_info, name="Device_info"),
    path("Device_Edit/<int:id>/", views.Device_Edit, name="Device_Edit"),
    path("Device_update/", views.Device_update, name="Device_update"),
    path("Device_delete/<int:id>/", views.Device_delete, name="Device_delete"),
    path("User/", views.User, name="User"),
    path("User_info/", views.User_info, name="User_info"),
    path("User_list/", views.User_list, name="User_list"),
    path("User_delete/<int:id>/", views.User_delete, name="User_delete"),
    path("User_Edit/<int:id>/", views.User_Edit, name="User_Edit"),
    path("User_update/", views.User_update, name="User_update"),
    path("pay_mode/", views.pay_mode, name="pay_mode"),
    path("pay_mode_info/", views.pay_mode_info, name="pay_mode_info"),
    path("pay_mode_Edit/<int:id>/", views.pay_mode_Edit, name="pay_mode_Edit"),
    path("pay_mode_update/", views.pay_mode_update, name="pay_mode_update"),
    path(
        "pay_mode_delete/<int:id>/", views.pay_mode_delete, name="pay_mode_delete"
    ),
    path("role_details/", views.role_details, name="role_details"),
    path("role_info/", views.role_info, name="role_info"),
    path("role_Edit/<int:id>/", views.role_Edit, name="role_Edit"),
    path("role_update/", views.role_update, name="role_update"),
    path("role_delete/<int:id>/", views.role_delete, name="role_delete"),
    path(
        "stock_entry_details/",
        views.stock_entry_details,
        name="stock_entry_details",
    ),
    path("stock_entry_info/", views.stock_entry_info, name="stock_entry_info"),
    path(
        "stock_entry_Edit/<int:id>/", views.stock_entry_Edit, name="stock_entry_Edit"
    ),
    path("stock_entry_update/", views.stock_entry_update, name="stock_entry_update"),
    path(
        "stock_entry_delete/<int:id>/",
        views.stock_entry_delete,
        name="stock_entry_delete",
    ),
    path("office_details/", views.office_details, name="office_details"),
    path(
        "office_details_info/", views.office_details_info, name="office_details_info"
    ),
    path(
        "office_details_list/", views.office_details_list, name="office_details_list"
    ),
    path(
        "office_details_delete/<int:office_id>/",
        views.office_details_delete,
        name="office_details_delete",
    ),
    path(
        "office_details_Edit/<int:office_id>/",
        views.office_details_Edit,
        name="office_details_Edit",
    ),
    path(
        "office_details_update/",
        views.office_details_update,
        name="office_details_update",
    ),
    path(
        "issue_state_office/", views.issue_state_office, name="issue_state_office"
    ),
    path("Device/", views.Device, name="Device"),
    path("get-offices/", views.get_offices, name="get_offices"),
]
