# PostgreSQL Setup and Troubleshooting Guide

## Quick Fix for Connection Errors

If you're experiencing the `socket.gaierror: [Errno -3] Temporary failure in name resolution` error with PostgreSQL, follow these steps to resolve it:

### 1. Update All Database Connection Information

#### Update your `.env` file
```bash
# Edit your .env file (create it if it doesn't exist)
cp .env.example .env
nano .env

# Make sure the PostgreSQL settings look like this:
PGHOST=localhost
PGUSER=postgres
PGPASSWORD=password  # Replace with your actual password
PGDATABASE=app
PGPORT=5432
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost/app
```

#### Update `alembic.ini`
```bash
# Edit the alembic.ini file
nano backend/alembic.ini

# Find the sqlalchemy.url line and change it to:
sqlalchemy.url = postgresql+asyncpg://postgres:password@localhost/app
```

### 2. Verify PostgreSQL is Running

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# If not running, start it:
sudo systemctl start postgresql
```

### 3. Create the Database if Needed

```bash
# Connect to PostgreSQL as the postgres user
sudo -u postgres psql

# Inside the PostgreSQL prompt, create the database
CREATE DATABASE app;

# Verify the database was created
\l

# Exit PostgreSQL
\q
```

### 4. Testing the Connection

```bash
# Test direct connection to PostgreSQL (should prompt for password)
psql -h localhost -U postgres -d app

# If you get a connection, you should see:
# psql (12.x)
# Type "help" for help.
# app=#

# Exit with:
\q
```

### 5. If Still Experiencing Issues

If you're still having problems, verify your PostgreSQL configuration allows connections:

```bash
# Edit PostgreSQL authentication config
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Add or update this line to allow local connections:
# local   all             postgres                                md5
# host    all             all             127.0.0.1/32            md5
# host    all             all             ::1/128                 md5

# Save and restart PostgreSQL
sudo systemctl restart postgresql
```

## Using PostgreSQL with Alembic

After fixing the connection, you can use Alembic to manage your database migrations:

```bash
# Navigate to the backend directory
cd backend

# Run migrations
alembic upgrade head
```

## Common Errors and Solutions

### Error: "Role 'postgres' does not exist"

```bash
# Create the postgres role
sudo -u postgres createuser --superuser postgres
```

### Error: "Database 'app' does not exist"

```bash
# Create the database
sudo -u postgres createdb app
```

### Error: "Password authentication failed for user 'postgres'"

```bash
# Set a password for the postgres user
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
```

Make sure your connection string uses the same password throughout:

1. Check all places that define the password:
```bash
# In your .env file:
PGPASSWORD=postgres
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/app

# In alembic.ini:
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost/app
```

2. If you still have issues, verify PostgreSQL authentication config:
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Make sure lines for local connections use 'md5' authentication:
# local   all             postgres                                md5
# host    all             all             127.0.0.1/32            md5
# host    all             all             ::1/128                 md5

# After changes, restart PostgreSQL:
sudo systemctl restart postgresql
```

### Error: "Could not connect to server: Connection refused"

```bash
# Make sure PostgreSQL is running and listening on the correct interface
sudo netstat -tulpn | grep postgres

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```