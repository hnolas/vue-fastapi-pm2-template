# How to Reset PostgreSQL Password

If you're encountering password authentication errors, follow these steps to reset the PostgreSQL password:

## 1. Connect to PostgreSQL as the postgres superuser:

```bash
sudo -u postgres psql
```

## 2. Set/reset the password for the postgres user:

Once connected to the PostgreSQL prompt, run:

```sql
ALTER USER postgres WITH PASSWORD 'postgres';
```

## 3. Verify the change:

```sql
\q
```

Then try to connect with the new password:

```bash
psql -U postgres -d app -h localhost
```
When prompted, enter the password 'postgres'.

## 4. If that doesn't work, you may need to modify PostgreSQL's authentication method:

Edit the pg_hba.conf file:

```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Look for lines that control local connections, and make sure they use 'md5' or 'password' authentication:

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

After making changes, restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

## 5. Verify the database exists:

```bash
sudo -u postgres psql -c "SELECT datname FROM pg_database;"
```

If the 'app' database doesn't exist, create it:

```bash
sudo -u postgres createdb app
```

## 6. Finally, try running the alembic migration again:

```bash
cd backend
alembic upgrade head
```