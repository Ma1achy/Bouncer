"""
Base class for access control decorators using Template Method pattern
"""
import inspect
from typing import Callable
from ..core import AccessLevel, InheritanceType
from ..descriptors import DescriptorFactory


class AccessControlDecorator:
    """Base class for access control decorators using Template Method pattern"""
    
    def __init__(self, access_level: AccessLevel):
        self._access_level = access_level
    
    def __call__(self, *args):
        """Template method for decorator application"""
        if len(args) == 0:
            return self._create_parameterized_decorator()
        elif len(args) == 1:
            return self._handle_single_argument(args[0])
        else:
            return self._handle_multiple_arguments(args)
    
    def _create_parameterized_decorator(self):
        """Create decorator when called with parentheses"""
        def decorator(func):
            return self._apply_to_function(func)
        return decorator
    
    def _handle_single_argument(self, arg):
        """Handle single argument (direct decoration or inheritance)"""
        if isinstance(arg, type):
            return self._handle_class_decoration(arg)
        else:
            return self._apply_to_function(arg)
    
    def _handle_multiple_arguments(self, args):
        """Handle multiple arguments (inheritance from multiple bases)"""
        if all(isinstance(arg, type) for arg in args):
            return self._create_inheritance_decorator(args)
        else:
            raise ValueError(f"All arguments to @{self._access_level.value} must be classes for inheritance")
    
    def _apply_to_function(self, func):
        """Apply access control to a function"""
        self._validate_function_usage(func)
        self._check_access_level_conflict(func)
        return DescriptorFactory.create_method_descriptor(func, self._access_level)
    
    def _handle_class_decoration(self, cls):
        """Handle class decoration (inheritance)"""
        # For now, allow all class decoration and create inheritance
        return self._create_inheritance_decorator([cls])
    
    def _create_inheritance_decorator(self, base_classes):
        """Create inheritance decorator"""
        inheritance_type = InheritanceType(self._access_level.value)
        
        def decorator(derived_class):
            self._apply_implicit_access_control(derived_class)
            
            if not hasattr(derived_class, '_inheritance_info'):
                derived_class._inheritance_info = {}
            
            for base_class in base_classes:
                derived_class._inheritance_info[base_class.__name__] = inheritance_type.value
                # Additional inheritance logic would go here
            
            return derived_class
        
        return decorator
    
    def _validate_function_usage(self, func):
        """Validate decorator is used on class methods"""
        if hasattr(func, '__qualname__') and len(func.__qualname__.split('.')) < 2:
            raise ValueError(
                f"@{self._access_level.value} decorator cannot be applied to module-level function. "
                f"Access control decorators can only be used on class methods."
            )
    
    def _check_access_level_conflict(self, func):
        """Check for conflicting access level decorators"""
        existing_level = getattr(func, '_access_level', None)
        if existing_level and existing_level != self._access_level.value:
            raise ValueError(
                f"Conflicting access level decorators: method already has @{existing_level} "
                f"decorator, cannot apply @{self._access_level.value} decorator"
            )
        
        if hasattr(func, '__call__') and not hasattr(func, 'func'):
            func._access_level = self._access_level.value
    
    def _is_bare_class_decoration(self, cls):
        """Check if this is bare class decoration (invalid)"""
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back
            if caller_frame and cls.__name__ not in caller_frame.f_locals:
                return True
        finally:
            del frame
        return False
    
    def _apply_implicit_access_control(self, cls):
        """Apply implicit access control based on naming conventions"""
        from ..utils import apply_implicit_access_control
        apply_implicit_access_control(cls)
