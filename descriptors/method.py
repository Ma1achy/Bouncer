"""
Descriptor for regular methods
"""
from functools import wraps
from .base import AccessControlledDescriptor
from ..core import internal_call_context


class MethodDescriptor(AccessControlledDescriptor):
    """Descriptor for regular methods"""
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        
        @wraps(self._func_or_value)
        def wrapper(*args, **kwargs):
            self._check_access(obj)
            
            # Import here to avoid circular import
            from ..system.access_control import get_access_control_system
            access_control = get_access_control_system()
            
            access_control.emit_event('access_attempt', {
                'method': f"{self._owner.__name__}.{self._name}",
                'access_level': self._access_level.value,
                'allowed': True
            })
            
            with internal_call_context():
                return self._func_or_value(obj, *args, **kwargs)
        
        return wrapper
    
    def _get_member_type(self) -> str:
        return "method"
