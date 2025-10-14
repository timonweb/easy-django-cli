# Easy Django CLI

A modern CLI tool that simplifies Django development by replacing `python manage.py` and `django-admin` commands with simpler `django` or `dj` commands.

[![CI](https://github.com/timonweb/easy-django-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/timonweb/easy-django-cli/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/easy-django-cli.svg)](https://badge.fury.io/py/easy-django-cli)
[![Python Versions](https://img.shields.io/pypi/pyversions/easy-django-cli.svg)](https://pypi.org/project/easy-django-cli/)
[![Django Versions](https://img.shields.io/badge/django-4.2%20%7C%205.0%20%7C%205.1%20%7C%205.2%20%7C%206.0-blue.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Simpler commands**: Use `django` or `dj` instead of `python manage.py`
- **Smart project detection**: Automatically finds your `manage.py` file
- **Drop-in replacement**: Works with all Django management commands
- **Zero configuration**: Just install and use
- **Fast**: No overhead compared to traditional Django commands

## Installation

### Using uv (recommended)

```bash
uv pip install easy-django-cli
```

### Using pip

```bash
pip install easy-django-cli
```

## Usage

After installation, you can use `django` or `dj` commands instead of `python manage.py`:

### Before (traditional Django)

```bash
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

### After (with easy-django-cli)

```bash
django runserver
django makemigrations
django migrate
django createsuperuser
django shell
```

Or use the even shorter `dj` alias:

```bash
dj runserver
dj makemigrations
dj migrate
dj createsuperuser
dj shell
```

## How It Works

`easy-django-cli` automatically:

1. Searches for `manage.py` in the current directory and up to 5 parent directories
2. If found, executes commands through your project's `manage.py`
3. If not found, falls back to `django-admin` for project creation and other admin commands

This means you can run Django commands from any subdirectory of your project!

## Examples

### Start the development server

```bash
django runserver
# or
dj runserver 0.0.0.0:8000
```

### Create and apply migrations

```bash
django makemigrations
django migrate
```

### Create a new Django project

```bash
django startproject myproject
```

### Create a new app

```bash
django startapp myapp
```

### Run tests

```bash
django test
```

### Open Django shell

```bash
django shell
# or use IPython/bpython if installed
django shell -i ipython
```

### Collect static files

```bash
django collectstatic --noinput
```

## Development

### Setting up development environment

1. Clone the repository:

```bash
git clone https://github.com/timonweb/easy-django-cli.git
cd easy-django-cli
```

2. Install dependencies using uv:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

3. Install pre-commit hooks:

```bash
pre-commit install
```

### Running tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=easy_django_cli --cov-report=html

# Run specific test file
pytest tests/test_cli.py

# Run with tox (multiple Python/Django versions)
tox
```

### Code quality

```bash
# Run linting
ruff check easy_django_cli tests

# Run formatting
ruff format easy_django_cli tests

# Run type checking
mypy easy_django_cli

# Run all checks with tox
tox -e lint,type
```

## Requirements

- Python 3.10 or higher
- Django 4.2 or higher

## Compatibility

This package is tested with:

- Python: 3.10, 3.11, 3.12, 3.13, 3.14
- Django: 4.2, 5.0, 5.1, 5.2, 6.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Tim Kamanin - [A Freelance Django and Wagtail Developer](https://timonweb.com)

## Links

- **Homepage**: https://github.com/timonweb/easy-django-cli
- **Documentation**: https://github.com/timonweb/easy-django-cli#readme
- **Repository**: https://github.com/timonweb/easy-django-cli
- **Issues**: https://github.com/timonweb/easy-django-cli/issues
- **PyPI**: https://pypi.org/project/easy-django-cli/

## Changelog

### 0.1.0 (2025)

- Initial release
- Basic functionality: `django` and `dj` commands
- Automatic `manage.py` detection
- Full compatibility with Django management commands
- Comprehensive test suite
- CI/CD with GitHub Actions
