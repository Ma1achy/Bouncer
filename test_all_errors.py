#!/usr/bin/env python3
"""
Test script to check different error message formats
"""
from limen import private, protected

def test_decorator_conflict():
    """Test conflicting decorators"""
    print("=== Testing Decorator Conflict ===")
    try:
        class TestClass:
            @private
            @protected  # This should cause a conflict
            def conflicted_method(self):
                return "conflict"
    except Exception as e:
        print(f"Exception: {type(e).__name__}")
        print(f"Message: {e}")
        print()

def test_decorator_usage_error():
    """Test decorator usage error"""
    print("=== Testing Decorator Usage Error ===")
    try:
        # Try to apply decorator to module-level function
        @private
        def module_function():
            return "module level"
        
        module_function()
    except Exception as e:
        print(f"Exception: {type(e).__name__}")
        print(f"Message: {e}")
        print()

def test_bare_class_decorator():
    """Test bare class decorator error"""
    print("=== Testing Bare Class Decorator ===")
    try:
        @protected  # Should require arguments for inheritance
        class BadClass:
            pass
    except Exception as e:
        print(f"Exception: {type(e).__name__}")
        print(f"Message: {e}")
        print()

def test_permission_denied():
    """Test permission denied with scope info"""
    print("=== Testing Permission Denied ===")
    try:
        class SecretClass:
            @private
            def secret_method(self):
                return "secret"
        
        class AccessorClass:
            def try_access(self, obj):
                return obj.secret_method()  # Should fail
        
        secret = SecretClass()
        accessor = AccessorClass()
        accessor.try_access(secret)
    except Exception as e:
        print(f"Exception: {type(e).__name__}")
        print(f"Message: {e}")
        print()

if __name__ == "__main__":
    test_decorator_conflict()
    test_decorator_usage_error()
    test_bare_class_decorator()
    test_permission_denied()
