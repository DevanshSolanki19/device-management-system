from .authentication import Home, Insert, login, logout_view, select, signup
from .inventory import (
    Device,
    stock_entry_Edit,
    stock_entry_delete,
    stock_entry_details,
    stock_entry_info,
    stock_entry_update,
)
from .master_data import (
    Bank_info,
    Delete,
    Device_Edit,
    Device_delete,
    Device_details,
    Device_info,
    Device_update,
    Stateoffice,
    Stateoffice_Edit,
    Stateoffice_delete,
    Stateoffice_update,
    Stateofficeadd,
    Stateofficeinfo,
    bank_details,
    categoryEdit,
    categoryupdate,
    pay_mode,
    pay_mode_Edit,
    pay_mode_delete,
    pay_mode_info,
    pay_mode_update,
    role_Edit,
    role_delete,
    role_details,
    role_info,
    role_update,
    vendor,
    vendor_Edit,
    vendor_delete,
    vendor_info,
    vendor_update,
    vendorinfo,
)
from .offices import (
    get_offices,
    issue_state_office,
    office_details,
    office_details_Edit,
    office_details_delete,
    office_details_info,
    office_details_list,
    office_details_update,
)
from .users import User, User_Edit, User_delete, User_info, User_list, User_update


__all__ = [name for name in globals() if not name.startswith("_")]
