"""
Descriptor for static methods
"""
from functools import wraps
from .base import AccessControlledDescriptor


class StaticMethodDescriptor(AccessControlledDescriptor):
    """Descriptor for static methods"""
    
    def __get__(self, obj, objtype=None):
        @wraps(self._func_or_value)
        def wrapper(*args, **kwargs):
            self._check_access(obj)
            return self._func_or_value(*args, **kwargs)
        
        return wrapper
    
    def _get_member_type(self) -> str:
        return "static method"
