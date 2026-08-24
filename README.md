# Device Management System

A web-based device and inventory management application developed using Django and MySQL. The system manages devices, stock entries, offices, vendors, users, roles and other supporting master data.

## Features

* Secure login and session-based authentication
* Role-aware user management
* Vendor and bank management
* State and office management
* Device-type and stock-entry management
* Payment-mode and role management
* Create, read, update and delete operations
* Form validation using Django forms
* CSRF-protected form submissions
* Custom Django admin with search and filters
* MySQL database integration
* Automated Django tests

## Technology Stack

* Python
* Django
* MySQL
* Django ORM
* HTML
* CSS
* JavaScript
* Git and GitHub

## Application Modules

* Authentication
* User Management
* Role Management
* Vendor Management
* Bank Management
* State Office Management
* Office Management
* Device Management
* Stock Management
* Payment Mode Management

## Database Relationships

* One state can contain multiple offices.
* One device type can have multiple stock entries.
* One office can be assigned to multiple user profiles.
* One role can be assigned to multiple users.
* Each Django user has one DMS user profile.

## Project Structure

```text
app/
├── management/
├── migrations/
├── views/
│   ├── authentication.py
│   ├── inventory.py
│   ├── master_data.py
│   ├── offices.py
│   └── users.py
├── admin.py
├── forms.py
├── models.py
├── tests.py
└── urls.py

project/
├── settings.py
├── urls.py
├── asgi.py
└── wsgi.py

template/
static/
manage.py
```

## Local Setup

Clone the repository:

```bash
git clone https://github.com/DevanshSolanki19/device-management-system.git
cd device-management-system
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements-mysql.txt
```

Create the MySQL database:

```sql
CREATE DATABASE nict_dms CHARACTER SET utf8mb4;
```

Create `.env` from the example file:

```bash
cp .env.example .env
```

Configure your MySQL credentials inside `.env`:

```dotenv
DB_ENGINE=mysql
DB_NAME=nict_dms
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

Create the database tables:

```bash
python manage.py migrate
```

Create an administrator:

```bash
python manage.py createsuperuser
```

Start the server:

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser.

## Testing

Run the automated tests:

```bash
python manage.py test
```

## Author

**Devansh Solanki**

GitHub: [DevanshSolanki19](https://github.com/DevanshSolanki19)

