# BIXOO Transportation Backend

## Overview
This is the FastAPI backend for the BIXOO Transportation module, designed to power the React transporter frontend.

## Architecture
- **Framework:** FastAPI
- **Database:** MySQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Auth:** JWT (pwdlib/Argon2)
- **Validation:** Pydantic

## Folder Structure
```text
Backend/
├── app/                  # Application code
│   ├── core/             # Configuration and security
│   ├── db/               # Database setup
│   ├── common/           # Shared utilities and responses
│   └── modules/          # Domain modules (auth, transporter, notifications)
├── docs/                 # Documentation and API mappings
├── migrations/           # Alembic migrations
├── scripts/              # Seed scripts
├── tests/                # Unit and integration tests
├── uploads/              # Uploaded files
├── .env                  # Environment variables
├── alembic.ini           # Alembic configuration
├── requirements.txt      # Dependencies
└── schema.sql            # MySQL Database schema
```

## Installation

### 1. Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Database Setup
Ensure MySQL is running. Create the database using `schema.sql`:
```powershell
mysql -u root -p < schema.sql
```

Update your `.env` file with your MySQL credentials:
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/bixoo_transportation
```

### 4. Migrations
Initialize and run migrations if you choose to use Alembic:
```powershell
alembic upgrade head
```

### 5. Create your account
Open the frontend login page, choose **Register**, and enter your own email,
mobile number, password and vehicle details. Registration saves the account in
MySQL and returns you to Login. Sign in using that same email and password.
Demo account creation and demo-data seed commands are disabled.

### 6. Run Server
From the `Backend` directory, start the FastAPI development server using the virtual environment's Python. This works in a new PowerShell terminal without activating the environment:
```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

If PowerShell reports that `uvicorn` is not recognized, use the command above. Uvicorn is installed inside `venv` and is only available as a bare command after activating that environment.

## API Documentation

### Frontend CORS origins

The backend allows `FRONTEND_URL`. In development it also allows both
`localhost` and `127.0.0.1` on Vite ports `5173` (dev) and `4173` (preview).
For another frontend port or deployment origin, add an explicit JSON list in
`Backend/.env`, for example:

```env
CORS_ORIGINS=["http://localhost:5174","http://127.0.0.1:5174"]
```

Origins must match the frontend browser address (scheme, host, and port), with
no page path. Restart the backend after changing `.env`; `--reload` reloads
Python source changes automatically. Production allows only `FRONTEND_URL`
and the explicitly configured `CORS_ORIGINS`.

Once running, the Swagger documentation is available at:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Testing
Run the automated tests using pytest:
```powershell
pytest
```
