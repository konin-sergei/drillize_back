[query_title]
Поддерживает ли python множественное наследование?

[query_title]
Поддерживает ли python множественное наследование?

[answer_title]
Ответ №1

[answer_content]
Да, Python поддерживает множественное наследование. Это означает, что класс может наследовать функциональность от нескольких предков, путем указания их имен в скобках при определении класса. 

Например:
```python
class MyBaseClass1:
    pass

class MyBaseClass2:
    pass

class MyDerivedClass(MyBaseClass1, MyBaseClass2):
    pass
```
В этом случае MyDerivedClass является подклассом MyBaseClass1 и MyBaseClass2, и поэтому наследует их функциональность. Класс MyDerivedClass может использовать методы и атрибуты, определенные в MyBaseClass1 и MyBaseClass2.


Существует несколько способов объявления класса, который наследует от нескольких родительских классов, но один из распространенных способов - это просто указать несколько родительских классов в скобках при определении класса-потомка.

Cледующий код определяет класс MyClass, который наследует от классов Parent1 и Parent2:
```python
class Parent1:
    def method1(self):
        print("This is a method from Parent1")

class Parent2:
    def method2(self):
        print("This is a method from Parent2")

class MyClass(Parent1, Parent2):
    pass

obj = MyClass()
obj.method1() # outputs "This is a method from Parent1"
obj.method2() # outputs "This is a method from Parent2"
```
Приведенный выше код создает MyClass, который наследует свойства и методы как от класса Parent1, так и от класса Parent2. Вы можете вызвать методы как от Parent1, так и от Parent2 через объект MyClass.
