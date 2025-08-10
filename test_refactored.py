"""
Simple test to verify the refactored bouncer system works
"""
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from bouncer_refactored import private, protected, public, friend
    print("Successfully imported refactored bouncer!")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class TestClass:
    def __init__(self):
        self._data = "test data"
    
    @private
    def _secret_method(self):
        return "secret"
    
    @protected
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value):
        self._data = value
    
    @public
    def public_method(self):
        return "public"

@friend(TestClass)
class FriendClass:
    def access_secret(self, obj):
        return obj._secret_method()

if __name__ == "__main__":
    print("Testing refactored bouncer system...")
    
    # Test basic functionality
    obj = TestClass()
    print(f"Public method: {obj.public_method()}")
    
    # Test property access (should work from same class context)
    print(f"Data property: {obj.data}")
    
    # Test friend access
    friend_obj = FriendClass()
    try:
        secret = friend_obj.access_secret(obj)
        print(f"Friend access: {secret}")
    except PermissionError as e:
        print(f"Friend access failed: {e}")
    
    # Test external access (should fail)
    try:
        external_secret = obj._secret_method()
        print(f"External access: {external_secret}")
    except PermissionError as e:
        print(f"External access blocked: {e}")
    
    print("Refactored bouncer system test completed!")
