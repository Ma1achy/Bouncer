"""
Descriptor for class methods
"""
from functools import wraps
from .base import AccessControlledDescriptor


class ClassMethodDescriptor(AccessControlledDescriptor):
    """Descriptor for class methods"""
    
    def __get__(self, obj, objtype=None):
        if objtype is None:
            objtype = type(obj)
        
        @wraps(self._func_or_value)
        def wrapper(*args, **kwargs):
            self._check_access(obj)
            return self._func_or_value(objtype, *args, **kwargs)
        
        return wrapper
    
    def _get_member_type(self) -> str:
        return "class method"
