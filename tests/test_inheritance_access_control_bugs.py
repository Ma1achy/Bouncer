"""
Test cases to identify bugs in access control system for inheritance hierarchies.
These tests replicate the reported issues where @private methods are incorrectly
blocked even when called from within the same class that owns them.
"""
import pytest
from limen.decorators.access_decorators import private, protected, public
from limen.exceptions.limen_errors import PermissionDeniedError


class TestBasicInheritanceAccessControl:
    """Test basic inheritance scenarios with explicit decorators"""
    
    def test_private_method_call_within_same_class_explicit(self):
        """Test that @private methods can be called from within the same class"""
        
        class Base:
            @protected
            def _method(self):
                pass
        
        class Derived(Base):
            @private
            def __private_method(self):
                return "private_result"
            
            def public_method(self):
                # This should work - calling private method from within same class
                return self.__private_method()
        
        obj = Derived()
        result = obj.public_method()
        assert result == "private_result"
    
    def test_private_method_call_in_constructor_explicit(self):
        """Test that @private methods can be called from constructor of same class"""
        
        class Base:
            @protected
            def _method(self):
                pass
        
        class Derived(Base):
            def __init__(self):
                self.result = self.__private_method()  # Should work
            
            @private
            def __private_method(self):
                return "constructor_result"
        
        obj = Derived()
        assert obj.result == "constructor_result"
    
    def test_private_method_call_across_inheritance_levels_explicit(self):
        """Test private method calls in multi-level inheritance with strict C++ semantics"""
        
        class Base:
            @protected
            def _method(self):
                pass
        
        class Derived(Base):
            @private
            def __derived_private(self):
                return "derived_private"
            
            def get_private(self):
                return self.__derived_private()
        
        class SubDerived(Derived):
            def __init__(self):
                super().__init__()
                # In strict C++ semantics, derived classes cannot access private methods
                # of base classes, even through public methods
                with pytest.raises(PermissionDeniedError):
                    self.result = self.get_private()
        
        # Test that the base class can access its own private method
        derived_obj = Derived()
        assert derived_obj.get_private() == "derived_private"
        
        # Test that the inheritance restriction is enforced
        SubDerived()  # Should not raise an exception during construction


class TestImplicitPrivateDecorators:
    """Test scenarios with implicit @private decorators from inheritance decorators"""
    
    def test_implicit_private_method_call_within_same_class(self):
        """Test implicit @private methods can be called from within same class"""
        
        class Base:
            @protected
            def _method(self):
                pass
        
        @private(Base)
        class Derived(Base):
            def __init__(self):
                # This should work - calling implicit private method from within same class
                self.result = self.__another_method()
            
            # Implicit @private applied due to @private inheritance decorator
            def __another_method(self):
                return "implicit_private"
        
        obj = Derived()
        assert obj.result == "implicit_private"
    
    def test_implicit_private_with_super_call(self):
        """Test the exact scenario from the bug report"""
        
        class Base:
            @protected
            def _method(self):
                pass
        
        @private(Base)
        class Derived(Base):
            def __init__(self):
                self.result = self.__another_method()
            
            def __another_method(self):
                return "derived_result"
        
        class Wrapper(Derived):
            def __init__(self):
                # This should work - super().__init__() calls Derived's constructor
                # which internally calls Derived's private method
                super().__init__()
                self.wrapper_result = "wrapper"
        
        obj = Wrapper()
        assert obj.result == "derived_result"
        assert obj.wrapper_result == "wrapper"
    
    def test_exact_user_reported_case(self):
        """Test the exact case reported by the user (with syntax fixes)"""
        
        class Base:
            @protected
            def _method(self):
                pass

        @private(Base)
        class Derived(Base):
            def __init__(self):
                # throws permission error even though call to @private is within same class
                self.result = self.__another_method()
            
            # implicit @private applied due to @private inheritance decorator
            def __another_method(self):
                return "another_method_result"

        class Wrapper(Derived):
            def __init__(self):
                # throws permission error even though call to @private is within Derived class 
                # to Derived's @private method (not actually an external call)
                super().__init__()
                self.wrapper_status = "wrapper_created"
        
        # Both of these should work without permission errors
        derived_obj = Derived()
        assert derived_obj.result == "another_method_result"
        
        wrapper_obj = Wrapper()
        assert wrapper_obj.result == "another_method_result"
        assert wrapper_obj.wrapper_status == "wrapper_created"


class TestComplexInheritanceScenarios:
    """Test complex inheritance hierarchies with mixed access levels"""
    
    def test_multiple_inheritance_with_private_methods(self):
        """Test multiple inheritance scenarios with correct C++ semantics"""
        
        class Mixin:
            @private
            def __mixin_private(self):
                return "mixin_private"
            
            def get_mixin_private(self):
                return self.__mixin_private()
        
        class Base:
            @protected
            def _base_protected(self):
                return "base_protected"
        
        @private(Base)
        class Derived(Base, Mixin):
            def __init__(self):
                # This correctly fails - derived classes cannot access private 
                # methods of base classes, even through public methods
                with pytest.raises(PermissionDeniedError):
                    self.mixin_result = self.get_mixin_private()
                
                # This should work - calling own implicit private method
                self.derived_result = self.__derived_private()
            
            def __derived_private(self):
                return "derived_private"
        
        # Test that direct access to Mixin methods works from Mixin itself
        mixin_obj = Mixin()
        assert mixin_obj.get_mixin_private() == "mixin_private"
        
        # Test that derived class properly restricts access
        obj = Derived()
        assert obj.derived_result == "derived_private"
    
    def test_diamond_inheritance_private_access(self):
        """Test diamond inheritance pattern with strict C++ semantics"""
        
        class A:
            @private
            def __a_private(self):
                return "a_private"
            
            def get_a_private(self):
                return self.__a_private()
        
        class B(A):
            @private
            def __b_private(self):
                return "b_private"
            
            def get_b_private(self):
                return self.__b_private()
        
        class C(A):
            @private
            def __c_private(self):
                return "c_private"
            
            def get_c_private(self):
                return self.__c_private()
        
        class D(B, C):
            def __init__(self):
                # In strict C++ semantics, derived classes cannot access
                # private methods of base classes, even through public methods
                with pytest.raises(PermissionDeniedError):
                    self.a_result = self.get_a_private()
                with pytest.raises(PermissionDeniedError):
                    self.b_result = self.get_b_private()
                with pytest.raises(PermissionDeniedError):
                    self.c_result = self.get_c_private()
                
                # Only own private methods are accessible
                self.d_result = self.__d_private()
            
            @private
            def __d_private(self):
                return "d_private"
        
        # Test that each class can access its own private methods directly
        a_obj = A()
        assert a_obj.get_a_private() == "a_private"
        
        b_obj = B()
        assert b_obj.get_b_private() == "b_private"
        
        c_obj = C()
        assert c_obj.get_c_private() == "c_private"
        
        # Test strict C++ semantics in diamond inheritance
        obj = D()
        assert obj.d_result == "d_private"


class TestProtectedAccessInInheritance:
    """Test protected access across inheritance hierarchies"""
    
    def test_protected_method_access_in_derived_class(self):
        """Test that derived classes can access protected methods"""
        
        class Base:
            @protected
            def _protected_method(self):
                return "protected_result"
        
        class Derived(Base):
            def __init__(self):
                # Should work - derived class accessing parent's protected method
                self.result = self._protected_method()
        
        obj = Derived()
        assert obj.result == "protected_result"
    
    def test_protected_method_with_private_inheritance(self):
        """Test protected methods with private inheritance decorator"""
        
        class Base:
            @protected
            def _protected_method(self):
                return "protected_result"
        
        @private(Base)
        class Derived(Base):
            def __init__(self):
                # Should work - protected methods should still be accessible to derived classes
                self.result = self._protected_method()
                self.private_result = self.__private_method()
            
            def __private_method(self):
                return "private_result"
        
        obj = Derived()
        assert obj.result == "protected_result"
        assert obj.private_result == "private_result"


class TestEdgeCasesAndBoundaryConditions:
    """Test edge cases that might reveal access control bugs"""
    
    def test_private_method_calling_another_private_method(self):
        """Test private methods calling other private methods within same class"""
        
        class TestClass:
            @private
            def __private_a(self):
                # Private method calling another private method in same class
                return self.__private_b()
            
            @private
            def __private_b(self):
                return "private_b_result"
            
            def public_entry(self):
                return self.__private_a()
        
        obj = TestClass()
        result = obj.public_entry()
        assert result == "private_b_result"
    
    def test_private_method_in_nested_class_hierarchy(self):
        """Test deeply nested inheritance with strict C++ semantics"""
        
        class A:
            @private
            def __a_method(self):
                return "a"
            
            def get_a(self):
                return self.__a_method()
        
        class B(A):
            @private
            def __b_method(self):
                return "b"
            
            def get_b(self):
                return self.__b_method()
        
        class C(B):
            @private
            def __c_method(self):
                return "c"
            
            def get_c(self):
                return self.__c_method()
        
        class D(C):
            def __init__(self):
                # In strict C++ semantics, private methods of base classes
                # should not be accessible even through public methods
                # when called on derived class instances
                with pytest.raises(PermissionDeniedError):
                    self.a_result = self.get_a()
                with pytest.raises(PermissionDeniedError):
                    self.b_result = self.get_b()
                with pytest.raises(PermissionDeniedError):
                    self.c_result = self.get_c()
                
                # Only own private methods are accessible
                self.d_result = self.__d_method()
            
            @private
            def __d_method(self):
                return "d"
        
        # Test that each class can access its own private methods directly
        a_obj = A()
        assert a_obj.get_a() == "a"
        
        b_obj = B()
        assert b_obj.get_b() == "b"
        
        c_obj = C()
        assert c_obj.get_c() == "c"
        
        # Test the strict C++ inheritance scenario
        obj = D()
        assert obj.d_result == "d"
    
    def test_constructor_chaining_with_private_methods(self):
        """Test constructor chaining where each constructor calls private methods"""
        
        class A:
            def __init__(self):
                self.a_value = self.__a_private()
            
            @private
            def __a_private(self):
                return "a_private"
        
        class B(A):
            def __init__(self):
                super().__init__()
                self.b_value = self.__b_private()
            
            @private
            def __b_private(self):
                return "b_private"
        
        class C(B):
            def __init__(self):
                super().__init__()
                self.c_value = self.__c_private()
            
            @private
            def __c_private(self):
                return "c_private"
        
        obj = C()
        assert obj.a_value == "a_private"
        assert obj.b_value == "b_private"
        assert obj.c_value == "c_private"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
