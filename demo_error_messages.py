from limen import private, protected, public, friend

class Base():
    @protected
    def protected_method(self):
        print("This is a protected method")

@protected
class Derived(Base):
    @private
    def public_method(self):
        self.protected_method()
        
obj = Derived()
obj.public_method()
obj.protected_method()  # This will raise an error since protected_method is not accessible outside the class