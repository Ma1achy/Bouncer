"""
Implicit access control based on naming conventions
"""
from typing import Type, Any
from ..core import AccessLevel
from ..descriptors import DescriptorFactory


def detect_implicit_access_level(method_name: str) -> AccessLevel:
    """
    Detect access level from Python naming conventions:
    - __method = private (double underscore, but not dunder methods)
    - _method = protected (single underscore)
    - method = public (no underscore)
    """
    # Skip dunder methods (like __init__, __str__, etc.)
    if method_name.startswith('__') and method_name.endswith('__'):
        return AccessLevel.PUBLIC  # Dunder methods should remain public
    
    if method_name.startswith('__'):
        # Double underscore prefix (but not dunder methods)
        return AccessLevel.PRIVATE
    elif method_name.startswith('_'):
        # Single underscore prefix
        return AccessLevel.PROTECTED
    else:
        # No underscore prefix
        return AccessLevel.PUBLIC


def apply_implicit_access_control(cls: Type) -> None:
    """
    Apply implicit access control based on naming conventions to a class.
    Only applies to methods that don't already have explicit decorators.
    """
    # Store original method names before name mangling for proper detection
    methods_to_control = {}

    # Collect methods and their original names
    for name, method in list(cls.__dict__.items()):
        # Only wrap methods defined directly in this class, not inherited
        if not hasattr(cls, name):
            continue
        if getattr(getattr(cls, name), '__objclass__', cls) is not cls:
            continue
        # Skip special methods (dunder methods like __init__, __str__)
        if name.startswith('__') and name.endswith('__'):
            continue

        # Skip if already has explicit access control
        if hasattr(method, '_access_level'):
            continue

        # Skip if it's already a descriptor from our system
        if hasattr(method, '_owner') and hasattr(method, '_access_level'):
            continue

        # Handle Python name mangling: _ClassName__method -> __method
        original_name = name
        if name.startswith(f'_{cls.__name__}__'):
            # This is a name-mangled method, get the original name
            original_name = '__' + name[len(f'_{cls.__name__}__'):]

        # Detect implicit access level using original name
        implicit_level = detect_implicit_access_level(original_name)

        # Apply access control to all callable methods (including public)
        if callable(method):
            methods_to_control[name] = (method, implicit_level, original_name)

    # Apply access control to methods
    for name, (method, implicit_level, original_name) in methods_to_control.items():
        # Create appropriate descriptor based on method type and access level
        if isinstance(method, staticmethod):
            descriptor = DescriptorFactory.create_static_method_descriptor(
                method.__func__, implicit_level
            )
        elif isinstance(method, classmethod):
            descriptor = DescriptorFactory.create_class_method_descriptor(
                method.__func__, implicit_level
            )
        elif isinstance(method, property):
            descriptor = DescriptorFactory.create_property_descriptor(
                method.fget, implicit_level, method.fset, method.fdel, method.__doc__
            )
        elif callable(method):
            # Regular method
            descriptor = DescriptorFactory.create_method_descriptor(method, implicit_level)
        else:
            continue

        # Replace the method with the access-controlled descriptor
        setattr(cls, name, descriptor)
        # Ensure descriptor knows its name and owner
        if hasattr(descriptor, '__set_name__'):
            descriptor.__set_name__(cls, name)
