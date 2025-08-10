"""
Friend decorator implementation
"""
from typing import Type, Callable
from ..system import get_access_control_system


def friend(target_class: Type) -> Callable:
    """@friend decorator for establishing friend relationships"""
    def decorator(friend_class: Type) -> Type:
        access_control = get_access_control_system()
        access_control.register_friend(target_class, friend_class)
        access_control.emit_event('friendship_established', {
            'target_class': target_class.__name__,
            'friend_class': friend_class.__name__
        })
        return friend_class
    return decorator
