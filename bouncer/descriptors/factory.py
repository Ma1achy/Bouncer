"""
Factory for creating appropriate descriptors
"""
from typing import Callable
from ..core import AccessLevel
from .base import AccessControlledDescriptor
from .method import MethodDescriptor
from .static_method import StaticMethodDescriptor
from .class_method import ClassMethodDescriptor
from .property import PropertyDescriptor


class DescriptorFactory:
    """Factory for creating appropriate descriptors"""
    
    @staticmethod
    def create_method_descriptor(func: Callable, access_level: AccessLevel) -> AccessControlledDescriptor:
        """Create appropriate method descriptor based on function type"""
        # Check for friend method decoration before creating descriptor
        DescriptorFactory._register_friend_method_if_needed(func)
        
        if isinstance(func, staticmethod):
            # Check the underlying function for friend decoration too
            DescriptorFactory._register_friend_method_if_needed(func.__func__)
            return StaticMethodDescriptor(func.__func__, access_level)
        elif isinstance(func, classmethod):
            # Check the underlying function for friend decoration too
            DescriptorFactory._register_friend_method_if_needed(func.__func__)
            return ClassMethodDescriptor(func.__func__, access_level)
        elif isinstance(func, property):
            # Check the getter function for friend decoration
            DescriptorFactory._register_friend_method_if_needed(func.fget)
            return PropertyDescriptor(func.fget, access_level, func.fset, func.fdel, func.__doc__)
        else:
            return MethodDescriptor(func, access_level)
    
    @staticmethod
    def _register_friend_method_if_needed(func: Callable) -> None:
        """Register a method as a friend if it was decorated with @friend"""
        if func and hasattr(func, '_bouncer_friend_target') and hasattr(func, '_bouncer_is_friend_method'):
            # We can't register now because we don't know the owner class yet
            # The descriptor will handle this in __set_name__
            pass
