"""
Main access checking logic
"""
from typing import Type
from ..core import AccessLevel, InheritanceType, CallerInfo
from ..inspection import StackInspector
from .friendship import FriendshipManager
from .inheritance import InheritanceAnalyzer


class AccessChecker:
    """Main access checking logic"""
    
    def __init__(self, friendship_manager: FriendshipManager, 
                 inheritance_analyzer: InheritanceAnalyzer,
                 stack_inspector: StackInspector):
        self._friendship_manager = friendship_manager
        self._inheritance_analyzer = inheritance_analyzer
        self._stack_inspector = stack_inspector
    
    def can_access(self, target_class: Type, method_name: str, 
                   access_level: AccessLevel, caller_info: CallerInfo = None, 
                   instance_class: Type = None) -> bool:
        """Check if access should be allowed"""
        if not caller_info:
            caller_info = self._stack_inspector.get_caller_info()
        
        caller_class = caller_info.caller_class
        
        # Check for friend access first (unified logic)
        if self._check_friend_access(target_class, access_level, caller_info):
            return True
        
        # Use instance class if provided for inheritance analysis
        actual_target_class = instance_class if instance_class else target_class
        
        # For private methods, enforce strict C++ semantics
        if access_level == AccessLevel.PRIVATE:
            # Special case: during constructor chains, allow access based on the 
            # immediate constructor context rather than the ultimate caller
            if (caller_info and caller_info.caller_method == '__init__' and
                instance_class and caller_class and target_class):
                # In constructor context, check if target_class is in the inheritance hierarchy
                # This handles super().__init__() calling private methods correctly
                if (issubclass(instance_class, target_class) or issubclass(target_class, instance_class)):
                    return True
            
            # In C++ semantics, private methods are only accessible when:
            # 1. Called from the exact same class (caller_class == target_class)
            # 2. AND the instance is of the same class or during constructor chains
            if caller_class == target_class:
                # Same class calling its own private method
                if not instance_class or instance_class == target_class:
                    # Direct instance access or no instance context
                    return True
                else:
                    # Private method of base class called on derived class instance
                    # This should be denied in strict C++ semantics
                    return False
            else:
                # Different class trying to access private method - always deny
                return False
        
        # Same class access for non-private methods is always allowed
        if caller_class == target_class:
            return True
        
        # Check if this is inheritance access (caller is derived from target)
        if caller_class and target_class and issubclass(caller_class, target_class):
            inheritance_type = self._inheritance_analyzer.get_inheritance_type(caller_class, target_class)
            
            # For private inheritance, derived class can still access protected/public methods internally
            if inheritance_type == InheritanceType.PRIVATE:
                # Allow internal access to protected and public methods
                if access_level in [AccessLevel.PROTECTED, AccessLevel.PUBLIC]:
                    return True
                # Private methods are never accessible even with inheritance
                return False
            
            # For protected inheritance, allow access to protected and public methods
            elif inheritance_type == InheritanceType.PROTECTED:
                if access_level in [AccessLevel.PROTECTED, AccessLevel.PUBLIC]:
                    return True
                return False
                
            # For public inheritance (normal inheritance), follow normal protected rules
            elif inheritance_type == InheritanceType.PUBLIC:
                if access_level == AccessLevel.PUBLIC:
                    return True
                elif access_level == AccessLevel.PROTECTED:
                    return True
                return False
        
        # Get effective access level considering inheritance (for external access to derived objects)
        effective_access = self._inheritance_analyzer.get_inherited_access_level(
            actual_target_class, method_name, access_level, caller_class
        )
        
        return self._check_access_by_level(effective_access, target_class, caller_class, caller_info)
    
    def _check_friend_access(self, target_class: Type, access_level: AccessLevel, caller_info: CallerInfo) -> bool:
        """Unified friend access checking logic"""
        # Only check friends for private and protected access
        if access_level not in [AccessLevel.PRIVATE, AccessLevel.PROTECTED]:
            return False
        
        caller_class = caller_info.caller_class
        caller_method = caller_info.caller_method
        
        # Additional check: Look for friend attributes on the caller function itself
        # This handles cases where friend functions are wrapped in standard descriptors
        if caller_class and caller_method:
            try:
                caller_func = getattr(caller_class, caller_method, None)
                if caller_func:
                    # Extract the actual function from various descriptor types
                    actual_func = self._extract_function_from_descriptor(caller_func)
                    
                    # Check if the actual function has friend attributes
                    if (actual_func and 
                        hasattr(actual_func, '_limen_friend_target') and
                        hasattr(actual_func, '_limen_is_friend_method') and
                        actual_func._limen_friend_target is target_class):
                        return True
            except (AttributeError, TypeError):
                pass
        
        # If normal stack inspection didn't find a caller class, check thread-local staticmethod context
        if caller_class is None:
            try:
                from ..descriptors.static_method import _thread_local
                staticmethod_context = getattr(_thread_local, 'staticmethod_context', None)
                if staticmethod_context:
                    caller_class = staticmethod_context['caller_class']
                    caller_method = staticmethod_context['caller_method']
            except (ImportError, AttributeError):
                pass
        
        if not caller_method:
            return False
        
        # Check for friend function access (when caller_class is None)
        if caller_class is None:
            # Check if it's a friend function
            if self._friendship_manager.is_friend_function(target_class, caller_method):
                return True
            
            # Also check for staticmethod friend access (staticmethods have caller_class = None)
            if self._friendship_manager.is_staticmethod_friend(target_class, caller_method):
                return True
        else:
            # Check for friend method access (when caller_class is not None)
            if self._friendship_manager.is_friend_method(target_class, caller_class, caller_method):
                return True
            
            # Check for friend class access
            if self._friendship_manager.is_friend(target_class, caller_class):
                return True
        
        return False
    
    def _extract_function_from_descriptor(self, descriptor):
        """Extract the underlying function from various descriptor types"""
        from ..utils.descriptors import extract_function_from_descriptor
        return extract_function_from_descriptor(descriptor)

    def _check_access_by_level(self, access_level: AccessLevel, 
                              target_class: Type, caller_class: Type, caller_info: CallerInfo = None) -> bool:
        """Check access based on access level using unified strategy pattern"""
        # Unified access level checking strategy
        access_strategies = {
            AccessLevel.PUBLIC: lambda: True,
            AccessLevel.PRIVATE: lambda: self._check_private_access(target_class, caller_class, caller_info),
            AccessLevel.PROTECTED: lambda: self._check_protected_access(target_class, caller_class, caller_info)
        }
        
        strategy = access_strategies.get(access_level)
        return strategy() if strategy else False
    
    def _check_private_access(self, target_class: Type, caller_class: Type, caller_info: CallerInfo = None) -> bool:
        """Check private access (same class or same instance context - friends already checked in can_access)"""
        if not caller_class:
            return False
        
        # Same class access is always allowed
        if caller_class == target_class:
            return True
        
        # For inheritance scenarios: check if we're in a constructor chain or same instance context
        if caller_info and caller_info.caller_method:
            # Allow private access during constructor chains (__init__ methods)
            # This handles cases like super().__init__() calling private methods
            if caller_info.caller_method == '__init__':
                # In constructor context, allow access to private methods of any class
                # in the inheritance hierarchy of the same instance
                if issubclass(caller_class, target_class) or issubclass(target_class, caller_class):
                    return True
            
            # Also allow private access when the caller is any method within the same
            # inheritance hierarchy - this handles cases where a method in a derived class
            # calls a private method defined in the same class during complex inheritance scenarios
            if issubclass(caller_class, target_class):
                return True
        
        return False
    
    def _check_protected_access(self, target_class: Type, caller_class: Type, caller_info: CallerInfo = None) -> bool:
        """Check protected access (inheritance hierarchy - friends already checked in can_access)"""        
        if not caller_class:
            return False
        
        # Check inheritance access
        if issubclass(caller_class, target_class) or issubclass(target_class, caller_class):
            if issubclass(caller_class, target_class):
                inheritance_type = self._inheritance_analyzer.get_inheritance_type(
                    caller_class, target_class
                )
                return inheritance_type in [InheritanceType.PUBLIC, InheritanceType.PROTECTED]
            return True
        
        return False
