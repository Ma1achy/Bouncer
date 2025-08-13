#!/usr/bin/env python3
"""
Simple test to check error message formatting
"""
from limen import protected

class TestClass:
    @protected
    def protected_method(self):
        return "protected data"

obj = TestClass()
try:
    obj.protected_method()  # This should fail
except Exception as e:
    print(f"Exception type: {type(e).__name__}")
    print(f"Exception module: {type(e).__module__}")
    print(f"Exception message: {e}")
    # Raise it again to see the traceback
    raise
