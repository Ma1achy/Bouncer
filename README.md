# Bouncer

Bouncer is an access control system that provides fine-grained security and encapsulation for Python classes. It implements true C++ semantics including public, protected, and private access levels, friend relationships, and inheritance-based access control with automatic detection of access levels based on method naming conventions.

### Key Features

- **C++ Style Access Control**: Complete implementation of `@private`, `@protected`, `@public` decorators
- **Implicit Access Control**: Automatic access level detection based on naming conventions (_, __, normal names)
- **Friend Relationships**: Support for `@friend` classes, methods, functions, and staticmethods/classmethods
- **Advanced Inheritance**: True C++ style inheritance with public, protected, and private inheritance patterns
- **Dual-Layer Security**: Access modifiers on friend methods for fine-grained permission control
- **Descriptor Support**: Full compatibility with `@staticmethod`, `@classmethod`, `@property` decorators
- **Multiple Inheritance**: Support for complex inheritance hierarchies with proper access control
- **Runtime Management**: Dynamic enable/disable enforcement, metrics, and debugging capabilities
- **Error Handling**: Specific exception types for different access control violations
- **Zero Dependencies**: Pure Python implementation with no external requirements

## Installation

### From PyPI (Recommended)
```bash
pip install bouncer-access-control
```

### From Source
```bash
git clone https://github.com/Ma1achy/Bouncer.git
cd Bouncer
pip install -e .
```

## Access Control Decorators

Bouncer provides three main access control decorators that define method visibility and accessibility.

### @private - Same Class Only

Private methods are only accessible within the same class where they're defined.

```python
from bouncer import private, protected, public, friend

class Base:
    @private
    def _private_method(self):
        return "private"
    
    @public
    def public_method(self):
        # Works - same class access
        return self._private_method()

obj = Base()
obj.public_method()  # Works - public access
# obj._private_method()  # PermissionError - private access
```

### @protected - Inheritance Hierarchy

Protected methods are accessible within the same class and its subclasses.

```python
class Base:
    @protected
    def _protected_method(self):
        return "protected"

class Derived(Base):
    def foo(self):
        # Works - derived class can access protected members
        return self._protected_method()

obj = Derived()
obj.foo()  # Works - calls protected method internally
# obj._protected_method()  # PermissionError - external access blocked
```

### @public - Universal Access

Public methods are accessible from anywhere (default Python behavior, useful for explicit documentation).

```python
class Base:
    @public
    def get_data(self):
        return "data"
    
    @public
    def check_status(self):
        return "ok"

obj = Base()
obj.get_data()      # Works from anywhere
obj.check_status()  # Works from anywhere
```

## Implicit Access Control

Bouncer provides automatic access level detection based on Python naming conventions. When inheritance decorators are applied, methods are automatically wrapped with appropriate access control based on their names.

### Naming Convention Rules

- **Normal names** (e.g., `method_name`) → `@public`
- **Single underscore prefix** (e.g., `_method_name`) → `@protected`
- **Double underscore prefix** (e.g., `__method_name`) → `@private`

### Automatic Application with Inheritance Decorators

When you use inheritance decorators like `@protected(BaseClass)`, implicit access control is automatically applied to both the base class and derived class:

```python
class Base:
    def public_method(self):               # Automatically treated as @public
        return "public"
    
    def _protected_method(self):           # Automatically treated as @protected
        return "protected"
    
    def __private_method(self):            # Automatically treated as @private
        return "private"
    
    @public                                # Explicit decorator overrides implicit
    def _explicitly_public(self):
        return "explicit public"

# Inheritance decorator applies implicit access control to Base
@protected(Base)
class Derived(Base):
    def test_access(self):
        # Can access all inherited methods internally
        public_data = self.public_method()       # Inherited public method
        protected_data = self._protected_method() # Inherited protected method
        explicit_data = self._explicitly_public() # Explicit override
        return f"{public_data}, {protected_data}, {explicit_data}"

obj = Derived()

# Internal access works
result = obj.test_access()  # Works - internal access

# External access controlled by inheritance rules
# Protected inheritance converts public methods to protected
obj.public_method()         # PermissionError - public became protected
obj._protected_method()     # PermissionError - protected method
obj._explicitly_public()   # PermissionError - explicit public became protected
```

### Manual Application

You can also manually apply implicit access control without inheritance:

```python
from bouncer.utils.implicit import apply_implicit_access_control

class Base:
    def public_method(self):
        return "public"
    
    def _protected_method(self):
        return "protected"
    
    def __private_method(self):
        return "private"

# Manually apply implicit access control
apply_implicit_access_control(Base)

obj = Base()
obj.public_method()      # Works - public access
# obj._protected_method()  # PermissionError - protected access
# obj.__private_method()   # PermissionError - private access (name mangled)
```

### Explicit Override of Implicit Rules

Explicit decorators always take precedence over implicit naming conventions:

```python
class Base:
    @private                               # Explicit private
    def normal_name_but_private(self):     # Normal name, but explicitly private
        return "private despite normal name"
    
    @public                                # Explicit public
    def _underscore_but_public(self):      # Underscore name, but explicitly public
        return "public despite underscore"

@protected(Base)  # Apply implicit control
class Derived(Base):
    pass

obj = Derived()

# Explicit decorators override naming conventions
# obj.normal_name_but_private()    # PermissionError - explicitly private
obj._underscore_but_public()       # PermissionError - but protected inheritance affects it
```

## Friend Relationships

Friend classes and functions can access private and protected members of target classes, providing controlled access across class boundaries.

### Friend Classes

Friend classes can access private and protected members of the target class.

```python
class Target:
    @private
    def _private_method(self):
        return "private"
    
    @protected
    def _protected_method(self):
        return "protected"

@friend(Target)
class FriendA:
    def access_target(self, target):
        # Friend can access private methods
        private_data = target._private_method()
        protected_data = target._protected_method()
        return f"{private_data}, {protected_data}"

@friend(Target)
class FriendB:
    def inspect_target(self, target):
        # Multiple classes can be friends
        return target._protected_method()

# Usage
target = Target()
friend_a = FriendA()
friend_b = FriendB()

friend_a.access_target(target)   # Friend access works
friend_b.inspect_target(target)  # Multiple friends work

# Regular class cannot access private members
class Regular:
    def try_access(self, target):
        # PermissionError - not a friend
        return target._protected_method()
```

### Friend Functions

Friend functions are standalone functions that can access private and protected members.

```python
class Target:
    @private
    def _private_method(self):
        return "private"
    
    @protected
    def _protected_method(self):
        return "protected"

@friend(Target)
def friend_function_a(target):
    """Friend function for processing"""
    private_data = target._private_method()
    return f"Processed: {private_data}"

@friend(Target)
def friend_function_b(target):
    """Friend function for analysis"""
    protected_data = target._protected_method()
    return f"Analyzed: {protected_data}"

def regular_function(target):
    """Regular function - no friend access"""
    # PermissionError - cannot access private methods
    return target._private_method()

# Usage
target = Target()

friend_function_a(target)   # Friend function works
friend_function_b(target)   # Another friend function works
# regular_function(target)  # PermissionError
```

### Friend Descriptors

Friend relationships work with all Python descriptor types: staticmethod, classmethod, and property.

```python
class Target:
    def __init__(self, value):
        self._value = value
    
    @private
    def _private_method(self):
        return "private"
    
    @private
    @property
    def private_property(self):
        return self._value

class Helper:
    # Friend staticmethod
    @friend(Target)
    @staticmethod
    def static_helper(target):
        return target._private_method()
    
    # Friend classmethod
    @friend(Target)
    @classmethod
    def class_helper(cls, target):
        return target._private_method()
    
    # Friend instance method accessing property
    @friend(Target)
    def access_property(self, target):
        return target.private_property

target = Target("secret")
result1 = Helper.static_helper(target)    # Works
result2 = Helper.class_helper(target)     # Works
helper = Helper()
result3 = helper.access_property(target)  # Works
```

## Dual-Layer Security: Access Modifiers on Friend Methods

**Advanced Feature**: Apply access modifiers to friend methods themselves for fine-grained control.

```python
class Target:
    @private
    def _private_method(self):
        return "private"

class Helper:
    # Public friend method - anyone can call it
    @public
    @friend(Target)
    def public_access(self, target):
        return target._private_method()
    
    # Protected friend method - only inheritance can use it
    @protected
    @friend(Target)
    def protected_access(self, target):
        return target._private_method()
    
    # Private friend method - only internal use
    @private
    @friend(Target)
    def private_access(self, target):
        return target._private_method()
    
    def internal_operation(self, target):
        # Can use private friend method internally
        return self.private_access(target)

class DerivedHelper(Helper):
    def inherited_operation(self, target):
        # Can use protected friend method via inheritance
        return self.protected_access(target)

# Usage
target = Target()
helper = Helper()
derived = DerivedHelper()

# Public friend method works for everyone
helper.public_access(target)

# Protected friend method works via inheritance
derived.inherited_operation(target)

# Private friend method works via internal access
helper.internal_operation(target)

# Direct access to protected/private friend methods blocked
# helper.protected_access(target)  # PermissionError
# helper.private_access(target)    # PermissionError
```

### Staticmethod and Classmethod with Access Modifiers

```python
class Target:
    @private
    def _private_method(self):
        return "private"

class Helper:
    # Protected friend staticmethod
    @protected
    @friend(Target)
    @staticmethod
    def protected_static_helper(target):
        return target._private_method()
    
    # Private friend classmethod
    @private
    @friend(Target)
    @classmethod
    def private_class_helper(cls, target):
        return target._private_method()
    
    @classmethod
    def internal_class_operation(cls, target):
        # Can use private classmethod internally
        return cls.private_class_helper(target)

class DerivedHelper(Helper):
    @classmethod
    def use_protected_static(cls, target):
        # Can use protected staticmethod via inheritance
        return cls.protected_static_helper(target)

target = Target()
helper = Helper()
derived = DerivedHelper()

# Protected staticmethod works via inheritance
derived.use_protected_static(target)

# Private classmethod works via internal access
helper.internal_class_operation(target)

# Direct access blocked
# Helper.protected_static_helper(target)  # PermissionError
# Helper.private_class_helper(target)     # PermissionError
```

## C++ Style Inheritance Access Control

Bouncer implements true C++ style inheritance semantics with public, protected, and private inheritance types. The inheritance decorator automatically applies implicit access control to base classes and modifies access levels according to C++ rules.

### Public Inheritance (Default)

Standard Python inheritance behavior where access levels are preserved:

```python
class Base:
    def public_method(self):              # Implicit @public
        return "public"
    
    def _protected_method(self):          # Implicit @protected
        return "protected"
    
    def __private_method(self):           # Implicit @private
        return "private"

class Derived(Base):
    def test_access(self):
        # Can access public and protected members from base
        public_data = self.public_method()       # Inherited as public
        protected_data = self._protected_method() # Inherited as protected
        
        # Cannot access private members from base
        # private_data = self.__private_method()  # PermissionError
        
        return f"{public_data}, {protected_data}"

obj = Derived()
result = obj.test_access()          # Works internally
external_public = obj.public_method()  # Works externally - public access
# external_protected = obj._protected_method()  # PermissionError - protected
```

### Protected Inheritance

Protected inheritance converts public members to protected, following C++ semantics:

```python
class Base:
    def public_method(self):             # Implicit @public
        return "public"
    
    def _protected_method(self):         # Implicit @protected
        return "protected"
    
    @private
    def _private_method(self):           # Explicit @private
        return "private"

@protected(Base)  # Protected inheritance - applies implicit control to Base
class Derived(Base):
    def operation(self):
        # Can access all inherited members internally
        public_data = self.public_method()       # Now protected due to inheritance
        protected_data = self._protected_method() # Remains protected
        # Cannot access private members
        # secret = self._private_method()        # PermissionError
        return f"{public_data}, {protected_data}"

obj = Derived()
result = obj.operation()       # Works internally

# External access - all methods are now protected due to inheritance
# obj.public_method()          # PermissionError - public became protected
# obj._protected_method()      # PermissionError - protected remains protected
```

### Private Inheritance

Private inheritance makes all inherited members private to the derived class:

```python
class Base:
    def public_method(self):             # Implicit @public
        return "public"
    
    def _protected_method(self):         # Implicit @protected
        return "protected"

@private(Base)  # Private inheritance
class Derived(Base):
    def operation(self):
        # Can access inherited members internally
        public_data = self.public_method()    # Now private due to inheritance
        protected_data = self._protected_method() # Now private due to inheritance
        return f"{public_data}, {protected_data}"
    
    def public_interface(self):
        # Expose functionality through controlled interface
        return self.operation()

obj = Derived()
result = obj.public_interface()       # Works - controlled access

# External access blocked - all inherited methods are now private
# obj.public_method()                 # PermissionError - public became private
# obj._protected_method()             # PermissionError - protected became private
```

### Multiple Inheritance

Bouncer supports complex multiple inheritance patterns with proper access control. You can apply inheritance decorators to multiple base classes simultaneously:

```python
class Foo:
    def foo_public(self):              # Implicit @public
        return "foo public method"
    
    def _foo_protected(self):          # Implicit @protected
        return "foo protected method"
    
    def __foo_private(self):           # Implicit @private
        return "foo private method"

class Bar:
    def bar_public(self):              # Implicit @public
        return "bar public method"
    
    def _bar_protected(self):          # Implicit @protected
        return "bar protected method"
    
    @private                           # Explicit @private
    def bar_explicit_private(self):
        return "bar explicit private"

# Multiple inheritance with access control applied to all base classes
@protected(Foo, Bar)
class Qux(Foo, Bar):
    def qux_operation(self):
        # Can access all inherited members internally
        foo_pub = self.foo_public()              # Protected due to inheritance
        foo_prot = self._foo_protected()         # Protected (unchanged)
        bar_pub = self.bar_public()              # Protected due to inheritance
        bar_prot = self._bar_protected()         # Protected (unchanged)
        
        # Cannot access private members from base classes
        # foo_priv = self._Foo__foo_private()    # PermissionError
        # bar_priv = self.bar_explicit_private() # PermissionError
        
        return f"Qux: {foo_pub}, {foo_prot}, {bar_pub}, {bar_prot}"

qux = Qux()
result = qux.qux_operation()          # Works internally

# External access blocked due to protected inheritance
# qux.foo_public()                    # PermissionError - public became protected
# qux.bar_public()                    # PermissionError - public became protected
# qux._foo_protected()                # PermissionError - protected access blocked
# qux._bar_protected()                # PermissionError - protected access blocked
```

#### Complex Multiple Inheritance Hierarchies

```python
class BaseA:
    def method_a(self):                 # Implicit @public
        return "a"
    
    def _helper_a(self):                # Implicit @protected
        return "helper a"
    
    def __private_a(self):              # Implicit @private
        return "private a"

class BaseB:
    def method_b(self):                 # Implicit @public
        return "b"
    
    def _helper_b(self):                # Implicit @protected
        return "helper b"
    
    @private                            # Explicit @private
    def _private_b(self):
        return "private b"

class BaseC:
    def method_c(self):                 # Implicit @public
        return "c"
    
    def _helper_c(self):                # Implicit @protected
        return "helper c"

# Triple inheritance with different access patterns
@protected(BaseA, BaseB)               # Protected inheritance for BaseA and BaseB
@private(BaseC)                        # Private inheritance for BaseC
class Derived(BaseA, BaseB, BaseC):
    def operation(self):
        # BaseA methods - protected due to inheritance
        a_method = self.method_a()       # Protected
        a_helper = self._helper_a()      # Protected
        
        # BaseB methods - protected due to inheritance  
        b_method = self.method_b()       # Protected
        self._helper_b()                 # Protected
        
        # BaseC methods - private due to inheritance
        c_method = self.method_c()       # Private
        c_helper = self._helper_c()      # Private
        
        return f"{a_method}, {a_helper}, {b_method}, {c_method}, {c_helper}"
    
    def public_interface(self):
        # Expose controlled functionality
        return self.operation()

obj = Derived()
result = obj.public_interface()   # Works - controlled access

# External access completely blocked for all inherited methods
# obj.method_a()                  # PermissionError - protected inheritance
# obj.method_b()                  # PermissionError - protected inheritance  
# obj.method_c()                  # PermissionError - private inheritance
# obj._helper_a()                 # PermissionError - protected method
# obj._helper_b()                 # PermissionError - protected method
# obj._helper_c()                 # PermissionError - private method
```

#### Mixed Inheritance Types

You can combine different inheritance types for different base classes:

```python
class PublicAPI:
#### Mixed Inheritance Types

You can combine different inheritance types for different base classes:

```python
class BaseX:
    def method_x(self):                 # Implicit @public
        return "x"
    
    def _helper_x(self):                # Implicit @protected  
        return "helper x"

class BaseY:
    def method_y(self):                 # Implicit @public
        return "y"
    
    def _helper_y(self):                # Implicit @protected
        return "helper y"

class BaseZ:
    def method_z(self):                 # Implicit @public
        return "z"
    
    def _helper_z(self):                # Implicit @protected
        return "helper z"

# Mix inheritance types: public, protected, and private
class Mixed(BaseX, BaseY, BaseZ):
    pass

# Apply different inheritance types to different base classes
@protected(BaseY)                      # Only BaseY gets protected inheritance
@private(BaseZ)                        # Only BaseZ gets private inheritance
class Selective(BaseX, BaseY, BaseZ):
    def test_access_levels(self):
        # BaseX methods retain their original access levels
        x_data = self.method_x()         # Still public
        # x_helper = self._helper_x()    # Still protected (blocked externally)
        
        # BaseY methods become protected  
        y_data = self.method_y()         # Now protected
        y_helper = self._helper_y()      # Still protected
        
        # BaseZ methods become private
        z_data = self.method_z()         # Now private
        z_helper = self._helper_z()      # Now private
        
        return f"{x_data}, {y_data}, {z_data}"

obj = Selective()
result = obj.test_access_levels()   # Works internally

# External access follows inheritance rules
obj.method_x()                      # Works - public inheritance (default)
# obj.method_y()                    # PermissionError - protected inheritance
# obj.method_z()                    # PermissionError - private inheritance
```

### Inheritance with Friend Relationships

Friend relationships are preserved and work correctly with inheritance patterns:

### Inheritance with Friend Relationships

Friend relationships are preserved and work correctly with inheritance patterns:

```python
class Target:
    def _protected_method(self):        # Implicit @protected
        return "protected"

@friend(Target)
class Friend:
    def access_target(self, target):
        # Friend can access protected members
        return target._protected_method()

# Protected inheritance preserves friend relationships
@protected(Target)
class Derived(Target):
    def internal_operation(self):
        return self._protected_method()     # Works internally

class DerivedFriend(Friend):
    def inherited_access(self, target):
        # Inherits friend relationship
        return self.access_target(target)   # Friend access works

obj = Derived()
friend = DerivedFriend()

# Friend access works even with inheritance
result = friend.inherited_access(obj)  # Works - friend relationship preserved

# Regular external access blocked
# obj._protected_method()            # PermissionError - protected access
```

### Inheritance Summary

| Inheritance Type | Public Members | Protected Members | Private Members |
|------------------|----------------|-------------------|-----------------|
| **Public** (default) | Remain public | Remain protected | Remain private (inaccessible) |
| **Protected** `@protected(Base)` | Become protected | Remain protected | Remain private (inaccessible) |
| **Private** `@private(Base)` | Become private | Become private | Remain private (inaccessible) |

## Property Access Control

Control getter and setter access independently with sophisticated property decorators.

### Basic Property Control

```python
class Base:
    def __init__(self, name, value):
        self._name = name
        self._value = value
    
    @protected
    @property
    def value(self):
        """Protected getter - accessible in inheritance"""
        return self._value
    
    @value.setter
    @private
    def value(self, new_value):
        """Private setter - only same class"""
        if new_value > 0:
            self._value = new_value
    
    def update_value(self, amount):
        # Private setter works within same class
        self.value = self._value + amount
    
    @public
    @property
    def name(self):
        """Public getter"""
        return self._name

class Derived(Base):
    def check_value(self):
        # Can read value (protected getter)
        return f"Value: {self.value}"
    
    def try_modify_value(self, new_value):
        # Cannot use private setter
        # self.value = new_value  # PermissionError
        pass

obj1 = Base("item1", 100)
obj2 = Derived("item2", 200)

# Public property access
print(obj1.name)

# Protected property access via inheritance
print(obj2.check_value())

# Internal value modification
obj1.update_value(50)

# External access to protected property
# print(obj1.value)  # PermissionError
```

### Friend Access to Properties

```python
class Target:
    def __init__(self, value):
        self._value = value
    
    @private
    @property
    def private_property(self):
        return self._value

@friend(Target)
class Friend:
    def access_property(self, target):
        # Friend can access private property
        value = target.private_property
        return f"Accessed: {value}"

target = Target("secret")
friend = Friend()
result = friend.access_property(target)  # Works
```

## System Management

### Runtime Control

```python
from bouncer import (
    enable_enforcement, 
    disable_enforcement, 
    is_enforcement_enabled,
    get_access_control_system
)

class Base:
    @private
    def _private_method(self):
        return "private"

obj = Base()

# Normal enforcement
try:
    obj._private_method()  # PermissionError
except PermissionError:
    print("Access blocked")

# Disable enforcement (useful for testing)
disable_enforcement()
result = obj._private_method()  # Now works
print(f"Access allowed: {result}")

# Re-enable enforcement
enable_enforcement()
# obj.secret_method()  # PermissionError again

# Check enforcement status
print(f"Enforcement enabled: {is_enforcement_enabled()}")
```

### System Metrics and Debugging

```python
from bouncer.system import get_access_control_system

# Get system instance for advanced operations
access_control = get_access_control_system()

# Check enforcement status
print(f"Enforcement enabled: {access_control.enforcement_enabled}")

# Get friendship relationships count
friendship_manager = access_control._friendship_manager
print(f"Total friend relationships: {friendship_manager.get_friends_count()}")
print(f"Classes with friends: {friendship_manager.get_relationships_count()}")

# Reset system state (useful for testing)
from bouncer import reset_system
reset_system()
```

## Error Handling

Bouncer provides specific exception types for different scenarios.

### Exception Types

```python
from bouncer.exceptions import (
    AccessControlError,          # Base exception
    PermissionDeniedError,       # Custom access denial (if using custom exceptions)
    DecoratorConflictError,      # Conflicting decorators
)

# Standard PermissionError is used by default
class SecureClass:
    @private
    def secret_method(self):
        return "secret"

try:
    obj = SecureClass()
    obj.secret_method()
except PermissionError as e:
    print(f"Access denied: {e}")
    # Output: Access denied: Access denied to private method secret_method
```

### Decorator Conflicts

```python
# This will raise an error during class creation
try:
    class ConflictClass:
        @private
        @public  # Conflicting access levels
        def conflicted_method(self):
            pass
except ValueError as e:
    print(f"Decorator conflict: {e}")
```

### Invalid Usage Detection

```python
# Invalid decorator usage is detected
try:
    @private  # Cannot use on module-level function
    def module_function():
        pass
except ValueError as e:
    print(f"Invalid usage: {e}")
```
## Testing and Development

### Testing with Enforcement Control

```python
import unittest
from bouncer import disable_enforcement, enable_enforcement

class TestSecureClass(unittest.TestCase):
    def setUp(self):
        # Disable enforcement for easier testing
        disable_enforcement()
    
    def tearDown(self):
        # Re-enable enforcement
        enable_enforcement()
    
    def test_private_method_access(self):
        class TestClass:
            @private
            def _secret(self):
                return "secret"
        
        obj = TestClass()
        # This works because enforcement is disabled
        result = obj._secret()
        self.assertEqual(result, "secret")

# Or use context manager approach
from bouncer.system import get_access_control_system

def test_with_disabled_enforcement():
    access_control = get_access_control_system()
    original_state = access_control.enforcement_enabled
    
    try:
        access_control.enforcement_enabled = False
        # Test code here with enforcement disabled
        pass
    finally:
        access_control.enforcement_enabled = original_state
```

### Debugging Friend Relationships

```python
from bouncer.system import get_access_control_system

class TargetClass:
    @private
    def secret(self):
        return "secret"

@friend(TargetClass)
class FriendClass:
    pass

# Debug friendship relationships
access_control = get_access_control_system()
friendship_manager = access_control._friendship_manager

print(f"Total friends: {friendship_manager.get_friends_count()}")
print(f"Classes with friends: {friendship_manager.get_relationships_count()}")

# Check if specific friendship exists
is_friend = friendship_manager.is_friend(TargetClass, FriendClass)
print(f"FriendClass is friend of TargetClass: {is_friend}")
```

## Requirements

- **Python 3.12+**
- **No external dependencies** for core functionality
- **Optional development dependencies** for testing and development

## Development Setup

### Clone and Setup

```bash
git clone https://github.com/Ma1achy/Bouncer.git
cd Bouncer
pip install -e .[dev]
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bouncer

# Run specific test categories
pytest -m access_control      # Access control tests
pytest -m friend_methods      # Friend relationship tests
pytest -m inheritance         # Inheritance tests
pytest -m edge_cases          # Edge cases and boundary tests
```

### Development Commands

```bash
# Format code
black bouncer/ tests/

# Type checking
mypy bouncer/

# Lint code
flake8 bouncer/ tests/
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest features.

### Development Guidelines

1. **Add tests** for new features
2. **Update documentation** for API changes
3. **Follow code style** (Black formatting, type hints)
4. **Ensure compatibility** with Python 3.8+

## License

MIT License - see [LICENSE](LICENSE) file for details.