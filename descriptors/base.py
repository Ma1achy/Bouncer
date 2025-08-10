"""
Abstract base class for access-controlled descriptors
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Type
from ..core import AccessLevel


class AccessControlledDescriptor(ABC):
    """Abstract base class for access-controlled descriptors"""
    
    def __init__(self, func_or_value: Any, access_level: AccessLevel):
        self._func_or_value = func_or_value
        self._access_level = access_level
        self._name: Optional[str] = None
        self._owner: Optional[Type] = None
        
        # Preserve function attributes
        if hasattr(func_or_value, '__name__'):
            self.__name__ = func_or_value.__name__
    
    def __set_name__(self, owner: Type, name: str) -> None:
        """Called when descriptor is assigned to a class attribute"""
        self._name = name
        self._owner = owner
        # Import here to avoid circular import
        from ..system.access_control import get_access_control_system
        access_control = get_access_control_system()
        access_control.register_method(owner.__name__, name, self._access_level)
    
    @abstractmethod
    def __get__(self, obj, objtype=None):
        """Abstract method for descriptor access"""
        pass
    
    def _check_access(self, obj=None) -> None:
        """Check access permissions"""
        # Import here to avoid circular import
        from ..system.access_control import get_access_control_system
        from ..inspection.stack_inspector import StackInspector
        from ..core.value_objects import CallerInfo
        
        access_control = get_access_control_system()
        
        # If enforcement is disabled, allow all access
        if not access_control.enforcement_enabled:
            return
        
        # Get caller info from stack
        stack_inspector = StackInspector()
        caller_info = stack_inspector.get_caller_info()
        
        # If stack inspection failed, try to infer from object instance
        if not caller_info.caller_class and obj is not None:
            # If we're accessing from the same class, allow it
            # This handles self.property access within the class
            caller_info = CallerInfo(
                caller_class=obj.__class__,
                caller_method="<same_class_access>"
            )
        
        # Use the access checker directly with our caller info
        if hasattr(access_control, '_access_checker'):
            # Pass instance class for inheritance analysis
            instance_class = obj.__class__ if obj is not None else None
            result = access_control._access_checker.can_access(
                self._owner, self._name, self._access_level, caller_info, instance_class
            )
        else:
            result = access_control.check_access(self._owner, self._name, self._access_level)
        
        if not result:
            raise PermissionError(
                f"Access denied to {self._access_level.value} {self._get_member_type()} {self._name}"
            )
    
    @abstractmethod
    def _get_member_type(self) -> str:
        """Get the type of member (method, property, etc.)"""
        pass
