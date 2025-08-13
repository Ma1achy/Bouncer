#!/usr/bin/env python3
"""
Comprehensive test of enhanced error messages with scope information
"""
from limen import private, protected, public

class DatabaseService:
    @private
    def _internal_query(self):
        return "sensitive data"
    
    @protected 
    def _validate_access(self):
        return "validation result"
    
    @public
    def public_method(self):
        return "public data"

class UserService:
    def __init__(self, db):
        self.db = db
    
    def process_user_data(self):
        # This will fail - trying to access private method from another class
        return self.db._internal_query()

class AdminService(DatabaseService):
    def admin_operation(self):
        # This will fail - trying to access protected method from subclass in wrong context
        return self._validate_access()

def module_level_function():
    db = DatabaseService()
    # This will fail - module-level function accessing private method
    return db._internal_query()

# Test 1: Module-level access violation
print("=== Test 1: Module-level access ===")
try:
    db = DatabaseService()
    db._internal_query()
except Exception as e:
    print(f"Error: {e}")

# Test 2: Cross-class access violation  
print("\n=== Test 2: Cross-class access ===")
try:
    db = DatabaseService()
    user_service = UserService(db)
    user_service.process_user_data()
except Exception as e:
    print(f"Error: {e}")

# Test 3: Function-level access violation
print("\n=== Test 3: Function-level access ===")
try:
    module_level_function()
except Exception as e:
    print(f"Error: {e}")

# Test 4: Inheritance context violation
print("\n=== Test 4: Inheritance context ===")
try:
    admin = AdminService()
    admin.admin_operation()
except Exception as e:
    print(f"Error: {e}")
