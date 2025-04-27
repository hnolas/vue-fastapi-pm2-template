# Participant Management Interface & Fitbit Data Integration System

This project is a comprehensive system for managing research participants, SMS messaging, and Fitbit data integration. It allows researchers to manage participant information, track message delivery, and collect Fitbit data through OAuth integration.

## Features

- Participant Management Interface with CRUD operations
- SMS messaging system with randomized messages and 1-week no-repeat rule
- Message history tracking (datetime, content, bucket, status)
- Timezone-aware message scheduling based on participant location
- Fitbit OAuth integration for data collection
- Secure web interface for participant Fitbit authorization

## Tech Stack

- **Frontend:** Vue 3 with TypeScript, Pinia, Vue Router
- **Backend:** FastAPI with SQLAlchemy, Pydantic, and Alembic
- **Database:** PostgreSQL
- **Deployment:** PM2 (frontend) & Uvicorn (backend)
- **SMS Integration:** Twilio

## Frontend Architecture

The frontend is built with Vue 3 using the Composition API and TypeScript for type safety. It follows a structured architecture with the following key components:

### Key Components

- **Centralized API Client**: Uses Axios with interceptors for consistent authentication handling and error management
- **Typed Stores**: Pinia stores with TypeScript interfaces for state management
- **Type Definitions**: Comprehensive TypeScript interfaces for all data models
- **Vue Router**: Route-based code splitting and navigation guards for authentication
- **Error Handling**: Standardized error handling and messaging throughout the application

### Store Pattern

The application uses Pinia stores with a consistent pattern:
- Each domain area has its own store (participants, messages, etc.)
- All stores follow a similar structure with loading states, error handling, and API integration
- Stores use the centralized API client for all requests
- Type safety is enforced with TypeScript interfaces

### API Integration

All API communication is handled through a centralized Axios client that:
1. Automatically attaches authentication tokens to requests
2. Handles token expiration and redirects to login when needed
3. Provides consistent error handling patterns
4. Configures base URL from environment variables

### TypeScript Type Safety

The application leverages TypeScript's type system for improved code quality and developer experience:

- **Interface Definitions**: All data models have corresponding TypeScript interfaces
- **API Response Types**: API responses are properly typed for IDE autocomplete and compile-time checks
- **Store Type Safety**: Pinia stores use typed state and typed actions
- **Environment Variables**: Environment variables are properly typed with interface declarations
- **Strict Null Checking**: Enabled strict null checking for preventing null reference errors
- **Error Typing**: Standardized error handling with typed error responses

### Frontend Folder Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── assets/             # Application assets (images, fonts)
│   ├── components/         # Reusable Vue components
│   │   ├── common/         # Generic UI components
│   │   ├── fitbit/         # Fitbit-related components
│   │   ├── layout/         # Layout components
│   │   ├── messages/       # Messaging components
│   │   └── participants/   # Participant management components
│   ├── plugins/            # Vue plugins
│   │   └── axios.ts        # Centralized Axios client
│   ├── router/             # Vue Router configuration
│   ├── stores/             # Pinia stores
│   │   ├── auth.ts         # Authentication store
│   │   ├── fitbit.ts       # Fitbit integration store
│   │   ├── messageContent.ts # Message content/templates store
│   │   ├── messages.ts     # SMS messaging store
│   │   └── participants.ts # Participants store
│   ├── types/              # TypeScript type definitions
│   │   ├── auth.ts         # Authentication types
│   │   ├── fitbit.ts       # Fitbit data types
│   │   ├── message.ts      # Messaging types
│   │   └── participant.ts  # Participant types
│   └── views/              # Page components
├── .env                    # Environment variables
└── vite.config.ts          # Vite configuration
```

## Project Structure

```
├── backend/              # FastAPI backend
│   ├── app/              # Application code
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic services
│   ├── alembic/          # Database migrations
├── frontend/             # Vue 3 frontend
│   ├── src/              # Source code
│   │   ├── components/   # Vue components
│   │   ├── stores/       # Pinia stores
│   │   ├── views/        # Page views
│   │   └── router/       # Vue Router configuration
└── .env.example          # Environment variables template
```

## Deployment Guide

This guide will walk you through deploying the application using PM2 and Uvicorn on a Linux server without Docker.

### Prerequisites

- A Linux server with Node.js, Python, and PostgreSQL installed
- Domain name (optional for SSL/TLS)
- Twilio account for SMS messaging

### 1. Install Required Software

```bash
# Update your system
sudo apt update
sudo apt upgrade -y

# Install Node.js and npm
sudo apt install -y nodejs npm

# Install PM2 globally
sudo npm install -g pm2

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Nginx
sudo apt install -y nginx
```

### 2. Clone the Repository

```bash
# Navigate to where you want to deploy
cd /opt

# Clone your repository
sudo git clone https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git pmi-fitbit-sms
sudo chown -R $USER:$USER /opt/pmi-fitbit-sms
cd pmi-fitbit-sms
```

### 3. Setting Up Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit the .env file with your actual values
nano .env
```

Update the following values in your `.env` file:

```
# Database configuration
PGHOST=localhost
PGUSER=postgres
PGPASSWORD=your_secure_password
PGDATABASE=app
PGPORT=5432
DATABASE_URL=postgresql://postgres:your_secure_password@localhost:5432/app

# Security
SECRET_KEY=generate_a_random_key

# Twilio configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# External URL for callback endpoints
EXTERNAL_BASE_URL=https://yourdomain.com
```

#### Generate a Secure SECRET_KEY

You can generate a secure random key using:

```bash
# Generate a secure random key
openssl rand -hex 32
```

Copy the output and paste it as your SECRET_KEY in the .env file.

### 4. Database Setup

Set up the PostgreSQL database:

```bash
# Connect to PostgreSQL as the postgres user
sudo -u postgres psql

# Inside the PostgreSQL prompt, create a database and user
CREATE DATABASE app;
CREATE USER youruser WITH ENCRYPTED PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE app TO youruser;

# Exit PostgreSQL
\q
```

Update your .env file with the database credentials you just created.

Now, set up the Python virtual environment and run migrations:

```bash
# Navigate to the backend directory
cd /opt/pmi-fitbit-sms/backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Deactivate the virtual environment when done
deactivate
```

#### Adding Sample Data (Optional)

If you want to add sample data for testing:

```bash
# Navigate to the backend directory
cd /opt/pmi-fitbit-sms/backend

# Activate the virtual environment
source venv/bin/activate

# Run the sample data script
python -m add_sample_data

# Deactivate the virtual environment when done
deactivate
```

### 5. Setting Up the Frontend with PM2

```bash
# Navigate to the frontend directory
cd /opt/pmi-fitbit-sms/frontend

# Install dependencies
npm install

# Build the frontend for production
npm run build

# Create a PM2 configuration file
cat > ecosystem.config.cjs << 'EOL'
module.exports = {
  apps: [{
    name: "pmi-frontend",
    script: "npm",
    args: "run preview",
    env: {
      NODE_ENV: "production",
      PORT: 5000
    }
  }]
};
EOL

# Start the frontend with PM2
pm2 start ecosystem.config.cjs

# Save the PM2 configuration to run on system startup
pm2 save
pm2 startup
```

### 6. Setting Up the Backend with Uvicorn

```bash
# Navigate to the backend directory
cd /opt/pmi-fitbit-sms/backend

# Create a systemd service for the backend
sudo nano /etc/systemd/system/pmi-backend.service
```

Add the following content to the service file:

```
[Unit]
Description=PMI Fitbit Backend Service
After=network.target

[Service]
User=your_username
Group=your_group
WorkingDirectory=/opt/pmi-fitbit-sms/backend
ExecStart=/opt/pmi-fitbit-sms/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
SyslogIdentifier=pmi-backend
Environment="PATH=/opt/pmi-fitbit-sms/backend/venv/bin"
Environment="DATABASE_URL=postgresql://postgres:your_secure_password@localhost:5432/app"
Environment="SECRET_KEY=your_secret_key"
Environment="TWILIO_ACCOUNT_SID=your_twilio_account_sid"
Environment="TWILIO_AUTH_TOKEN=your_twilio_auth_token"
Environment="TWILIO_PHONE_NUMBER=your_twilio_phone_number"
Environment="EXTERNAL_BASE_URL=https://yourdomain.com"

[Install]
WantedBy=multi-user.target
```

Start and enable the service:

```bash
sudo systemctl enable pmi-backend
sudo systemctl start pmi-backend
```

### 7. Configuring Nginx as a Reverse Proxy

Create an nginx configuration file:

```bash
# Create the site configuration
sudo nano /etc/nginx/sites-available/pmi-fitbit-sms
```

Add the following content:

```
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /redoc {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /openapi.json {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site and restart nginx:

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/pmi-fitbit-sms /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test the configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### 8. Configuring SSL/TLS with Let's Encrypt (Optional)

For production deployments, you should configure SSL/TLS:

```bash
# Install Certbot with nginx plugin
sudo apt install -y certbot python3-certbot-nginx

# Obtain and configure SSL certificate
sudo certbot --nginx -d yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

The certbot nginx plugin will automatically update your nginx configuration for SSL.

### 9. Setting Up Scheduled Tasks

Create cron jobs to handle scheduled tasks:

```bash
# Edit crontab
crontab -e

# Add the following lines:
# Refresh Fitbit tokens every 12 hours
0 */12 * * * cd /opt/pmi-fitbit-sms/backend && /opt/pmi-fitbit-sms/backend/venv/bin/python -m app.refresh_tokens

# Sync Fitbit data every hour
0 * * * * cd /opt/pmi-fitbit-sms/backend && /opt/pmi-fitbit-sms/backend/venv/bin/python -m app.sync_fitbit_data

# Trigger scheduled messages every 15 minutes
*/15 * * * * cd /opt/pmi-fitbit-sms/backend && /opt/pmi-fitbit-sms/backend/venv/bin/python -m app.send_scheduled_messages
```

### 10. Database Backup Strategy

Set up automatic backups:

```bash
# Create backup script
sudo nano /usr/local/bin/backup-pmi-db.sh
```

Add the following content:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/pmi-database"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p $BACKUP_DIR

# PostgreSQL backup using pg_dump
PGPASSWORD="your_secure_password" pg_dump -h localhost -U postgres -d app > "$BACKUP_DIR/pmi_db_backup_$TIMESTAMP.sql"

# Delete backups older than 14 days
find $BACKUP_DIR -type f -mtime +14 -name "pmi_db_backup_*.sql" -delete
```

Make it executable and add to cron:

```bash
sudo chmod +x /usr/local/bin/backup-pmi-db.sh
crontab -e
# Add:
0 2 * * * /usr/local/bin/backup-pmi-db.sh
```

## Database Migrations with Alembic

This project uses Alembic for database schema migrations. Alembic is a database migration tool for SQLAlchemy that helps manage changes to the database schema over time.

### What Alembic Does

1. **Database Schema Versioning**: Alembic tracks all changes to your database schema using migration files (version control for your database structure).

2. **Automated Migrations**: It can automatically generate migration scripts by comparing your SQLAlchemy models with the current database state.

3. **Safe Upgrades and Downgrades**: Each migration can be applied (upgrade) or reversed (downgrade) without losing data.

### How We're Using Alembic

1. **Migration Files**: In the `/backend/alembic/versions/` directory, we store migration files that represent each change to the database schema.

2. **Configuration**: The `alembic.ini` file in the backend directory contains configuration for connecting to the database and running migrations.

3. **Key Commands**:
   ```bash
   # Apply all pending migrations
   cd /opt/pmi-fitbit-sms/backend
   source venv/bin/activate
   alembic upgrade head
   
   # Generate a new migration based on model changes
   alembic revision --autogenerate -m "description of changes"
   
   # Revert the last migration
   alembic downgrade -1
   ```

### Example Workflow

When making changes to the database models:

1. Update the model definitions in `backend/app/models/`
2. Generate a migration: `alembic revision --autogenerate -m "add new field to model"`
3. Review the generated migration file in `backend/alembic/versions/`
4. Apply the migration: `alembic upgrade head`
5. Verify the changes in the database

This ensures database schema changes are tracked, reversible, and consistent across all environments.

## Recent Updates

### Version 1.2.0 (April 2025)

- **Frontend Refactoring**:
  - Created centralized Axios client in `src/plugins/axios.ts` with auth token handling and interceptors
  - Refactored all store files to use the centralized API client
  - Improved TypeScript type definitions for better IDE support and type checking
  - Added proper environment variable type declarations
  - Standardized error handling across all components

- **API Improvements**:
  - Added consistent error response format
  - Improved validation for all endpoints
  - Added health check endpoint for monitoring
  - Enhanced authentication token handling

- **Documentation**:
  - Added detailed frontend architecture documentation
  - Updated TypeScript interface definitions documentation
  - Added troubleshooting guides for common issues

- **Fitbit Integration**:
  - Enhanced Fitbit data export functionality
  - Added Dropbox integration for automated data backups
  - Improved token refresh mechanism

- **Bug Fixes**:
  - Fixed timezone handling in SMS scheduling
  - Resolved issues with duplicate message sending
  - Fixed TypeScript build errors
  - Addressed security vulnerabilities in dependencies

## Accessing the Application

After deployment, you can access:

- The web interface at: `http://yourdomain.com` (or `https://yourdomain.com` if SSL is configured)
- The API at: `http://yourdomain.com/api` (or `https://yourdomain.com/api`)
- API documentation at: `http://yourdomain.com/api/docs` (or `https://yourdomain.com/api/docs`)

## Default Login

- Username: `researcher`
- Password: `password`

**Important**: Change this default password immediately after first login.

## Updating the Application

To update the application:

```bash
# Pull the latest changes
cd /opt/pmi-fitbit-sms
git pull

# Update the frontend
cd /opt/pmi-fitbit-sms/frontend
npm install
npm run build
pm2 restart pmi-frontend

# Update the backend
cd /opt/pmi-fitbit-sms/backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart pmi-backend
```

## Troubleshooting

### Viewing Logs

```bash
# View frontend logs
pm2 logs pmi-frontend

# View backend logs
sudo journalctl -u pmi-backend.service -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Common Issues

#### Missing alembic.ini File

If you encounter an error like `No config file 'alembic.ini' found, or file has no '[alembic]' section`:

1. Check if the alembic.ini file exists in the backend directory:
```bash
ls -la backend/alembic.ini
```

2. If it's missing, create it:
```bash
cat > backend/alembic.ini << EOL
[alembic]
# Path to migration scripts
script_location = alembic

# Template used to generate migration files
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d%%(second).2d_%%(slug)s

# Prepend sys.path if present
prepend_sys_path = .

# Max length of characters to apply to the "slug" field
truncate_slug_length = 40

# Set to 'true' to run the environment during the 'revision' command
revision_environment = false

# Set to 'true' to allow .pyc and .pyo files without a source .py file to be detected
sourceless = false

# Version path separator
version_path_separator = os  # Use os.pathsep

# Output encoding used when revision files are written
output_encoding = utf-8

# The SQLAlchemy connection URL - this will be overridden by the DATABASE_URL env var
sqlalchemy.url = postgresql+asyncpg://postgres:your_secure_password@localhost:5432/app

[post_write_hooks]
# Post-write hooks allow you to execute commands after a revision file is created.
# Specify a command and a list of files as arguments

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOL
```

#### "Database Does Not Exist" Error

If you see `asyncpg.exceptions.InvalidCatalogNameError: database "app" does not exist`:

1. Connect to PostgreSQL and create the database:
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

2. Verify your database connection settings in your .env file:
```bash
cat .env | grep DATABASE_URL
```

#### Database Connection Issues

If the backend can't connect to the database:

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Restart PostgreSQL
sudo systemctl restart postgresql
```

##### DNS Resolution Errors

If you see errors like `socket.gaierror: [Errno -3] Temporary failure in name resolution`:

1. Check your DATABASE_URL in the `.env` file:
```bash
cat .env | grep DATABASE_URL
```

2. Try using direct IP addresses instead of hostnames:
```bash
# Edit the .env file
nano .env

# Change this:
# DATABASE_URL=postgresql+asyncpg://username:password@db:5432/dbname
# To this:
# DATABASE_URL=postgresql+asyncpg://username:password@127.0.0.1:5432/dbname
# Or use this format (without explicit port):
# DATABASE_URL=postgresql+asyncpg://postgres:password@localhost/app
```

3. Make sure your `/etc/hosts` file contains proper mappings:
```bash
# Check the hosts file
cat /etc/hosts

# Add mapping if needed
echo "127.0.0.1 db" | sudo tee -a /etc/hosts
```

4. Test DNS resolution directly:
```bash
# Extract hostname from DATABASE_URL (replace with your actual hostname)
nslookup your_db_hostname
ping -c 2 your_db_hostname
```

5. If using a remote database, ensure your firewall allows connections:
```bash
# Check if you can reach the database port (replace with actual IP and port)
telnet database_ip_address 5432
```

#### PM2 Issues

If you're having trouble with PM2:

```bash
# Check PM2 status
pm2 status

# View PM2 logs
pm2 logs pmi-frontend

# Restart PM2 process
pm2 restart pmi-frontend

# If PM2 seems corrupted, try resetting it
pm2 kill
pm2 start ecosystem.config.js
pm2 save
```

#### Uvicorn/Backend Service Issues

If the backend service is not running correctly:

```bash
# Check service status
sudo systemctl status pmi-backend

# View detailed logs
sudo journalctl -u pmi-backend.service -f

# Restart the service
sudo systemctl restart pmi-backend
```

#### Frontend API Connection Errors

If the frontend is showing 500 errors when connecting to the API:

1. Check that the API URL is set correctly in the frontend .env file:
```bash
# Navigate to the frontend directory
cd /opt/pmi-fitbit-sms/frontend

# Check or create a .env file
cat > .env << EOL
VITE_API_URL=http://localhost:8000/api
EOL
```

2. Make sure the backend can be reached directly:
```bash
# Test the backend API
curl http://localhost:8000/api/health
```

3. Check CORS settings in the backend (if you're accessing from a different domain):
```bash
# Edit the backend CORS settings
sudo nano /opt/pmi-fitbit-sms/backend/app/main.py
```

4. Check for API URL trailing slash inconsistencies:

The FastAPI backend may behave inconsistently with trailing slashes in URLs. If you're getting 307 redirects or 404 errors, ensure your frontend API client is using the correct URL format. Most API endpoints do not require trailing slashes:

```javascript
// Correct
axios.get('/api/participants')
axios.get('/api/sms/history')
axios.get('/api/sms/stats')

// Problematic (may cause redirects or errors)
axios.get('/api/participants/')
axios.get('/api/sms/history/')
axios.get('/api/sms/stats/')
```

To fix this in your frontend code:
```bash
# Check all API calls in your store files
grep -r "axios.get(" frontend/src/stores/
grep -r "apiClient.get(" frontend/src/stores/

# Remove trailing slashes from API endpoint URLs
```

5. Authentication token issues:

If you see 401 Unauthorized errors after previously successful authentication:

```
Error fetching participants: Request failed with status code 401
```

The JWT token may have expired. The centralized Axios client should automatically handle token refresh, but you may need to check:

```bash
# Examine the Axios client configuration
nano frontend/src/plugins/axios.ts
```

Make sure it includes proper interceptors for authentication:

```javascript
// Token refresh interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If unauthorized and not already tried refreshing
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Call token refresh endpoint or redirect to login
        const newToken = await refreshToken(); // implement this
        
        // Update token in storage
        localStorage.setItem('token', newToken);
        
        // Update the header in the original request
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
        
        // Retry the original request
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Redirect to login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
```

For a quick fix, log out and log back in to obtain a new token.

Look for the CORS configuration and make sure it allows your frontend domain.

#### TypeScript Build Errors

If you encounter TypeScript errors during the frontend build:

```
error TS2339: Property 'env' does not exist on type 'ImportMeta'.
error TS2339: Property 'pid' does not exist on type 'never'.
ERROR: "type-check" exited with 2.
```

You can fix these by:

1. Creating a proper TypeScript environment declaration file:
```bash
# Navigate to the frontend directory
cd frontend

# Create a vite-env.d.ts file in the src directory
cat > src/vite-env.d.ts << EOL
/// <reference types="vite/client" />

interface ImportMeta {
  readonly env: {
    readonly VITE_API_URL: string;
    readonly [key: string]: string;
  };
}
EOL
```

2. Temporarily bypass TypeScript checks during build:
```bash
# Modify the package.json build script
sed -i 's/"build": "vue-tsc --noEmit && vite build"/"build": "vite build"/' package.json
```

#### Alembic "No module named 'app'" Error

If you encounter `ModuleNotFoundError: No module named 'app'` when running Alembic commands:

1. Edit the `alembic/env.py` file:
```bash
nano backend/alembic/env.py
```

2. Add the following code near the top of the file, after the imports:
```python
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

3. Save the file and try again.

Alternative solution: Install your app as a development package:
```bash
cd backend
pip install -e .
```

This may require creating a simple setup.py file if you don't have one:
```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="app",
    version="0.1",
    packages=find_packages(),
)
```

#### SSL Certificate Issues

If you're having issues with SSL:

```bash
# Verify certificate paths
sudo ls -la /etc/letsencrypt/live/yourdomain.com/

# Check nginx configuration
sudo nginx -t

# Test certificate renewal
sudo certbot renew --dry-run
```

## Security Considerations

1. **Keep your server updated**: Regularly update your server with security patches
2. **Secure environment variables**: Never commit your `.env` file to version control
3. **Regular backups**: Ensure your database backup strategy is working
4. **SSL/TLS**: Always use SSL/TLS in production environments
5. **Firewall**: Configure a firewall to restrict access to only necessary ports

## CI/CD Pipeline

This project includes a GitHub Actions CI/CD pipeline for automated testing and deployment to your PM2 and Uvicorn environment.

### Pipeline Overview

The CI/CD pipeline consists of two main jobs:

1. **Test**: Runs automated tests for both the backend and frontend
2. **Deploy**: Deploys the application to your production server, setting up PM2 and Uvicorn services

### Setting Up Required Secrets

To use the CI/CD pipeline, you need to add the following secrets to your GitHub repository:

1. Go to your GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Add the following secrets:

#### Server Deployment Credentials
- `SERVER_HOST`: Your server's IP address or hostname
- `SERVER_USER`: SSH username for your server
- `SSH_PRIVATE_KEY`: The private SSH key to access your server

#### Application Secrets
- `SECRET_KEY`: A secure random key for your application
- `DB_PASSWORD`: Your database password

### How to Use the Pipeline

The pipeline triggers automatically when:
- You push to the `main` or `master` branch
- A pull request is created targeting the `main` or `master` branch

You can also trigger the pipeline manually:
1. Go to your GitHub repository
2. Navigate to Actions > CI/CD Pipeline
3. Click "Run workflow" and select the branch to run it on

### First-Time Deployment Setup

Before the first automatic deployment:

1. SSH into your server manually
2. Create the deployment directory: `mkdir -p /opt/pmi-fitbit-sms`
3. Clone your repository: `git clone https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git /opt/pmi-fitbit-sms`
4. Set up initial configuration: `cd /opt/pmi-fitbit-sms && cp .env.example .env`
5. Edit the `.env` file with your actual values: `nano .env`
6. Install PM2 globally: `sudo npm install -g pm2`
7. Set up PostgreSQL: `sudo apt install -y postgresql postgresql-contrib`
8. Install Python dependencies: `sudo apt install -y python3 python3-pip python3-venv`
9. Install nginx: `sudo apt install -y nginx`

After these steps, the CI/CD pipeline will handle future deployments automatically.
