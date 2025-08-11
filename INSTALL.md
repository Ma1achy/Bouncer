# Installation and Development Guide

## Quick Installation

### From PyPI
```bash
pip install pylimen
```

### From Source (Current)
```bash
git clone https://github.com/Ma1achy/Limen.git
cd Limen
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/Ma1achy/Limen.git
cd Limen
pip install -e .[dev]
```

## Development Workflow

### Using the dev.py helper script:
```bash
# Install in development mode with all dev dependencies
python dev.py install-dev

# Run tests
python dev.py test

# Run tests with coverage
python dev.py test-cov

# Format code
python dev.py format

# Run linting
python dev.py lint

# Run type checking
python dev.py type-check

# Run all quality checks
python dev.py all-checks

# Build the package
python dev.py build

# Clean build artifacts
python dev.py clean
```

### Manual commands:
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .

# Run tests
pytest

# Run tests with coverage
pytest --cov=limen --cov-report=html

# Format code
black limen tests

# Lint code
flake8 limen tests

# Type check
mypy limen

# Build package
python -m build

# Check distribution
twine check dist/*
```

## Publishing to PyPI

1. **Prepare for release:**
   ```bash
   python dev.py all-checks
   python dev.py clean
   python dev.py build
   ```

2. **Test upload to TestPyPI:**
   ```bash
   twine upload --repository testpypi dist/*
   ```

3. **Upload to PyPI:**
   ```bash
   twine upload dist/*
   ```

4. **Test installation:**
   ```bash
   pip install pylimen
   ```

## Project Structure

```
Limen/
├── limen/                   # Main package
│   ├── __init__.py         # Public API
│   ├── access/             # Access control logic
│   ├── core/               # Core types and protocols
│   ├── decorators/         # Decorator implementations
│   ├── descriptors/        # Property descriptors
│   ├── exceptions/         # Custom exceptions
│   ├── inspection/         # Stack inspection utilities
│   ├── system/             # System management
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── pyproject.toml          # Package configuration
├── setup.py               # Backwards compatibility
├── MANIFEST.in            # Package data
├── requirements-dev.txt   # Development dependencies
├── dev.py                 # Development helper script
├── README.md              # Main documentation
├── LICENSE                # MIT license
└── .gitignore             # Git ignore rules
```

## Version Management

Update version in:
- `pyproject.toml` (project.version)
- `limen/__init__.py` (__version__)

## Testing

The test suite includes:
- C++ semantics validation
- Access control functionality
- Inheritance behavior
- Friend relationships
- Edge cases and boundary conditions
- Performance tests

Run with: `python dev.py test` or `pytest`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `python dev.py all-checks`
5. Submit a pull request

All contributions must:
- Pass all tests
- Follow code formatting (black)
- Pass linting (flake8)
- Include type hints (mypy)
- Include appropriate tests
