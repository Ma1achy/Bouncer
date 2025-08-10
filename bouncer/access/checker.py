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
        
        # Use instance class if provided for inheritance analysis
        actual_target_class = instance_class if instance_class else target_class
        
        # Same class access is always allowed
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
        
        return self._check_access_by_level(effective_access, target_class, caller_class)
    
    def _check_access_by_level(self, access_level: AccessLevel, 
                              target_class: Type, caller_class: Type) -> bool:
        """Check access based on access level"""
        if access_level == AccessLevel.PUBLIC:
            return True
        
        if access_level == AccessLevel.PRIVATE:
            return self._check_private_access(target_class, caller_class)
        
        if access_level == AccessLevel.PROTECTED:
            return self._check_protected_access(target_class, caller_class)
        
        return False
    
    def _check_private_access(self, target_class: Type, caller_class: Type) -> bool:
        """Check private access (same class or friends only)"""
        if not caller_class:
            return False
        
        # Check friend access
        if self._friendship_manager.is_friend(target_class, caller_class):
            return True
        
        # Private methods are only accessible from same class
        return False
    
    def _check_protected_access(self, target_class: Type, caller_class: Type) -> bool:
        """Check protected access (inheritance hierarchy or friends)"""
        if not caller_class:
            return False
        
        # Check friend access
        if self._friendship_manager.is_friend(target_class, caller_class):
            return True
        
        # Check inheritance access
        if issubclass(caller_class, target_class) or issubclass(target_class, caller_class):
            if issubclass(caller_class, target_class):
                inheritance_type = self._inheritance_analyzer.get_inheritance_type(
                    caller_class, target_class
                )
                return inheritance_type in [InheritanceType.PUBLIC, InheritanceType.PROTECTED]
            return True
        
        return False
