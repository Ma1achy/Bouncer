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
        if isinstance(func, staticmethod):
            return StaticMethodDescriptor(func.__func__, access_level)
        elif isinstance(func, classmethod):
            return ClassMethodDescriptor(func.__func__, access_level)
        elif isinstance(func, property):
            return PropertyDescriptor(func.fget, access_level, func.fset, func.fdel, func.__doc__)
        else:
            return MethodDescriptor(func, access_level)
