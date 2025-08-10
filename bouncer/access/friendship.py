"""
Manages friend relationships between classes
"""
from typing import Type, Dict, Set


class FriendshipManager:
    """Manages friend relationships between classes"""
    
    def __init__(self):
        self._relationships: Dict[str, Set[str]] = {}
    
    def register_friend(self, target_class: Type, friend_class: Type) -> None:
        """Register a friend relationship"""
        target_name = target_class.__name__
        friend_name = friend_class.__name__
        
        if target_name not in self._relationships:
            self._relationships[target_name] = set()
        
        self._relationships[target_name].add(friend_name)
    
    def is_friend(self, target_class: Type, caller_class: Type) -> bool:
        """Check if caller is a friend of target"""
        if not target_class or not caller_class:
            return False
            
        target_name = target_class.__name__
        caller_name = caller_class.__name__
        
        return (target_name in self._relationships and 
                caller_name in self._relationships[target_name])
    
    def get_friends_count(self) -> int:
        """Get total number of friend relationships"""
        return sum(len(friends) for friends in self._relationships.values())
    
    def get_relationships_count(self) -> int:
        """Get number of classes with friends"""
        return len(self._relationships)
    
    def clear(self) -> None:
        """Clear all friend relationships"""
        self._relationships.clear()
