# Bouncer

A comprehensive access control system for Python that brings C++ style access levels to Python classes.

## Overview

Bouncer provides fine-grained control over method and property access using decorators, enabling developers to enforce access restrictions similar to those found in languages like C++ and Java.

**Key Features:**
- C++ style access control (`@private`, `@protected`, `@public`)
- Friend class relationships (`@friend`)
- Inheritance access control with proper semantics
- Property access control for getters and setters
- Runtime enforcement management
- Comprehensive error handling

## Installation

Install from PyPI:
```bash
pip install bouncer-access-control
```

Install from source:
```bash
git clone https://github.com/Ma1achy/Bouncer.git
cd Bouncer
pip install -e .
```

## Quick Start

```python
from bouncer import private, protected, public, friend

class BankAccount:
    def __init__(self, balance=0):
        self._balance = balance
    
    @private
    def _validate_transaction(self, amount):
        return amount > 0 and amount <= self._balance
    
    @protected
    def _log_transaction(self, amount):
        print(f"Transaction: ${amount}")
    
    @public
    def withdraw(self, amount):
        if self._validate_transaction(amount):
            self._balance -= amount
            self._log_transaction(amount)
            return True
        return False
```

## Access Control Decorators

### @private
Methods marked as private are only accessible within the same class.

```python
class SecureClass:
    @private
    def _internal_method(self):
        return "secret data"
    
    def public_method(self):
        # This works - same class
        return self._internal_method()

obj = SecureClass()
obj.public_method()  # Works
obj._internal_method()  # Raises PermissionDeniedError
```

### @protected
Methods marked as protected are accessible within the same class and its subclasses.

```python
class BaseClass:
    @protected
    def _protected_method(self):
        return "protected data"

class DerivedClass(BaseClass):
    def access_protected(self):
        # This works - derived class can access protected members
        return self._protected_method()

obj = DerivedClass()
obj.access_protected()  # Works
obj._protected_method()  # Raises PermissionDeniedError (external access)
```

### @public
Methods marked as public are accessible from anywhere. This is the default Python behavior but can be used for explicit documentation.

```python
class PublicClass:
    @public
    def public_method(self):
        return "accessible everywhere"

obj = PublicClass()
obj.public_method()  # Works from anywhere
```

## Friend Classes

Friend classes can access private and protected members of the target class.

```python
class Database:
    def __init__(self):
        self._connection = "db_connection"
    
    @private
    def _execute_query(self, query):
        return f"Executing: {query}"

@friend(Database)
class DatabaseManager:
    def backup_database(self, db):
        # Friend class can access private methods
        return db._execute_query("BACKUP DATABASE")

@friend(Database)
class DatabaseAuditor:
    def audit_connection(self, db):
        # Multiple classes can be friends
        return db._connection

# Usage
db = Database()
manager = DatabaseManager()
auditor = DatabaseAuditor()

manager.backup_database(db)  # Works - friend access
auditor.audit_connection(db)  # Works - friend access

# Regular class cannot access private members
class RegularClass:
    def try_access(self, db):
        return db._execute_query("SELECT *")  # Raises PermissionDeniedError
```

## Friend Functions

Friend functions are standalone functions that can access private and protected members of a class.

```python
class SecureVault:
    def __init__(self):
        self._treasure = "classified data"
    
    @private
    def _get_secret(self):
        return self._treasure
    
    @protected
    def _log_access(self, accessor):
        print(f"Access by: {accessor}")

@friend(SecureVault)
def trusted_backup(vault):
    """Friend function that can access private members"""
    vault._log_access("backup_system")
    return f"Backing up: {vault._get_secret()}"

@friend(SecureVault)
def security_audit(vault):
    """Another friend function"""
    return f"Audit found: {vault._get_secret()}"

def unauthorized_access(vault):
    """Regular function without friend access"""
    return vault._get_secret()  # Raises PermissionDeniedError

# Usage
vault = SecureVault()

# Friend functions work
backup_data = trusted_backup(vault)  # Works
audit_result = security_audit(vault)  # Works

# Regular function is blocked
try:
    unauthorized_access(vault)
except PermissionDeniedError:
    print("Access denied to unauthorized function")
```

### Mixed Friend Relationships

You can have both friend classes and friend functions for the same target class:

```python
class DataStore:
    @private
    def _internal_data(self):
        return "sensitive data"

@friend(DataStore)
class DataManager:
    def manage_data(self, store):
        return f"Managing: {store._internal_data()}"

@friend(DataStore)
def backup_data(store):
    return f"Backup: {store._internal_data()}"

# Both friend class and friend function can access private members
store = DataStore()
manager = DataManager()

manager.manage_data(store)  # Works
backup_data(store)  # Works
```

## Property Access Control

Control access to property getters and setters independently.

```python
class Employee:
    def __init__(self, name, salary):
        self._name = name
        self._salary = salary
    
    @protected
    @property
    def salary(self):
        """Protected getter - accessible in derived classes"""
        return self._salary
    
    @salary.setter
    @private
    def salary(self, value):
        """Private setter - only accessible within Employee class"""
        if value > 0:
            self._salary = value
    
    def give_raise(self, amount):
        # Private setter accessible within same class
        self.salary = self._salary + amount

class Manager(Employee):
    def review_salary(self):
        # Can read salary (protected getter)
        return f"Current salary: {self.salary}"
    
    def try_set_salary(self, amount):
        # Cannot set salary (private setter)
        self.salary = amount  # Raises PermissionDeniedError
```

## Inheritance Access Control

Bouncer follows C++ access semantics for inheritance.

```python
class Base:
    @private
    def _base_private(self):
        return "base private"
    
    @protected
    def _base_protected(self):
        return "base protected"
    
    @public
    def base_public(self):
        return "base public"

class Derived(Base):
    def test_access(self):
        # Can access protected members from base class
        protected_data = self._base_protected()  # Works
        
        # Cannot access private members from base class
        # private_data = self._base_private()  # Raises PermissionDeniedError
        
        # Can always access public members
        public_data = self.base_public()  # Works
        
        return protected_data, public_data
```

## System Management

Control access enforcement at runtime.

```python
from bouncer import enable_enforcement, disable_enforcement, get_metrics, reset_system

# Disable enforcement (useful for testing)
disable_enforcement()

# Now access control is not enforced
obj._private_method()  # Would normally fail, but now allowed

# Re-enable enforcement
enable_enforcement()

# Get system metrics
metrics = get_metrics()
print(f"Access checks performed: {metrics.get('total_access_checks', 0)}")

# Reset the system
reset_system()
```

## Error Handling

Bouncer provides specific exception types for different access control violations.

```python
from bouncer import (
    PermissionDeniedError,
    DecoratorConflictError,
    InvalidDecoratorUsageError,
    FriendshipError
)

class SecureClass:
    @private
    def secret_method(self):
        return "secret"

try:
    obj = SecureClass()
    obj.secret_method()
except PermissionDeniedError as e:
    print(f"Access denied: {e}")

# Decorator conflicts are detected
try:
    class ConflictClass:
        @private
        @public  # This creates a conflict
        def conflicted_method(self):
            pass
except DecoratorConflictError as e:
    print(f"Decorator conflict: {e}")
```

## Requirements

- Python 3.8+
- No external dependencies for core functionality

## Development

For development setup:

```bash
git clone https://github.com/Ma1achy/Bouncer.git
cd Bouncer
pip install -e .[dev]
```

Run tests:
```bash
pytest
```

## License

MIT License - see LICENSE file for details.
