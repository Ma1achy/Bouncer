"""
Base class for access control decorators using Template Method pattern
"""
import inspect
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
            arg = args[0]
            if isinstance(arg, type):
                # This is a class - we need to check if it's bare decoration or inheritance
                if self._is_bare_class_decoration():
                    # This is invalid bare decoration like @private \n class Foo:
                    raise ValueError(
                        f"@{self._access_level.value} cannot be used as a class decorator without arguments. "
                        f"Use @{self._access_level.value}(BaseClass) for {self._access_level.value} inheritance from BaseClass, "
                        f"or apply @{self._access_level.value} to individual methods instead."
                    )
                else:
                    # This is valid - @private(BaseClass) called, now applying to derived class
                    return self._handle_class_decoration(arg)
            else:
                return self._apply_to_function(arg)
        else:
            return self._handle_multiple_arguments(args)
    
    def _create_parameterized_decorator(self):
        """Create decorator when called with parentheses"""
        def decorator(func):
            return self._apply_to_function(func)
        return decorator
    
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
        
        # Check if this is already a descriptor created by the bouncer system
        from ..descriptors.base import AccessControlledDescriptor
        if isinstance(func, AccessControlledDescriptor):
            # Update the access level of the existing descriptor
            func._access_level = self._access_level
            return func
        
        return DescriptorFactory.create_method_descriptor(func, self._access_level)
    
    def _handle_class_decoration(self, cls):
        """Handle class decoration (inheritance)"""
        # If we get here, it's valid inheritance decoration
        return self._create_inheritance_decorator([cls])
    
    def _create_inheritance_decorator(self, base_classes):
        """Create inheritance decorator"""
        inheritance_type = InheritanceType(self._access_level.value)
        
        def decorator(derived_class):
            # Validate that this is actually being applied to a class
            if not isinstance(derived_class, type):
                base_names = [base.__name__ for base in base_classes]
                if callable(derived_class):
                    if hasattr(derived_class, '__qualname__') and '.' in derived_class.__qualname__:
                        target_type = "method"
                    else:
                        target_type = "function"
                    raise ValueError(
                        f"@{self._access_level.value}({', '.join(base_names)}) cannot be applied to {target_type}. "
                        f"Inheritance decorators can only be applied to classes. "
                        f"Use @{self._access_level.value} (without parentheses) for {target_type} access control."
                    )
                else:
                    raise ValueError(
                        f"@{self._access_level.value}({', '.join(base_names)}) can only be applied to classes for inheritance."
                    )
            
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
        if hasattr(func, '__qualname__'):
            qualname_parts = func.__qualname__.split('.')

            # Check if this looks like a class method by examining the pattern
            # Valid patterns:
            # - ClassName.method_name (normal case)
            # - outer_func.<locals>.ClassName.method_name (class inside function)
            # - OuterClass.NestedClass.method_name (nested class)
            # Invalid patterns:
            # - function_name (module-level function)
            # - outer_func.<locals>.function_name (nested function)

            if len(qualname_parts) < 2:
                # Single part = module-level function
                raise ValueError(
                    f"@{self._access_level.value} decorator cannot be applied to module-level function. "
                    f"Access control decorators can only be used on class methods."
                )
            elif '<locals>' in qualname_parts:
                # If it contains <locals>, check if it ends with ClassName.method_name
                # Find the last occurrence of <locals>
                locals_index = len(qualname_parts) - 1 - qualname_parts[::-1].index('<locals>')
                remaining_parts = qualname_parts[locals_index + 1:]

                # Should have at least 2 parts after <locals>: ClassName.method_name
                # Could be more for nested classes: OuterClass.InnerClass.method_name
                if len(remaining_parts) < 2:
                    raise ValueError(
                        f"@{self._access_level.value} decorator cannot be applied to module-level function. "
                        f"Access control decorators can only be used on class methods."
                    )
            # For normal cases without <locals>, we need at least 2 parts for ClassName.method_name
            # Could be more for nested classes

    def _check_access_level_conflict(self, func):
        """Check for conflicting access level decorators"""
        existing_level = None
        has_friend_flag = False
        
        # Check direct access level and friend flag
        if hasattr(func, '_access_level'):
            existing_level = getattr(func, '_access_level')
            has_friend_flag = getattr(func, '_created_by_friend_decorator', False)
        # Check if this is a property containing an access-controlled descriptor
        elif isinstance(func, property) and hasattr(func.fget, '_access_level'):
            existing_level = getattr(func.fget, '_access_level')
            has_friend_flag = getattr(func.fget, '_created_by_friend_decorator', False)
        # Check if this is a staticmethod containing an access-controlled descriptor
        elif isinstance(func, staticmethod) and hasattr(func.__func__, '_access_level'):
            existing_level = getattr(func.__func__, '_access_level')
            has_friend_flag = getattr(func.__func__, '_created_by_friend_decorator', False)
        # Check if this is a classmethod containing an access-controlled descriptor
        elif isinstance(func, classmethod) and hasattr(func.__func__, '_access_level'):
            existing_level = getattr(func.__func__, '_access_level')
            has_friend_flag = getattr(func.__func__, '_created_by_friend_decorator', False)

        if existing_level is not None:
            # Special case: Allow overriding or confirming access level if it was set by friend decorator
            if has_friend_flag and existing_level == AccessLevel.PUBLIC:
                # Allow explicit access level to override or confirm the friend decorator's default
                return
            
            # Provide more specific error messages based on the wrapper type
            if isinstance(func, property):
                wrapper_info = " (found in property.fget)"
            elif isinstance(func, staticmethod):
                wrapper_info = " (found in staticmethod.__func__)"
            elif isinstance(func, classmethod):
                wrapper_info = " (found in classmethod.__func__)"
            else:
                wrapper_info = ""
            
            if existing_level == self._access_level:
                raise ValueError(
                    f"Duplicate access level decorators: method already has @{existing_level.value} "
                    f"decorator{wrapper_info}, cannot apply another @{self._access_level.value} decorator"
                )
            else:
                raise ValueError(
                    f"Conflicting access level decorators: method already has @{existing_level.value} "
                    f"decorator{wrapper_info}, cannot apply @{self._access_level.value} decorator"
                )

    def _is_bare_class_decoration(self):
        """Check if this is bare class decoration (invalid)"""
        try:
            # Use inspect.stack() to get reliable frame information
            stack = inspect.stack()
            
            # Look for the decorator application in the stack
            # We skip the first few frames which are internal to our decorator
            for frame_info in stack[3:8]:  # Check a reasonable range of frames
                if frame_info.code_context:
                    line = frame_info.code_context[0].strip()
                    # Look for patterns like "@private" without parentheses
                    decorator_name = f"@{self._access_level.value}"
                    if line.startswith(decorator_name) and "(" not in line:
                        return True  # Bare decoration detected
                    elif f"@{self._access_level.value}(" in line:
                        return False  # Inheritance decoration detected
            
            # If we can't determine from the stack, assume it's valid (safer)
            return False
        except Exception:
            # If anything goes wrong with stack inspection, assume valid
            return False
    
    def _apply_implicit_access_control(self, cls):
        """Apply implicit access control based on naming conventions and inheritance"""
        from ..utils import apply_implicit_access_control
        from ..descriptors import DescriptorFactory
        
        # First apply standard implicit access control
        apply_implicit_access_control(cls)
        
        # For inheritance decoration, also ensure all inherited methods have descriptors
        # so they can participate in inheritance-based access control
        for name in dir(cls):
            # Skip special methods and private attributes
            if name.startswith('__') and name.endswith('__'):
                continue
            if name.startswith('_' + cls.__name__ + '__'):  # Name-mangled private
                continue
                
            attr = getattr(cls, name)
            
            # Only process callable methods that aren't already our descriptors
            if (callable(attr) and 
                not hasattr(attr, '_access_level') and 
                not hasattr(attr, '_owner')):
                
                # Check if this method is inherited (not defined in this class)
                if name not in cls.__dict__:
                    # This is an inherited method - wrap it with a descriptor
                    # so it can participate in inheritance-based access control
                    
                    # Determine the original access level
                    if name.startswith('_'):
                        access_level = AccessLevel.PROTECTED
                    else:
                        access_level = AccessLevel.PUBLIC
                    
                    # Create a descriptor for the inherited method
                    descriptor = DescriptorFactory.create_method_descriptor(attr, access_level)
                    setattr(cls, name, descriptor)
                    if hasattr(descriptor, '__set_name__'):
                        descriptor.__set_name__(cls, name)
