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
            # For classmethods, obj could be None when called on the class
            # We use objtype as the effective class for access checking
            check_obj = obj if obj is not None else objtype
            self._check_access_classmethod(check_obj, objtype)
            return self._func_or_value(objtype, *args, **kwargs)
        
        return self._create_wrapper_with_context(wrapper)
    
    def _check_access_classmethod(self, check_obj, objtype):
        """Class method specific access checking"""
        # Import here to avoid circular import
        from ..system.access_control import get_access_control_system
        from ..inspection.stack_inspector import StackInspector

        access_control = get_access_control_system()

        # If enforcement is disabled, allow all access
        if not access_control.enforcement_enabled:
            return

        # Safety check: if _owner is None, __set_name__ hasn't been called yet
        if self._owner is None or self._name is None:
            return

        # Get caller info from stack
        stack_inspector = StackInspector()
        caller_info = stack_inspector.get_caller_info()
        
        # For class methods, the instance_class should be the class itself (objtype)
        # not the metaclass (which would be check_obj.__class__)
        if hasattr(access_control, '_access_checker'):
            print(f"DEBUG CLASSMETHOD: owner={self._owner}, objtype={objtype}, caller={caller_info.caller_class}, method={caller_info.caller_method}")
            result = access_control._access_checker.can_access(
                self._owner, self._name, self._access_level, caller_info, objtype
            )
        else:
            result = access_control.check_access(self._owner, self._name, self._access_level)
        
        if not result:
            from ..exceptions import PermissionDeniedError
            raise PermissionDeniedError(
                self._access_level.value,
                self._get_member_type(),
                self._name
            )
    
    def _get_member_type(self) -> str:
        return "class method"
