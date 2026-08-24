# Device Management System — Original Templates, Proper Django Backend

This version keeps the original HTML/CSS templates and the same pages, labels,
colours, menus, and feature flow from the uploaded project. Only the Django
backend and the necessary template actions were corrected.

## What was changed

- The original templates in `template/` are still used.
- Raw `mysql.connector` queries were replaced with Django ORM queries.
- Database tables are represented by models in `app/models.py`.
- Server-side validation is handled by forms in `app/forms.py`.
- Django authentication now creates a real login session.
- Passwords are stored with Django password hashing, never as plain text.
- The selected role is checked during login.
- CRUD requests use model instances and `get_object_or_404()`.
- Delete operations use POST forms with CSRF protection.
- URLs use Django URL names instead of broken literal paths.
- Database credentials are read from environment variables.
- Django admin and automated tests were added.

No new dashboard design or additional inventory workflow was introduced.

## Project structure

```text
project/
├── app/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── signals.py
│   ├── urls.py
│   ├── views/
│   │   ├── authentication.py
│   │   ├── inventory.py
│   │   ├── master_data.py
│   │   ├── offices.py
│   │   └── users.py
│   └── tests.py
├── project/
│   ├── settings.py
│   └── urls.py
├── template/          # The original templates supplied in project.zip
├── static/
├── .env.example
├── requirements.txt
└── manage.py
```

## Models matching the original pages

| Original page/table | Django model |
| --- | --- |
| Vendor | `Vendor` |
| Bank Details | `Bank` |
| State Office | `StateOffice` |
| Office Details | `OfficeDetails` |
| Device Details | `DeviceDetails` |
| Stock Entry | `StockEntry` |
| Pay Mode | `PaymentMode` |
| Role Details | `Role` |
| User | Django `User` + `DMSUserProfile` |

`OfficeDetails.state` and `StockEntry.device_type` are proper foreign-key
relationships. Application users use Django's built-in `User` model, while the
office, role, status, and token fields are stored in `DMSUserProfile`.

## Run the project

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\activate
```

Open <http://127.0.0.1:8000/>. A superuser can log in by selecting `Admin`.

Run validation and tests:

```bash
python manage.py check
python manage.py test
```

## Optional MySQL setup

The project uses SQLite by default so it starts immediately. To use MySQL:

```bash
pip install -r requirements-mysql.txt
```

Create a database and dedicated user, then update `.env`:

```dotenv
DB_ENGINE=mysql
DB_NAME=nict_dms
DB_USER=dms_user
DB_PASSWORD=your-strong-password
DB_HOST=127.0.0.1
DB_PORT=3306
```

Then run `python manage.py migrate`.

The old ZIP did not contain a database dump, so existing raw MySQL records are
not included in this project. Create new records through the existing pages or
export/import the old data separately. Old plain-text passwords must not be
imported; create those accounts again through Django.

## Import the old DMS data dump

The project includes a safe one-time importer for the original data-only MySQL
dump. It imports state offices, offices, roles, banks, payment modes, devices,
vendors, and stock entries into the proper Django models.

First configure MySQL in `.env` and create the Django tables:

```bash
python manage.py migrate
```

Preview the import without saving anything:

```bash
python manage.py import_legacy_dms /absolute/path/to/demo.sql --dry-run
```

Review the summary and warnings. Then perform the import:

```bash
python manage.py import_legacy_dms /absolute/path/to/demo.sql
```

The command is safe to run again: records already present are reported instead
of being duplicated. Conflicting legacy rows, such as repeated GSTIN or device
numbers with different details, are skipped and reported.

Legacy `hello`, `user`, `auth_user`, session, permission, and migration records
are deliberately not copied. Some old login tables contain plain-text
passwords, and the internal Django tables belong to the old application. Create
secure accounts for this project instead:

```bash
python manage.py createsuperuser
```
