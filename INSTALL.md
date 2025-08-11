# Installation and Development Guide

## Quick Installation

### From PyPI (when published)
```bash
pip install bouncer-access-control
```

### From Source (Current)
```bash
git clone https://github.com/Ma1achy/Bouncer.git
cd Bouncer
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/Ma1achy/Bouncer.git
cd Bouncer
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
pytest --cov=bouncer --cov-report=html

# Format code
black bouncer tests

# Lint code
flake8 bouncer tests

# Type check
mypy bouncer

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
   pip install bouncer-access-control
   ```

## Project Structure

```
Bouncer/
├── bouncer/                 # Main package
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
- `bouncer/__init__.py` (__version__)

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
