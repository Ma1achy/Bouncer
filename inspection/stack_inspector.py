"""
Stack inspection logic for the Bouncer Access Control System
"""
import inspect
from typing import Type
from ..core import CallerInfo


class StackInspector:
    """Handles stack inspection logic"""
    
    PYTEST_MODULES = ['pluggy', '_pytest', 'pytest', 'unittest', 'runpy', 'importlib']
    WRAPPER_FUNCTIONS = [
        'controlled_static', 'controlled_class', 'wrapper',
        'static_wrapper', 'class_wrapper', 'method_wrapper',
        'controlled_getattribute', 'controlled_setattr', 'getter',
        '_check_access', '__get__', '__set__', '__delete__'  # Add descriptor methods
    ]
    
    def get_caller_info(self) -> CallerInfo:
        """Get caller class and method from stack"""
        stack = inspect.stack()
        
        # Look for caller starting from frame 3
        for i, frame_info in enumerate(stack[3:], 3):
            if self._is_internal_frame(frame_info):
                continue
            
            frame_locals = frame_info.frame.f_locals
            
            # Look for instance methods (with 'self')
            if 'self' in frame_locals:
                caller_instance = frame_locals['self']
                caller_method_name = frame_info.function
                caller_class = self._find_method_defining_class(
                    caller_instance, caller_method_name
                )
                return CallerInfo(caller_class, caller_method_name)
            
            # Look for class methods (with 'cls')
            elif 'cls' in frame_locals and isinstance(frame_locals['cls'], type):
                caller_class = frame_locals['cls']
                caller_method_name = frame_info.function
                return CallerInfo(caller_class, caller_method_name)
        
        return CallerInfo(None, None)
    
    def is_explicit_base_class_call(self, target_class: Type, caller_class: Type) -> bool:
        """Detect if this is an explicit Base.method() call vs inherited access"""
        stack = inspect.stack()
        
        for frame_info in stack[3:]:
            if self._is_internal_frame(frame_info):
                continue
            
            code_context = frame_info.code_context
            if code_context:
                for line in code_context:
                    if line and f"{target_class.__name__}." in line:
                        return True
            break
        
        return False
    
    def _is_internal_frame(self, frame_info) -> bool:
        """Check if frame is internal (pytest or bouncer)"""
        return (self._is_pytest_internal_frame(frame_info) or 
                self._is_bouncer_wrapper_frame(frame_info))
    
    def _is_pytest_internal_frame(self, frame_info) -> bool:
        """Check if a frame is part of pytest's internal execution"""
        filename = frame_info.filename
        module_name = frame_info.frame.f_globals.get('__name__', '')
        
        return any(pytest_module in module_name or pytest_module in filename 
                  for pytest_module in self.PYTEST_MODULES)
    
    def _is_bouncer_wrapper_frame(self, frame_info) -> bool:
        """Check if a frame is one of our wrapper functions"""
        return frame_info.function in self.WRAPPER_FUNCTIONS
    
    def _find_method_defining_class(self, instance, method_name) -> Type:
        """Find the class that actually defines the given method"""
        instance_class = type(instance)
        
        for cls in instance_class.__mro__:
            if hasattr(cls, method_name) and method_name in cls.__dict__:
                return cls
        
        return instance_class
