# Fitness Club Membership Service

## 📋 Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Testing](#testing)
- [Development Tools](#development-tools)
- [Docker](#docker)

## ✨ Features

- 🚀 **uv** - Fast Python package manager
- 🎨 **ruff** - Ultra-fast linter and code formatter
- 🔍 **pre-commit** - Automatic code checks before commits
- 🧪 **pytest** - Modern testing framework
- 📚 **DRF Spectacular** - Automatic OpenAPI documentation generation
- 🔒 **Django REST Framework** - Powerful API toolkit
- 🔐 **JWT Authentication** - Secure token-based authentication
- 🐳 **Docker Compose** - Containerized PostgreSQL and Redis

## 📦 Requirements

- Python 3.11+
- PostgreSQL 14+ (or Docker)
- uv (package manager)

### Installing uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

## 🚀 Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd django-project
```

### 2. Create Virtual Environment with uv

```bash
# Create venv
uv venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install all dependencies including dev
uv pip install -e ".[dev]"

# Or use Makefile
make dev-install
```

### 4. Database Setup

#### Option A: Using Docker

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Check status
docker-compose ps
```

#### Option B: Local PostgreSQL

Install PostgreSQL and create database:

```sql
CREATE DATABASE django_db;
CREATE USER django_user WITH PASSWORD 'django_password';
ALTER ROLE django_user SET client_encoding TO 'utf8';
ALTER ROLE django_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE django_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE django_db TO django_user;
```

### 5. Environment Variables Setup

```bash
# Copy .env.sample
cp .env.sample .env

# Edit .env (add your values)
nano .env
```

Example `.env`:

```env
SECRET_KEY=your-super-secret-key-change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql
DB_NAME=django_db
DB_USER=django_user
DB_PASSWORD=django_password
DB_HOST=localhost
DB_PORT=5432
```

### 6. Database Migrations

```bash
cd src
python manage.py makemigrations
python manage.py migrate

# Or via Makefile
make migrate
```

### 7. Create Superuser

```bash
cd src
python manage.py createsuperuser
```

### 8. Install pre-commit hooks

```bash
pre-commit install
```

## 📁 Project Structure

```
django-project/
├── src/
│   ├── apps/                    # Django apps
│   │   ├── __init__.py
│   │   └── example_app/         # Example app
│   ├── config/                  # Project configuration
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── migrations/              # Database migrations
│   └── manage.py
├── tests/                       # Tests
│   ├── conftest.py             # pytest configuration
│   ├── unit/                   # Unit tests
│   │   └── test_example.py
│   └── integration/            # Integration tests
│       └── test_api.py
├── .env.sample                 # Environment variables example
├── .gitignore
├── .pre-commit-config.yaml     # pre-commit configuration
├── docker-compose.yml          # Docker Compose configuration
├── Makefile                    # Command automation
├── pyproject.toml              # Project and tools configuration
├── README.md
└── uv.lock                     # Dependencies lock file
```

## 🎯 Usage

### Run Development Server

```bash
# Via manage.py
cd src
python manage.py runserver

# Or via Makefile
make run
```

Server will be available at: http://localhost:8000

### Admin Panel

```
URL: http://localhost:8000/admin/
Login: your superuser
Password: your password
```

### API Documentation

After starting the server, documentation is available:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### JWT Authentication

The project uses JWT (JSON Web Tokens) for authentication. See [JWT_AUTHENTICATION.md](JWT_AUTHENTICATION.md) for detailed documentation.

#### Quick Start

1. **Obtain Token:**
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

2. **Use Token in Requests:**
```bash
curl http://localhost:8000/api/v1/books/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

3. **Refresh Token:**
```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."}'
```

**JWT Endpoints:**
- `POST /api/token/` - Obtain access and refresh tokens
- `POST /api/token/refresh/` - Refresh access token
- `POST /api/token/verify/` - Verify token validity

**Configuration** (`.env`):
```env
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
JWT_ROTATE_REFRESH_TOKENS=True
JWT_BLACKLIST_AFTER_ROTATION=True
```


### Django Shell

```bash
cd src
python manage.py shell

# Or with extended shell (if shell_plus is installed)
make shell
```

## 🧪 Testing

### Run All Tests

```bash
pytest

# Or via Makefile
make test
```

### Run Specific Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Specific file
pytest tests/unit/test_example.py

# Specific test
pytest tests/unit/test_example.py::TestExample::test_example
```

### Tests with Coverage

```bash
# Run with coverage
pytest --cov

# Generate HTML report
pytest --cov --cov-report=html

# Or via Makefile
make test-cov
```

HTML report will be available at `htmlcov/index.html`

### pytest Markers

```bash
# Only unit tests
pytest -m unit

# Only integration tests
pytest -m integration

# Without slow tests
pytest -m "not slow"
```

### Parallel Test Execution

```bash
# Auto-detect number of processes
pytest -n auto

# Specific number of processes
pytest -n 4
```

## 🛠️ Development Tools

### Ruff (Linter & Formatter)

#### Code Checking

```bash
# Check entire project
ruff check .

# Check specific file
ruff check src/apps/example_app/models.py

# Or via Makefile
make lint
```

#### Code Formatting

```bash
# Format entire project
ruff format .

# Format specific file
ruff format src/apps/example_app/models.py

# Auto-fix errors
ruff check --fix .

# Or via Makefile
make format
```

#### Ruff Configuration

Configuration is in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "DJ"]
ignore = ["E501", "B008", "DJ001"]
```

### Pre-commit

Pre-commit runs automatically before each commit.

### What Pre-commit Does

Pre-commit runs the following checks automatically:

1. **Code Quality Checks** (from pre-commit-hooks):
   - Remove trailing whitespace
   - Fix end of file
   - Check YAML syntax
   - Check for large files (>1MB)
   - Check JSON and TOML syntax
   - Check for merge conflicts
   - Check for debug statements
   - Normalize line endings

2. **Ruff Linter and Formatter**:
   - Check code style (PEP 8)
   - Find potential bugs
   - Sort imports
   - Format code automatically
   - Fix simple issues

3. **Type Checking** (mypy):
   - Check type hints
   - Find type-related errors

4. **Django Checks**:
   - Run `python manage.py check`
   - Check for missing migrations

### Installation

Pre-commit is installed automatically when you run:

```bash
make dev-install
```

Or manually:

```bash
uv pip install -e ".[dev]"
pre-commit install
```

**Important**: Pre-commit requires Git to be initialized:

```bash
# If you get an error about Git not being initialized:
git init
git add .
pre-commit install
```

### Manual Run

Run pre-commit manually without committing:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run ruff --all-files
pre-commit run ruff-format --all-files
```

### Pre-commit Workflow

```bash
# 1. Make changes to your code
nano src/apps/myapp/models.py

# 2. Stage changes
git add .

# 3. Try to commit (pre-commit runs automatically)
git commit -m "Add new model"

# Pre-commit output:
# Trim Trailing Whitespace...........................Passed
# Fix End of Files....................................Passed
# Check Yaml..........................................Passed
# Ruff................................................Failed  # ← Code needs fixing
# - hook id: ruff
# - exit code: 1
# 
# Found 3 errors:
# - apps/myapp/models.py:10:5: F401 'datetime' imported but unused
# - apps/myapp/models.py:15:80: E501 line too long (95 > 100)

# 4. Pre-commit may auto-fix some issues
# Check what was changed:
git diff

# 5. Stage auto-fixed files
git add .

# 6. Commit again
git commit -m "Add new model"

# Now it passes:
# Trim Trailing Whitespace...........................Passed
# Ruff................................................Passed
# ✓ All checks passed!
```

### Skipping Pre-commit (Not Recommended)

If you need to commit without running pre-commit (emergency only):

```bash
git commit -m "Emergency fix" --no-verify
```

**Warning**: Only use `--no-verify` in emergencies. Skipping checks can introduce bugs and style inconsistencies.

### Update Hooks

Update to the latest versions of pre-commit hooks:

```bash
pre-commit autoupdate
```

This updates versions in `.pre-commit-config.yaml`.

### Configuration

Pre-commit is configured in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      # ... more hooks

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.15
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: django-check
        name: Django System Check
        entry: python src/manage.py check
        language: system
        pass_filenames: false
```

### Customizing Pre-commit

#### Disable Specific Hooks

Edit `.pre-commit-config.yaml` and comment out hooks:

```yaml
hooks:
  - id: trailing-whitespace
  # - id: check-yaml  # Disabled
  - id: end-of-file-fixer
```

#### Add Custom Hooks

Add your own checks:

```yaml
  - repo: local
    hooks:
      - id: check-env-file
        name: Check .env file exists
        entry: bash -c 'test -f .env || (echo ".env file missing!" && exit 1)'
        language: system
        pass_filenames: false
      
      - id: run-security-check
        name: Security Check
        entry: bandit -r src/apps/
        language: system
        pass_filenames: false
```

#### Skip Hooks for Specific Files

```yaml
  - id: ruff
    exclude: ^migrations/
```

### Troubleshooting

#### "git failed. Is it installed?"

**Problem**: Pre-commit requires Git
**Solution**:
```bash
git init
git add .
pre-commit install
```

#### "hook failed" errors

**Problem**: Code doesn't meet standards
**Solution**: 
1. Review the error message
2. Fix the code manually
3. Or let pre-commit auto-fix with `--fix`
4. Stage changes: `git add .`
5. Try commit again

#### Hooks are slow

**Problem**: Pre-commit takes too long
**Solution**: 
- Run only on changed files (default)
- Skip mypy for faster commits:
  ```bash
  SKIP=mypy git commit -m "Quick fix"
  ```
- Or configure to skip in `.pre-commit-config.yaml`

#### Want to commit anyway

**Solution**: Use `--no-verify` (emergency only):
```bash
git commit -m "Emergency" --no-verify
```

### Best Practices

1. **Let pre-commit auto-fix**: Don't fight it, let it format your code
2. **Run manually before committing**: `pre-commit run --all-files`
3. **Update regularly**: `pre-commit autoupdate` monthly
4. **Don't skip**: Using `--no-verify` should be rare
5. **Fix root causes**: If a check always fails, fix your code or update config
6. **Review auto-fixes**: Check `git diff` after pre-commit runs

This ensures code quality even if someone bypasses local pre-commit hooks.

### Common Pre-commit Hooks

| Hook | Purpose | Auto-fix |
|------|---------|----------|
| `trailing-whitespace` | Remove trailing spaces | ✅ Yes |
| `end-of-file-fixer` | Ensure newline at EOF | ✅ Yes |
| `check-yaml` | Validate YAML syntax | ❌ No |
| `check-json` | Validate JSON syntax | ❌ No |
| `ruff` | Lint Python code | ✅ Partial |
| `ruff-format` | Format Python code | ✅ Yes |
| `mypy` | Type checking | ❌ No |
| `django-check` | Django system check | ❌ No |

#### Manual Run

```bash
# Run for all files
pre-commit run --all-files

# Run for staged files
pre-commit run
```

#### Update Hooks

```bash
pre-commit autoupdate
```

#### Skip pre-commit (not recommended)

```bash
git commit -m "message" --no-verify
```

### Django Management Commands

#### Migrations

```bash
cd src

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# View migrations
python manage.py showmigrations

# Rollback migration
python manage.py migrate app_name migration_name
```

#### Custom Migration Modules

If you need to use custom migration directories (e.g., for different environments or splitting migrations), configure `MIGRATION_MODULES` in `config/settings.py`:

```python
# config/settings.py

MIGRATION_MODULES = {
    # Register custom migration modules here
    # Format: "app_name": "path.to.custom.migrations"
    
    # Example 1: Custom migrations directory
    "myapp": "apps.myapp.migrations_custom",
    
    # Example 2: Separate migrations for different environments
    "orders": "apps.orders.migrations_production",
    
    # Example 3: Disable migrations for specific app (useful for testing)
    "third_party_app": None,
}
```

**Use Cases:**

1. **Custom Migration Location:**
   ```python
   MIGRATION_MODULES = {
       "books": "apps.books.migrations_custom",
   }
   ```
   Structure:
   ```
   apps/books/
   ├── migrations_custom/
   │   ├── __init__.py
   │   ├── 0001_initial.py
   │   └── 0002_add_isbn.py
   ```

2. **Environment-Specific Migrations:**
   ```python
   import os
   
   if os.getenv("ENVIRONMENT") == "production":
       MIGRATION_MODULES = {
           "myapp": "apps.myapp.migrations_production",
       }
   else:
       MIGRATION_MODULES = {
           "myapp": "apps.myapp.migrations_dev",
       }
   ```

3. **Disable Migrations (Testing):**
   ```python
   # Useful for testing with third-party apps
   if TESTING:
       MIGRATION_MODULES = {
           "third_party_app": None,
       }
   ```

**Creating Custom Migration Directory:**

```bash
# 1. Create custom migrations directory
mkdir -p src/apps/myapp/migrations_custom
touch src/apps/myapp/migrations_custom/__init__.py

# 2. Configure in settings.py
# MIGRATION_MODULES = {"myapp": "apps.myapp.migrations_custom"}

# 3. Create migrations
cd src
python manage.py makemigrations myapp
```

#### Collect Static Files

```bash
cd src
python manage.py collectstatic
```

#### Create App

```bash
cd src
python manage.py startapp new_app apps/new_app
```

#### Django Check

```bash
cd src
python manage.py check

# Or via Makefile
make check
```

## 🐳 Docker

### Start Services

```bash
# Start in background
docker-compose up -d

# Start with logs
docker-compose up

# Stop
docker-compose down

# Stop with volume removal
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f db
docker-compose logs -f redis
```

### Execute Commands in Container

```bash
# PostgreSQL
docker-compose exec db psql -U django_user -d django_db

# Redis
docker-compose exec redis redis-cli
```

## 📝 Makefile Commands

The project includes a Makefile for automating routine tasks:

```bash
make help          # Show all available commands
make install       # Install production dependencies
make dev-install   # Install dev dependencies + pre-commit
make migrate       # Run migrations
make test          # Run tests
make test-cov      # Tests with coverage
make lint          # Check code
make format        # Format code
make check         # Django system check
make clean         # Clean temporary files
make run           # Start dev server
make shell         # Open Django shell
```

### Detailed Makefile Usage

#### Installation Commands

```bash
# Install only production dependencies
make install

# Install development dependencies and setup pre-commit
make dev-install
```

This is equivalent to:
```bash
uv pip install -e .                    # make install
uv pip install -e ".[dev]"             # make dev-install
pre-commit install                      # make dev-install
```

#### Development Commands

```bash
# Run development server (localhost:8000)
make run

# Open Django shell with IPython
make shell

# Run database migrations
make migrate
```

Equivalent to:
```bash
cd src && python manage.py runserver   # make run
cd src && python manage.py shell       # make shell
cd src && python manage.py makemigrations && python manage.py migrate  # make migrate
```

#### Code Quality Commands

```bash
# Check code with ruff (find issues)
make lint

# Format code with ruff (fix issues)
make format

# Run Django system checks
make check
```

Equivalent to:
```bash
ruff check .                           # make lint
ruff format . && ruff check --fix .    # make format
cd src && python manage.py check && python manage.py makemigrations --check --dry-run  # make check
```

#### Testing Commands

```bash
# Run all tests
make test

# Run tests with coverage report
make test-cov
```

Equivalent to:
```bash
pytest                                  # make test
pytest --cov --cov-report=html         # make test-cov
```

#### Cleanup Commands

```bash
# Clean temporary files and caches
make clean
```

This removes:
- `__pycache__` directories
- `.pyc` and `.pyo` files
- `.pytest_cache`
- Coverage reports
- Build artifacts


Usage:
```bash
make backup
make restore
make create-app
make deploy
```

## 🔍 Pre-commit Hooks

Pre-commit automatically runs code quality checks before each commit. This ensures that only properly formatted and linted code enters the repository.

## 🔧 IDE Configuration

### PyCharm

1. Open Settings → Project → Python Interpreter
2. Select `.venv/bin/python`
3. Tools → External Tools → Add Ruff
4. Settings → Tools → Python Integrated Tools → Testing → pytest

## 🚀 Creating a New App

```bash
# 1. Create app
cd src
python manage.py startapp my_app apps/my_app

# 2. Add to INSTALLED_APPS (config/settings.py)
INSTALLED_APPS = [
    ...
    "apps.my_app",
]

# 3. Create structure
cd apps/my_app
touch urls.py serializers.py tests.py

# 4. Add URLs (config/urls.py)
urlpatterns = [
    ...
    path("api/v1/my-app/", include("apps.my_app.urls")),
]
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)
- [pre-commit Documentation](https://pre-commit.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.
