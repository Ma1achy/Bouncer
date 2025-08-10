"""
Validation utilities for the Bouncer Access Control System
"""
from typing import Callable


def validate_method_usage(func: Callable, decorator_name: str) -> None:
    """Validate that a decorator is being used on a class method, not a module-level function"""
    if hasattr(func, '__qualname__'):
        qualname_parts = func.__qualname__.split('.')
        if len(qualname_parts) < 2:
            raise ValueError(
                f"@{decorator_name} decorator cannot be applied to module-level function '{func.__name__}'. "
                f"Access control decorators can only be used on class methods."
            )


def validate_class_decoration(cls, decorator_name: str) -> None:
    """Validate that class decoration is being used correctly"""
    import inspect
    
    frame = inspect.currentframe()
    try:
        caller_frame = frame.f_back.f_back  # Go up two frames
        if caller_frame and cls.__name__ not in caller_frame.f_locals:
            raise ValueError(
                f"@{decorator_name} cannot be used as a class decorator without arguments. "
                f"Use @{decorator_name}(BaseClass) for {decorator_name} inheritance from BaseClass, "
                f"or apply @{decorator_name} to individual methods instead."
            )
    finally:
        del frame
