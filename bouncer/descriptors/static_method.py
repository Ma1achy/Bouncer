"""
Descriptor for static methods
"""
import threading
from functools import wraps
from .base import AccessControlledDescriptor

# Thread-local storage for staticmethod caller context
_thread_local = threading.local()


class StaticMethodDescriptor(AccessControlledDescriptor):
    """Descriptor for static methods"""
    
    def __get__(self, obj, objtype=None):
        @wraps(self._func_or_value)
        def wrapper(*args, **kwargs):
            # Store the owner class in local variables for stack inspection
            _bouncer_owner_class = self._owner
            _bouncer_method_name = self._name
            # Also store on the wrapper function itself
            wrapper._bouncer_owner_class = self._owner
            wrapper._bouncer_method_name = self._name
            
            # Only store in thread-local storage if this is a friend method
            old_context = None
            is_friend_method = hasattr(self._func_or_value, '_friend_classes') and self._func_or_value._friend_classes
            if is_friend_method:
                old_context = getattr(_thread_local, 'staticmethod_context', None)
                _thread_local.staticmethod_context = {
                    'caller_class': self._owner,
                    'caller_method': self._name
                }
            
            try:
                self._check_access(obj)
                return self._func_or_value(*args, **kwargs)
            finally:
                # Restore previous context only if we set it
                if is_friend_method:
                    _thread_local.staticmethod_context = old_context
        
        return wrapper
    
    def _get_member_type(self) -> str:
        return "static method"
