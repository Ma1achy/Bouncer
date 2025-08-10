"""
Pytest configuration and fixtures for C++ semantics testing
"""
import pytest
import sys
import os

# Add parent directory to path for testing the refactored bouncer
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from bouncer_refactored import reset_system

@pytest.fixture(autouse=True)
def reset_bouncer_system():
    """Reset bouncer system before each test"""
    reset_system()
    yield
    reset_system()

@pytest.fixture
def sample_classes():
    """Provide sample classes for testing"""
    from bouncer_refactored import private, protected, public
    
    class Base:
        @private
        def private_method(self):
            return "private_method_result"
        
        @protected
        def protected_method(self):
            return "protected_method_result"
        
        def public_method(self):
            return "public_method_result"
        
        @private
        @staticmethod
        def private_static():
            return "private_static_result"
        
        @protected
        @staticmethod
        def protected_static():
            return "protected_static_result"
        
        @private
        @classmethod
        def private_class(cls):
            return f"private_class_result_{cls.__name__}"
        
        @protected
        @classmethod
        def protected_class(cls):
            return f"protected_class_result_{cls.__name__}"
        
        @private
        @property
        def private_prop(self):
            return "private_prop_result"
        
        def call_private_methods(self):
            """Method to test same-class access to private methods"""
            return {
                'private_method': self.private_method(),
                'private_static': self.private_static(),
                'private_class': self.private_class(),
                'private_prop': self.private_prop
            }
        
        def call_protected_method(self):
            """Method to test same-class access to protected methods"""
            return self.protected_method()
    
    class Derived(Base):
        def try_access_base_private(self):
            """Try to access private methods from base class (should be blocked)"""
            results = {}
            
            try:
                results['private_method'] = self.private_method()
            except PermissionError:
                results['private_method'] = 'BLOCKED'
            
            try:
                results['private_static'] = self.private_static()
            except PermissionError:
                results['private_static'] = 'BLOCKED'
            
            try:
                results['private_class'] = self.private_class()
            except PermissionError:
                results['private_class'] = 'BLOCKED'
            
            try:
                results['private_prop'] = self.private_prop
            except PermissionError:
                results['private_prop'] = 'BLOCKED'
            
            return results
        
        def try_access_base_protected(self):
            """Try to access protected methods from base class (should work)"""
            return {
                'protected_method': self.protected_method(),
                'protected_static': self.protected_static(),
                'protected_class': self.protected_class()
            }
    
    class Unrelated:
        def access_other_public(self, other):
            """Access public methods of another object"""
            return other.public_method()
    
    return {
        'Base': Base,
        'Derived': Derived,
        'Unrelated': Unrelated
    }
