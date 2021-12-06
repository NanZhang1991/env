
<font face="宋体" color=black size=10>Python开发规范</font>
[toc]


# 1. 命名规范

## 1.1. 变量和函数

使用小写字母命名变量和函数，并使用下划线分割单词，同时可以使用一个下划线前缀来命名类的私有成员变量，只用于标明, 外部类还是可以访问到这个变量

```python
popular_books_list = []
_books = []
```

对函数同样

```python
def get_data():
    ...

def _get_data():  #私有方法
    ...

def _path():   #防止该方法与python内置函数出现名称混淆
    ...
```

此外，需要明确具体函数的名称

类内部函数命名，用单下划线(_)开头（该函数可被继承访问）

类内私有函数命名，用双下划线(__)开头（该函数不可被继承访问）

对于传入用户ID来返回用户对象的函数，下述第一个函数名称模糊，不能确定输入参数id是何种类型，而第二种则明确是用户的id

```python
def get_user_info(id):
    ...

def get_user_by(user_id):
    ...
```

## 1.2. 类和异常名

使用大驼峰方法，内部类名前缀加下划线，异常名以Error作为后缀

```python
class EmployeePaychecks:
    ...

try:     
    pass   
except ValueError as result:     
    pass
```

## 1.3. 常量

全部使用大写字母来定义常量名

```python
MAX_OVERFLOW = 7
```

## 1.4. 函数和方法参数

遵循与变量和函数名相同的规则，使用小写的动宾短语并适当添加下划线增加可读性。例如：

```python
def open_file()

class Person():
    def _private_func():  #私有函数名前加下划线
        pass
```

单前导下划线仅用于不打算作为类的公共接口的内部方法。

双前导下划线表示类私有的名字，python 将这些名字和类名连接在一起。
如果类 Foo 有一个属性名为 __a, 它不能以 Foo.__a 访问，如果非要访问，还是可以通过 Foo._Foo__a 得到访问权。通常，双前导下划线应该只用来避免与类中的属性发生名字冲突。

## 1.5. 模块名

模块应该是不含下划线的，简短的，小写的名字。

不鼓励使用下划线主要考虑模块名是与文件夹相对应的，因此需要考虑文件系统的一些命名规则的，比如Unix系统对大小写敏感，而过长的文件名会影响其在 Windows\Mac\Dos 等系统中的正常使用。

## 1.6. 继承

始终要确定一个类中的方法和实例变量是否要被公开。同样，需要确定你的属性是否应为私有的。

私有与非公有的区别在于：前者永远不会被用在一个派生类中，而后者可能会。

私有属性必须有两个前导下划线，无后置下划线。非公有属性必须有一个前导下划线，无后置下划线。公共属性没有前导和后置下划线，除非它们与保留字冲突。

## 1.7. 全局变量

全部大写，多个单词用_下划线隔开，如需要阻止导入模块内的全局变量，可以加一个前导下划线，GLOBAL_VAR_NAME，_GLOBAL_VAL，常量和全局变量命名规范相同。

## 1.8. 命名风格

注意几个特殊点：

### 1.8.1. 单下划线作为前导

如：_single_begin，这是弱的内部使用标识，例如使用“from M import *”的时候不会被导入,在不想被导入的全局变量（以及内部函数和类）前面加一个下划线；

```python
#下划线前缀的含义是：以单个下划线开头的变量或方法仅供内部使用，但是程序不受影响
class Test:
   def __init__(self):
       self.foo = 11
       self._bar = 23

>>> t = Test()
>>> t._bar  #正常访问该变量
23

#与通配符导入不同，常规导入不受前导单个下划线命名约定的影响
>>> import my_module
>>> my_module._internal_func()
```

### 1.8.2. 单下划线作为结尾的

如：single_end_，一般用于防止python关键词冲突。有时候，一个变量的最合适的名称已经被一个关键字所占用。 因此，像class或def这样的名称不能用作Python中的变量名称。这时可以附加一个下划线来解决命名冲突：

```python
>>> def make_object(name, class):
SyntaxError: "invalid syntax"

>>> def make_object(name, class_):
...    pass
```

### 1.8.3. 双下划线前导

如：__double_begin，类私有名。双下划线前缀会导致Python解释器重写属性名称，以避免子类中的命名冲突。这也叫做名称修饰（name mangling） - 解释器更改变量的名称，以便在类被扩展的时候不容易产生冲突。例子如下所示：

```python
class Test:
   def __init__(self):
       self.foo = 11
       self._bar = 23
       self.__baz = 23

>>> t = Test()
>>> dir(t)
['_Test__baz', '__class__', '__delattr__', '__dict__', '__dir__',
'__doc__', '__eq__', '__format__', '__ge__', '__getattribute__',
'__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__',
'__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
'__setattr__', '__sizeof__', '__str__', '__subclasshook__',
'__weakref__', '_bar', 'foo']

#可看到__baz属性的名称变成_Test__baz，这就是Python解释器所做的名称修饰。 它这样做是为了防止变量在子类中被重写。

#下面扩建Test类的类，并尝试重写构造函数中添加的现有属性：
class ExtendedTest(Test):  
   def __init__(self):
       super().__init__()
       self.foo = 'overridden'
       self._bar = 'overridden'
       self.__baz = 'overridden'

>>> t2 = ExtendedTest()
>>> t2._bar
'overridden'
>>> t2.__baz
AttributeError: "'ExtendedTest' object has no attribute '__baz'"

#AttributeError是因为__baz变成_ExtendedTest__baz以防止意外修改
>>> dir(t2)
['_ExtendedTest__baz', '_Test__baz', '__class__', '__delattr__',
'__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__',
'__getattribute__', '__gt__', '__hash__', '__init__', '__le__',
'__lt__', '__module__', '__ne__', '__new__', '__reduce__',
'__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__',
'__subclasshook__', '__weakref__', '_bar', 'foo', 'get_vars']

#查看发现原来的t2._Test__baz还在
>>> t2._ExtendedTest__baz
'overridden'
>>> t2._Test__baz
42

#另一个例子
_MangledGlobal__mangled = 23

class MangledGlobal:
   def __method(self):
       return 42

   def test(self):
       return __mangled

>>> MangledGlobal().__method()#双下划线名称修饰对程序员是完全透明的
AttributeError: "'MangledMethod' object has no attribute '__method'"

>>> MangledGlobal().test() 
23
#Python解释器自动将名称__mangled扩展为_MangledGlobal__mangled，因为它以两个下划线字符开头。这表明名称修饰不是专门与类属性关联的。它适用于在类上下文中使用的两个下划线字符开头的任何名称。
```

### 1.8.4. 双下划线前导+结尾

如果一个名字同时以双下划线开始和结束，则不会应用名称修饰。由双下划线前缀和后缀包围的变量不会被Python解释器修改：

```python
class PrefixPostfixTest:
   def __init__(self):
       self.__bam__ = 42

>>> PrefixPostfixTest().__bam__
42

#但是，Python保留了有双前导和双末尾下划线的名称，用于特殊用途。 这样的例子有，__init__对象构造函数，或__call__ 使得一个对象可以被调用。可以用于触发某个特殊行为，如运算符重载(python通过这种特殊的命名方式来拦截操作符，以实现重载)
```

## 1.9. 应避免的名字

永远不要用：

1） 小写字母“l”（小写的“L”）、大写字母“O”和大写字母“I”（读音 eye）

作为单字符的变量名，因为不利于跟数字“0”和“1”很好的区分开来。
当要用小写字母“l”时，请用大写字母“L”代替。

2） 命名只能以字母或者_下划线开头，且不能包含空格

```python
#错误类名
class 4_Person():
  pass
#错误函数名
def 相加():
  pass
#错误添加空格
def 相 减():
  pass
```

3） 名字不能与关键字重合

```python
#错误函数名，与关键字and重合
def and():
    pass
```

## 1.10. 编写代码的建议

### 1.10.1. 更偏向使用join而不是内置的字符串连接符'+'

使用join时python对已经连接的字符串只分配一次内存，但是使用串连接符连接字符串时，python会为每一次连接字符串分配新的内存

### 1.10.2. 判断是否为none时考虑使用is和is not

```python
# val不能是dict或set，否则会被当做是false
if val：   
# 为了编写明确含义的代码，应该写成下述
if val is not None:
```

### 1.10.3. 更偏向使用is not而不是not...is

当你本意是"if x is not None"时，对写成"if x"要小心，因为例如当你测试一个默认为None的变量或参数是否被设置为其它值时，这个其它值可能是一个在布尔上下文中为假的值。

### 1.10.4. 绑定标识符时考虑使用函数而不是lambda表达式

可以在较大的表达式中使用lambda，这样不会影响代码可读性

```python
# 不要写
square = lambda x: x * x
# 而要写，有助于字符串表示和回溯
def square(val):
    return val * val
```

### 1.10.5. 与return语句保持一致

如果函数有返回值，确保任何执行此函数的地方都有返回值

```python
def multiply_number(num):
    if num > 0:
        return num * num
    else:
        return None
```

### 1.10.6. 更偏向使用"".startswith()和"".endswith()

当需要进行前缀和后缀的检查时，使用"".startswith()和"".endswith()而不是切片，可以让读者清楚这是在对字符串进行前后缀的检查

### 1.10.7. 比较类型时更偏向使用isinstance()方法而不是type()

如果传递的是特殊类型的数据结构（例如ordereddict的dict子类），type()会失败，而isinstance()会识别出是dict的子类

```python
# 不要
type(user_id) == dict:
# 而要
isinstance(user_id,dict):
```

### 1.10.8. 比较Boolean值

```python
# 不要
if is_empty = False
if is_empty == False
if is_empty is False
# 而要
is_empty = False
if is_empty：
```

### 1.10.9. 为上下文管理器编写显示代码

当使用with语句时，最好显示地编写不同函数处理不同于资源获取和释放的其他任何操作

### 1.10.10. 使用Lint工具格式化代码

Lint工具主要帮助解决：语法错误、结构化未使用的变量或者向函数传递正确的参数、指出违背PEP8规范的地方

最著名的是Flake8和Pylint

Pylint除了平常代码分析工具的作用之外，它提供了更多的功能：如检查一行代码的长度，变量名是否符合命名标准，一个声明过的接口是否被真正实现等等。

调用命令：pylint [options] module_or_package

### 1.10.11. 基于类的异常总是好过基于字符串的异常：

模块和包应该定义它们自己的域内特定的基异常类, 基类应该是内建的 Exception 类的子类。 还始终包含一个类的文档字符串。例如:

```python
1 class MessageError(Exception):
2 """Base class for errors in the email package."""
```

## 1.11. 使用文档字符串

文档字符串通常写在方法、类和模块的第一个语句，一个文档字符串是其对象的_doc_的特殊属性。

编写文档字符串的规则：
使用三重引号、三重引号中的字符串前后不应有任何空行、文档字符串中的语句因该使用句点(.)作为结束符。

注意：文档字符串的惯例是一个多行字符串，它的首行以大写字母开始，句号结尾。第一行是函数和类的简要描述，文档字符中的简要描述和摘要之间有一行空白

```python
#谷歌的文档字符串例子
"""Calling given url.

:Parameters：
    url(str):url address to call.

:Returns:
    dict:Response of the url api.
"""
```

### 1.11.1. 模块级文档字符串

应该关注该模块的目标，包括所有模块里的所有方法和类。应当放在import之前

```python
"""This module contains all of the network related requests. 
This module will check for all the exceptions while making the network 
calls and raise exceptions for any unknown exception.
Make sure that when you use this module,
you handle these exceptions in client code as:
NetworkError exception for network calls.
NetworkNotFound exception if network not found.
"""
import json
```

### 1.11.2. 类文档字符串

主要用于简述类的使用及其目标

```python
class Student:
    """Student class information.

    This class handle actions performed by a student.
    This class provides information about student full name, age, 
    roll-number and other information.
    Usage:
        import student
        student = student.Student()
        student.get_name()
        >>> 678998
   """
   def __init__(self):
       pass
```

### 1.11.3. 函数文档字符串

可以写在函数之前或之后，主要描述函数的作用

```python
def is_prime_number(number):
    """Check for prime number.

    Check the given number is prime number 
    or not by checking against all the numbers 
    less the square root of given number.

    :param number:Given number to check for prime
    :type number: int
    :return: True if number is prime otherwise False.
    :rtype: boolean
    """
```

### 1.11.4. 文档字符串工具

文档字符串工具通过将文档字符串转换为HTML格式的文档来帮助文档化python代码，且可以通过运行简单命令来自动更新文档。有Sphinx、Pycoo、Read the docs和Epydocs

## 1.12. 编写python的控制结构

### 1.12.1. 使用列表推导

建议使用列表推导而不是map和filter方法，其可读性更强且不需要额外的循环性能开销（循环需要每次将项追加到列表中，而列表推导不需要）。若在一个循环中需要做很多事情，则最好还是使用循环。

```python
aquare_num = map(lambda num:num**2,num_list)
aquare_num = [num**2 for num in num_list]
```

### 1.12.2. 不要使用复杂的列表推导

列表推导对于一个条件下最多两个循环是可行的，否则会影响代码的可读性。

### 1.12.3. 是否使用lambda

不能用lambda替换函数的使用。PEP8文档提到：始终使用def语句，而不是将lambda表达式直接绑定到名称的赋值语句

```python
# 推荐
def f(x):
    return 2*x
# 不推荐,使用赋值语句绑定lambda就不能嵌入到更大的表达式
f = lambda x: 2*x
```

### 1.12.4. 什么时候使用生成器和列表推导

它俩的主要区别是列表推导将数据保存在内存中，而生成器不是

在下列情形下使用列表推导：
1）当需要多次遍历列表时
2）当需要列出方法来处理生成器中不可用的数据时
3）当没有大量数据重复，且可以保存在内存中（内存足够）

### 1.12.5. 不要在循环中使用else

for和while循环后加一个else语句，以便在循环结束后执行一个额外的操作

```python
# for循环结束后执行else语句
for item in [1,2]:
    print("good")
else
    print("bad")

>>> good
>>> good
>>> good
>>> bad
```

### 1.12.6. python3的range函数

range类似xrange并且生成一个迭代器，range不将数据保存在内存中，是一个占用较小且相同内存量的不可变的可迭代对象。range可以切片且在处理数字时比列表快得多

## 1.13. 引发异常

在python中，异常是由内置模块处理的。异常帮助API和库的使用者了解代码的限制，以便他们在使用代码时也可以使用良好的错误机制。

### 1.13.1. 习惯引发异常

使用try…except，这样程序就不会因为异常而中断。try/except语句用来检测try语句块中的错误，从而让except语句捕获异常信息并处理。

```python
# 注意文档字符串需要缩进
def divison(dividend,divisor):
    """Perform arithmetic division."""
    try:
        return dividend/divisor
    except ZeroDivisionError as zero:
        raise ZeroDivisionError("Please provide greater than 0 value")   #主动抛出异常
```

如果调用者不处理divison(dividend,divisor)方法失败的情况，即使代码中有ZeroDivisionError，也会在发生异常时返回None

### 1.13.2. 使用finally处理异常

在python中finally块中代码总会被执行。finally关键字在处理异常时非常有用，无论是否发生异常，都可以使用finally来确保给关闭或释放文件或资源。

```python
#无论文件是否有可写权限，都会输出"Error: 没有找到文件或读取文件失败",确保即使在程序执行期间发生异常，也可以关闭文件。

try:
    fh = open("testfile", "w")
    fh.write("这是一个测试文件，用于测试异常!!")
finally:
    print("Error: 没有找到文件或读取文件失败")
```

### 1.13.3. 创建自己的异常类

需要确保在创建自己的异常类时，异常类具有良好的边界并且是可描述的。自定义异常类，定义时须继承Exception或Exception的子类，并且类名最好和抛出的异常有关，让人一目了然。

```python
class UserNotFoundError(Exception):
    """Raise the exception when user not found."""
    def _init_(self,message = None,errors = None):
        super()._init_(message)
        self.errors = errors

def get_user_info(user_obj):
    """Get user information from DB"""
    user = get_user_from_db(user_obj)
    if not user:
        raise UserNotFoundError(f"No user found of this id:{user_obj.id}")
```

### 1.13.4. 只处理特定的异常




# 2. 数据结构
## 2.1. 常用数据结构
### 2.1.1. 内置序列类型
容器序列list、tuple 和 collections.deque 这些序列能存放不同类型的数据。 
扁平序列str、bytes、bytearray、memoryview 和 array.array，这类序列只能容纳一种类型。
容器序列存放的是它们所包含的任意类型的对象的引用，而扁平序列里存放的是值而不是引用。
可变序列 list、bytearray、array.array、collections.deque 和 memoryview。 
不可变序列 tuple、str 和 bytes。
### 2.1.2. 散列表

散列表（Hash table，也叫哈希表），通过把关键值映射到表中一个位置来访问记录，以加快查找的速度。这个映射函数叫做散列函数，存放记录的数组叫做散列表。在 dict 的散列表当中，每个键值对都占用一个表元，每个表元都有两 个部分，一个是对键的引用，另一个是对值的引用。

Python 中set,dict都是基于哈希表的数据结构。

Python 调用内部的散列函数，将键（Key）作为参数进行转换，得到一个唯一的地址，然后将值（Value）存放到该地址中。键必须是可哈希的，换句话说就是要可以通过散列函数计算出唯一地址的。列表、字典、集合都不能做为键（Key）。而元组里边可以存放列表这类可变因素，只有当元组中只包括像数字和字符串这样的不可变元素时，才可以作为字典中有效的键（Key）。

![节点](https://media.giphy.com/media/mOk8ziZxYJdr75uG8q/giphy.gif)

### 2.1.3. 笛卡尔积
用列表推导可以生成两个或以上的可迭代类型的笛卡儿积。 笛卡儿积是一个列表，列表里的元素是由输入的可迭代类型的元素对构成的元组，因此笛卡儿积列表的长度等于输入变量的长度的乘积。
```python
colors = ['black', 'white'] 
sizes = ['S', 'M', 'L'] 
>>>tshirts = [(color, size) for color in colors for size in sizes] 
tshirts [('black', 'S'), ('black', 'M'), ('black', 'L'), ('white', 'S'), ('white', 'M'), ('white', 'L')]

for color in colors: 
    for size in sizes: 
        print((color, size)) 

>>>('black', 'S') ('black', 'M') ('black', 'L') ('white', 'S') ('white', 'M') ('white', 'L') 

tshirts = [(color, size) for size in sizes for color in colors] 
>>>tshirts 
[('black','S'), ('white','S'), ('black','M'), ('white','M'), ('black','L'), ('white','L')]
```



### 2.1.4. 谨慎使用列表，优先使用生成器
列表在存储大量数据序列时可能会产生内存泄漏。
生成器可以用于创建其他任何类型的序列，生成器背后遵守了迭代器协议。
迭代器在从数据库获取数据时非常有用，不像列表会把所有元素一次性加载到内存中，而是在每次for循环调用next方法的时候才返回该元素。
```python
def func(n):
    yield n*2

g = func(5)
>>> next(g)
10
```

### 2.1.5. 元组
元组可用作不可变的列表，还可以用于没有名段的记录。
#### 2.1.5.1. 把元组用作记录
元组其实是对数据的记录：元组中的每个元素都存放了记录中一个字段的数据，外加这个字段的位置。
```python
lax_coordinates = (33.9425, -118.408056) 
city, year, pop, chg, area = ('Tokyo', 2003, 32450, 0.66, 8014) 
traveler_ids = [('USA', '31195855'), ('BRA', 'CE342567'),('ESP', 'XDA205856')] for passport in sorted(traveler_ids):
    print('%s/%s' % passport) 
    
>>>BRA/CE342567 
   ESP/XDA205856 
   USA/31195855 

>>>for country, _ in traveler_ids:   #元组拆包
        print(country) 

>>>USA BRA ESP
```
#### 2.1.5.2. 元组拆包
可以使用 * 运算符把一个可迭代对象拆开作为函数的参数：
```python
def add(num1,num2):
    return num1+num2

t = (20, 8) 
add(*t) 
>>> 28
```
同时，用*来处理剩下的元素（函数用 *args 来获取不确定数量的参数）：
```python
a, b, *rest = range(5) 
>>>a, b, rest 
(0, 1, [2, 3, 4])
```
嵌套元组拆包：
```python
#把输入元组的最后一个元素拆包到由变量构成的元组里
for name, cc, pop, (latitude, longitude) in metro_areas: 
    if longitude <= 0: 
        print(fmt.format(name, latitude, longitude))
```

### 2.1.6. 使用namedtuple
元组作为记录来用的话，还是少了一个功能： 我们时常会需要给记录中的字段命名。namedtuple 函数的出现帮我们解决了这个问题。namedtuple是一个带有数据名称的元组。
collections.namedtuple函数可以用来构建一个带字段名的元组和一个有名字的类。
#### 2.1.6.1. 访问数据
创建一个不可变类：
```python
#创建一个具名元组需要两个参数，一个是类名，另一个是类的各个字段的名字。后者可以是由数个字符串组成的可迭代对象，或者是由空格分隔开的字段名组成的字符串。
Point = namedtuple('Point',['x','y','z'])
point = Point(x=3,y=4,z=5)
point.x
#用namedtuple构建的类的实例所消耗的内存跟元组是一样的，因为字段名都被存在对应的类里面。这个实例跟普通的对象实例比起来也要小一些，因为Python不会用 __dict__ 来存放这些实例的属性。
```
namedtuple通过名称访问而不是索引访问，使访问数据更加方便。namedtuple的字段名必须是字符串。

#### 2.1.6.2. 返回数据
将值封装到数据结构中，以此来提供上下文而不编写额外的代码
```python
#不使用namedtuple封装参数时：
def get_usr_info(user_obj)：
    user = get_data_from_db(user_obj)
    first_name = user['first_name']
    last_name = user['last_name;]
    age = user['age']
    return fisrt_name,last_name,age

def get_full_name(fisrt_name,last_name,age)：
    return first_name + last_name

fisrt_name,last_name,age = get_usr_info(user_obj)
full_name = get_full_name(fisrt_name,last_name,age)

#将user的名字和年龄值封装在user_info实例中
def get_usr_info(user_obj)：
    user = get_data_from_db(user_obj)
    UderInfo = namedtuple('UserInfo',['first_name','last_name','age'])
    user_info = UserInfo(first_name=user['first_name'],last_name=user['last_name'],age=user['age'])
    return user_info    #把fisrt_name,last_name,age封装到user_info中

def get_full_name(user_info)：
    return user_info.first_name + user_info.last_name

user_info = get_user_info(user_obj)
full_name = get_full_name(user_info)

```
user_info作为namedtuple给出了额外的上下文，而没有在函数get_usr_info中返回时显式设置，故使用namedtuple可使代码在长期运行状态下更具有可读性和维护性。

### 2.1.7. 对序列使用+和*
在使用拼接的过程中，两个被操作的序列都不会被修改，Python 会新建一个包含同样类型数据的序列来作为拼接的结果。
```python
#需要防止复制好的列表都指向同一个对象
weird_board = [['_'] * 3] * 3 
>>> weird_board 
[['_', '_', '_'], ['_', '_', '_'], ['_', '_', '_']] 
>>> weird_board[1][2] = 'O' 
weird_board [['_', '_', 'O'], ['_', '_', 'O'], ['_', '_', 'O']]

board = [] 
for i in range(3): 
    row=['_'] * 3 
    board.append(row) 

>>> board 
[['_', '_', '_'], ['_', '_', '_'], ['_', '_', '_']] 
>>> board[2][0] = 'X' 
>>> board 
[['_', '_', '_'], ['_', '_', '_'], ['X', '_', '_']]
```
使用python tutor网站可以展示赋值的整个过程。
![节点](https://media.giphy.com/media/D3cgYjApYofeq6jaCJ/giphy.gif)

### 2.1.8. list.sort方法和内置函数sorted
list.sort方法会就地排序列表，不会把原列表复制一份，同时会返回None。
与 list.sort 相反的是内置函数 sorted，它会新建一个列表作为返回值。这个方法可以接受任何形式的可迭代对象作为参数，甚至包括不可变序列或生成器，同时返回一个列表。
他们都有两个可选的关键字参数：
reverse：设为True时，被排序的序列里的元素会以降序输出
key：一个只有一个参数的函数，这个函数会被用在序列里的每一个元素上，所产生的结果将是排序算法依赖的对比关键字。比如说，在对一些字符串排序时，可以用 key=str.lower 来实现忽略大小写的排序，或者用 key=len 进行基于字符串长度的排序。
```python
fruits = ['grape', 'raspberry', 'apple', 'banana'] 
>>> sorted(fruits)
['apple', 'banana', 'grape', 'raspberry'] 
>>> fruits   #不修改原list
['grape', 'raspberry', 'apple', 'banana'] 

fruits.sort() 
>>> fruits   #修改原list，减少内存损耗
['apple', 'banana', 'grape', 'raspberry'] 
```

### 2.1.9. 用bisect来管理已排序的序列
bisect 模块包含两个主要函数，bisect 和 insort，两个函数都利用二分查找算法来在有序序列中查找或插入元素，故比使用for和if语句查找插入元素更加快速。
#### 2.1.9.1. 用bisect来搜索
bisect(haystack, needle) 在 haystack（干草垛）里搜索 needle（针）的位置，该位置满足的条件是，把 needle 插入这个位置之后，haystack 还能保持升序。
```python
#比较bisect和for循环查找的时间，明显可以看出bisect时间更少
%time
all_score = [33, 99, 77, 70, 89, 90, 100]
breakpoints=[60, 70, 80, 90,100]
grades='FDCBA'
final_score = []

for score in all_score:
    for i in range(len(breakpoints)):
        if score <= breakpoints[i] :
            final_score.append(grades[i])
            break
    
>>>CPU times: user 2 µs, sys: 0 ns, total: 2 µs
Wall time: 3.58 µs

%time
def grade(score, breakpoints=[60, 70, 80, 90], grades='FDCBA'): 
    i = bisect.bisect(breakpoints, score) 
    return grades[i] 


[grade(score) for score in [33, 99, 77, 70, 89, 90, 100]] 

>>>CPU times: user 1 µs, sys: 0 ns, total: 1 µs
Wall time: 2.86 µs

#另一个例子
import bisect
import sys

HAYSTACK = [1, 4, 5, 6, 8, 12, 15, 20, 21, 23, 23, 26, 29, 30]
NEEDLES = [0, 1, 2, 5, 8, 10, 22, 23, 29, 30, 31]
ROW_FMT = '{0:2d} @ {1:2d} {2}{0:<2d}'

for needle in reversed(NEEDLES):
    position = bisect.bisect(HAYSTACK, needle)
    offset = position * ' |'
    print(ROW_FMT.format(needle, position, offset))

>>>
31 @ 14  | | | | | | | | | | | | | |31
30 @ 14  | | | | | | | | | | | | | |30
29 @ 13  | | | | | | | | | | | | |29
23 @ 11  | | | | | | | | | | |23
22 @  9  | | | | | | | | |22
10 @  5  | | | | |10
 8 @  5  | | | | |8 
 5 @  3  | | |5 
 2 @  1  |2 
 1 @  1  |1 
 0 @  0 0 

#如果将bisect改成bisect_left，结果变成：
>>> 
31 @ 14  | | | | | | | | | | | | | |31
30 @ 13  | | | | | | | | | | | | |30
29 @ 12  | | | | | | | | | | | |29
23 @  9  | | | | | | | | |23
22 @  9  | | | | | | | | |22
10 @  5  | | | | |10
 8 @  4  | | | |8 
 5 @  2  | |5 
 2 @  1  |2 
 1 @  0 1 
 0 @  0 0 
```
bisect.bisect系列返回的是插入索引的位置，bisect 函数其实是bisect_right 函数的别名，后者还有个函数叫 bisect_left。它们的区别在于，bisect_left 返回的插入位置是原序列中跟被插入元素相等的元素的位置，也就是新元素会被放置于它相等的元素的前面，而bisect_right 返回的则是跟它相等的元素之后的位置。
#### 2.1.9.2. 用bisect.insort插入新元素
排序很耗时，因此在得到一个有序序列之后，我们最好能够保持它的有序。bisect.insort(seq, item) 把变量 item 插入到序列 seq 中，并能保持 seq 的升序顺序。
```python
import bisect 
import random 

SIZE=7
random.seed(1729) 
my_list = [] 
for i in range(SIZE): 
    new_item = random.randrange(SIZE*2) 
    bisect.insort(my_list, new_item) 
    print('%2d ->' % new_item, my_list)

>>> 
10 -> [10]
 0 -> [0, 10]
 6 -> [0, 6, 10]
 8 -> [0, 6, 8, 10]
 7 -> [0, 6, 7, 8, 10]
 2 -> [0, 2, 6, 7, 8, 10]
10 -> [0, 2, 6, 7, 8, 10, 10]
```

### 2.1.10. 使用zip处理列表
当有两个列表需要并行处理时，可使用Zip函数。zip() 函数用于将可迭代的对象作为参数，将对象中对应的元素打包成一个个元组，然后返回由这些元组组成的对象，这样做的好处是节约了不少的内存。因为zip产生的是生成器，可以按需生成数据，而不是直接将全部的数据生成，载入内存，故可以提高速度和节约内存的使用率，同时zip中的数据只能操作一次，内存就会释放。
```python
users = ['a','b']
salary = ['1','2']
users_salary = []
for usr_slr in zip(users,salary):
    users_salary.append(usr_slr)

>>> print(users_salary)
[('a', '1'), ('b', '2')]

#等同于

for index in range(len(users)):
    users_salary.append((users[index],salary[index]))
print(users_salary)

>>> [('a', '1'), ('b', '2')]

#list和tuple储存相同内容，但是占用内存大小不同
nums=['a',1,2]
tp=('a',1,2)
>>> nums.__sizeof__()
104
>>> tp.__sizeof__()
48

#list为了能够实时追踪内存的使用情况，当空间不足时以及分配额外空间，额外的多分配了内存，而且还需要存储指针，指向对应的元素。
l=[]
>>> l.__sizeof__()  
40

l.append('a')      #为了减小每次增加 / 删减操作时空间分配的开销，Python 每次分配空间时都会额外多分配一些
>>> l.__sizeof__()
72

l.append('h')  
>>> l.__sizeof__()
72
    
```


### 2.1.11. 字典及其有用的库
#### 2.1.11.1. collections
##### 2.1.11.1.1. Counter
该类型会给键准备一个整数计数器。每次更新一个键的时候 都会增加这个计数器。是dict的一个子类，是一个有序集合，其中元素储存为字典的键，计数储存为键的值。
有很多方法，其中most_common()用于返回最常见的元素及其个数。
```python
ct = collections.Counter('abracadabra') 
>>> ct 
Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1}) 

>>> ct.update('aaaaazzz') 
>>> ct 
Counter({'a': 10, 'z': 3, 'b': 2, 'r': 2, 'c': 1, 'd': 1}) 

>>> ct.most_common(2) 
[('a', 10), ('z', 3)]
```

##### 2.1.11.1.2. deque
双端队列（deque）具有从任一端添加和删除元素的功能。用于创建队列和栈。
利用 .append 和 .pop 方法，我们可以把列表当作栈或者队列来用，但是相关操作会很耗时。而collections.deque 类（双向队列）是一个线程安全、可以快速从两端添加或者删除元素的数据类型。
栈（Stack）是限定只能在表的一端进行插入和删除操作的线性表。队列（Queue）是限定只能在表的一端进行插入和在另一端进行删除操作的线性表。栈必须按"后进先出"的规则进行操作，而队列必须按"先进先出"的规则进行操作。
![节点](https://img-blog.csdnimg.cn/20190116210403793.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQzNTAzNzI0,size_16,color_FFFFFF,t_70
)
![节点](https://img-blog.csdnimg.cn/20190116213755279.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQzNTAzNzI0,size_16,color_FFFFFF,t_70)
deque有append(x)从右侧追加x，appendleft(x)从左侧追加x，clear()清除所有元素，pop()从右侧弹出元素等方法。
```python
from collections import deque

deq = deque('abcds')
deq.append('h')
>>> deque
deque(['a', 'b', 'c', 'd', 's', 'h'])

deq.appendleft('i')
>>> deque
deque(['i','a', 'b', 'c', 'd', 's', 'h'])
```


##### 2.1.11.1.3. defaultdict
可以为不存在的键提供默认值。
```python
#在实例化一个 defaultdict 的时候，需要给构造方法提供一个可调用对象，这个可调用对象会在 __getitem__ 碰到找不到的键 的时候被调用，让 __getitem__ 返回某种默认值。
from collections import defaultdict

colors = defaultdict(list) #用list的构造方法作为 default_factory 来创建一个 defaultdict。
colors['orange']  

>>> []

>>> colors
defaultdict(list, {'orange': []})
```
当colors找不到orange的键时，首先调用 list() 来建立一个新列表，然后把这个新列表作为值，'new-key' 作为它的键，放到 dd 中，最后返回这个列表的引用，而这个用来生成默认值的可调用对象存放在名为 default_factory 的实例属性里。当查询不到键值时，就会调用default_factory并为查询不到的键创造一个值。

##### 2.1.11.1.4. OrderedDict
可以按照特定顺序获取键,但是python 3.6之后的dict变为有序的了。
以前的字典只有一张简单的hash table，新的字典不仅有一张hash table，还有一张indices索引表加以辅助，于是便可以实现字典的有序。

插入值具体的实现过程：
1.通过hash函数对key进行hash，得到hash value；
2.将hash value和(len(indices)-1)做与操作，得到一个数字（index），这就是要插入的indices索引表中的位置；
3.得到index后，对应到indices的位置，但是此位置不是存的hash value，而是存序号，表示该值在entries中的位置；
4.若无冲突（序号不存在），则插入entries中的相应元素；
5.若序号存在，就出现哈希冲突，则会继续向下寻找空位置，一直到找到剩余空位为止。
```python
#代码实现：
my_dict = {}

my_dict["hello"] = "world"

indices = [None, None, None, None]
entries = [
    ["--", "--", "--"],
    ["--", "--", "--"],
    ["--", "--", "--"],
    ["--", "--", "--"]]

hash_value = hash('hello')  
index = hash_value & ( len(indices) - 1) 
print('hash_value=',hash_value,'index=',index)
#得到hash_value= 7165159075754429265 index= 1

# 找到indices的index为1的位置，并插入entries的长度
indices = [None, 0, None, None]
# 此时entries会插入这个元素
entries = [
    ["--", "--", "--"],
    [7165159075754429265, "hello", "world"],
    ["--", "--", "--"],
    ["--", "--", "--"]]
```
#### 2.1.11.2. 使用字典的switch语句
Python没有switch/case语句，因此有时候需要用很长的if...elif...else作为替代品。可以利用dict创建一个switch语句。
```python
#如果使用if...elif...else语句：
def calculator(x,o,y):
    if o == '+':
        return x+y
    elif o == '-':
        return x-y
    elif o == '*':
        return x*y
    else :
        return x/y
    
calculator(1,'/',2)

#如果使用字典的switch语句：
def add(x,y):
    return x+y

def dec(x,y):
    return x-y

def multi(x,y):
    return x*y

def div(x,y):
    return x/y

operater = {'+':add,'-':dec,'*':multi,'/':div}
def switch_calculator(x,o,y):
    return operater.get(o)(x,y)

switch_calculator(1,'+',2)

>>> 3 
```

#### 2.1.11.3. 合并两个字典
需要注意内存的使用和数据的丢失
```python
#在3.5之后的python中
dict_first = {'a':1}
dict_sec = {'b':2}

#关键字参数是一个由键值对组成的集合，允许通过变量名进行匹配，而不是位置
{**dict_first，**dict_sec}
>>>{'a':1,'b':2}
```


# 3. 函数和类

## 3.1. 函数

### 3.1.1. 编写小函数并返回生成器

首先编写实现功能的代码，当实现了功能后 再考虑将功能分解为多个函数，以减少代码中的异味。


```python
def get_certain_line():
    correct = []
    with open('test_file.txt',encoding='utf-8') as f:
        for line in f:
            if 'first' in line:
                correct.append(line)
    return correct

get_certain_line()       
```




    ['This is the first line.\n']




```python
def get_certain_line():
    correct = []
    for line in read_file():
        if 'first' in line:
            correct.append(line)
    return correct

def read_file():
    with open('test_file.txt',encoding='utf-8') as f:
        for line in f:
            yield line

get_certain_line() 
```




    ['This is the first line.\n']



上面代码使用了生成器来返回文件的行数据，可以防止由于文件大小的不确定导致的内存损耗。
生成器有用的两个主要原因：
1.生成器调用函数时，会立即返回迭代器而不是运行整个函数，可以在上面执行不同的操作，比如循环或转换为列表。完成后会自动调用内置函数next()，并返回到yield关键字的下一行继续执行read_file函数，使得代码更易于阅读和理解。
2.在列表或其他数据结构中，Python需要在返回之前将数据保存在内存中，如果数据太大，可能会导致内存损耗，而生成器不会。因此，当需要处理大量数据或事先不确定数据大小时，建议优先使用生成器。

### 3.1.2. 引发异常替代返回None

当代码出现问题时，如果只是返回None或者打印日志，可能会导致bug隐藏，因此尽量不要显式地返回None。


```python
def read_lines_for_python(file_name,file_type):
    if not file_name or file_type not in ('txt','html'):  #不能确定返回的None是由于文件格式不对还是文件没有python单词
        return None
    with open(file_name,'r') as f:
        for line in f:
            if 'python' in line:
                return 'found python'
            
print(read_lines_for_python('test_file.txt','txt'))

if not read_lines_for_python('file_without_python_name','pdf'):
    print('no correct file format or file name does not exist')
```

    None



```python
def read_lines_for_python(file_name,file_type):
    if not file_name or file_type not in ('txt','html'):
        raise ValueError('Not correct file format')
    if not file_name:
        raise IOError('File Not Found')
    with open(file_name,'r') as f:
        for line in f:
            if 'python' in line:
                return 'found python'

if not read_lines_for_python('file_without_python_name','pdf'):
    print('no correct file format or file name does not exist')
```


    ---------------------------------------------------------------------------

    ValueError                                Traceback (most recent call last)

    /tmp/ipykernel_9471/2850270351.py in <module>
          9                 return 'found python'
         10 
    ---> 11 if not read_lines_for_python('file_without_python_name','pdf'):
         12     print('no correct file format or file name does not exist')


    /tmp/ipykernel_9471/2850270351.py in read_lines_for_python(file_name, file_type)
          1 def read_lines_for_python(file_name,file_type):
          2     if not file_name or file_type not in ('txt','html'):
    ----> 3         raise ValueError('Not correct file format')
          4     if not file_name:
          5         raise IOError('File Not Found')


    ValueError: Not correct file format


### 3.1.3. 使用默认参数和关键字参数

建议对两个以上的函数参数使用关键字参数


```python
years = ['2021','2022']
areas = ['xiaan','beijing']
income = [100,200]
def calulate_all_income(years,*,areas,income):   #使用*可以强制关键字参数进入调用者函数中
    for year in years:
        for area in areas:
            all_income = income[0]+income[1]
    return all_income
            
    
calulate_all_income(years,areas=areas,income=income)
```




    300



### 3.1.4. 编写函数时需要防御

由于不能保证在编写代码时不会出错，需要在编写函数时采取一些措施以便在投入生产之前预防或暴露代码中的bug，或者有助于在生产中找到bug。将代码交付生产之前，可以通过日志记录和单元测试来提高代码质量。


#### 3.1.4.1. 日志记录

日志记录是 logging 模块用来满足所有需求信息的包。它们包含了需要记录日志的地方、变化的字符串、参数、请求的信息队列等信息。


```python
import logging
import os 
 
logging.basicConfig(filename=os.path.join(os.getcwd(),'log.txt'),level=logging.DEBUG)
logging.debug('debug message')
logging.info('info message')
logging.warning('warning message')
```

#### 3.1.4.2. 单元测试


```python
from unittest import TestCase
from my_sum import sum_list   #导入要测试的sum_list函数
import unittest

class TestSum(TestCase):   #创建一个测试类TestSum并且继承了TestCase
    def test_list_int(self):  #定义的每一个测试函数都是一个test case并且函数名必须以test开头
        data = [1, 2, 3]
        result = sum_list(data)
        self.assertEqual(result, 6)  #检测结果

    def test_list_float(self):
        data = [1.0, 2.0, 3.0]
        result = sum_list(data)
        self.assertEqual(result, 5)

unittest.main(argv=['ignored', '-v'], exit=False)
```

    test_list_float (__main__.TestSum) ... FAIL
    test_list_int (__main__.TestSum) ... ok
    
    ======================================================================
    FAIL: test_list_float (__main__.TestSum)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/tmp/ipykernel_8875/3331514767.py", line 14, in test_list_float
        self.assertEqual(result, 5)
    AssertionError: 6.0 != 5
    
    ----------------------------------------------------------------------
    Ran 2 tests in 0.001s
    
    FAILED (failures=1)





    <unittest.main.TestProgram at 0x7f8090132f70>



### 3.1.5. 注意lambda的使用

lambda函数是匿名函数，可以接受任意数量的参数且只有一个表达式。最适合需要小的功能且仅使用一次的地方，lambda的一种常见用法是将其设置为内置sorted()函数中的关键参数。但是其的滥用会导致降低代码的可读性和可维护性。

lambda的第一个误用是忽略了现有的内置函数


```python
number_tuples = [(4, 5, 7), (3, 1, 2), (9, 4, 1)] 
sorted(number_tuples, key=lambda x: max(x)) 

sorted(number_tuples, key=max) 
```




    [(3, 1, 2), (4, 5, 7), (9, 4, 1)]



lambda应该只使用一次，因此不要将lambda分配给变量，而应当使用def关键字来定义一个函数。同时由于lambda是匿名函数，当引发错误的时候很难显示功能名称。

高阶函数搭配lambda使用不当。map(),filter()和reduce()经常与lambda一起使用。其中，高阶函数是指可以通过将函数作为参数或通过返回函数来对其他函数进行操作的函数。


```python
numbers = [1, 2, 3, 5, 8]   
#返回平方列表
squares = list(map(lambda x: x * x, numbers)) 
squares = [x * x for x in numbers] 
squares
```




    [1, 4, 9, 25, 64]



## 3.2. 类

### 3.2.1. 类结构

1.类变量:
包含实例变量和类变量。实例变量用于每个实例的唯一数据，而类变量用于类的所有实例共享的属性和方法。


```python
class Dog:
    kind = '泰迪'   #类变量
    def __init__(self,name):
        self.name = name   #实例变量
```

2.__init__:类构造函数，包含了类的状态以及如何调用该类的信息。


3.python的特殊方法（python内置的特殊方法，如__call__等）：特殊方法更改类的默认行为或为类提供额外的功能（方法重写），将之放在顶部可以帮助记住该类独有的行为。


```python
class Dog:
    kind = '泰迪'   #类变量
    def __init__(self,name,age):
        self.name = name   #实例变量
        self.age = age
        
    def __str__(self):
        return ('name:'+self.name+'age:'+self.age)
    
dog1 = Dog('lily','10')
print(dog1)
```

    name:lilyage:10


4.类方法：Python类方法和实例方法相似，它最少也要包含一个参数，只不过类方法中通常将其命名为 cls，Python 会自动将类本身绑定给 cls 参数（注意，绑定的不是类对象）。也就是说在调用类方法时，无需显式为cls参数传参。同时使用@classmethod修饰符进行修饰。由于在调用类方法时，只需要将类型本身传递给类方法，因此，既可以通过类也可以通过实例来调用类方法，二者均不需要传参。


```python
class Dog:
    kind = '泰迪'   #类变量
    def __init__(self,name,age):
        self.name = name   #实例变量
        self.age = age
        
    def __str__(self):
        return ('name:'+self.name+' '+'age:'+self.age)
    
    @classmethod
    def price(cls):   #将类传给cls
        return cls.kind
    
dog1 = Dog('lily','10')
dog1.price()
```




    '泰迪'



5.静态方法：静态方法没有类似 self、cls 这样的特殊参数，因此 Python 解释器不会对它包含的参数做任何类或对象的绑定。因此类的静态方法中无法调用任何类属性和类方法，也无法修改类的状态。静态方法需要使用@staticmethod修饰。静态方法的调用，既可以使用类名，也可以使用类对象。


```python
class Dog:
    kind = '泰迪'   #类变量
    def __init__(self,name,age):
        self.name = name   #实例变量
        self.age = age
        
    def __str__(self):
        return ('name:'+self.name+'age:'+self.age)
    
    @classmethod
    def dog_kind(cls):   #将类传给cls
        return cls.kind
    
    @staticmethod
    def birth():
        return '2021'
    
dog1 = Dog('lily','10')
dog1.birth()
```




    '2021'



6.实例方法：实例方法最大的特点就是最少要包含一个 self 参数，用于绑定调用此方法的实例对象（Python 会自动完成绑定）。实例方法通常会用类对象直接调用，也可以用过类名调用，但是需要手动给self参数传值。


```python
class Dog:
    kind = '泰迪'   #类变量
    def __init__(self,name,age,gender):
        self.name = name   #实例变量
        self.age = age
        self.gender = gender
        
    def __str__(self):
        return ('name:'+self.name+'age:'+self.age)
    
    @classmethod
    def dog_kind(cls):   #将类传给cls
        return cls.kind
    
    @staticmethod
    def birth():
        return '2021'
    
    def dog_gender(self):
        print(self.gender)
        
a = Dog('a','1','boy')
a.dog_gender()
```

    boy


7.私有方法：类内部函数命名，单下划线（_）开头（该函数可被继承访问）类内私有函数命名，双下划线（_）开头（该函数不可被继承访问）


```python
class Dog:
    kind = '泰迪'   #类变量
    def __init__(self,name,age,gender):
        self.name = name   #实例变量
        self.age = age
        self.gender = gender
        
    def __str__(self):
        return ('name:'+self.name+'age:'+self.age)
    
    @classmethod
    def dog_kind(cls):   #将类传给cls
        return cls.kind
    
    @staticmethod
    def birth():
        return '2021'
    
    def dog_gender(self):
        print(self.gender)
        
    def _dog_name(self):
        return self.name
    
    def __dog_name(self):
        return self.name
        
a = Dog('a','1','boy')
a._dog_name()
a.__dog_name()
```


    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    /tmp/ipykernel_8258/3987392607.py in <module>
         28 a = Dog('a','1','boy')
         29 a._dog_name()
    ---> 30 a.__dog_name()
    

    AttributeError: 'Dog' object has no attribute '__dog_name'


### 3.2.2. 实例方法、类方法、静态方法的区别

这三种方法都是保存在类的内存中，调用者不同。

实例方法由对象调用，至少一个self参数，self代表对象的引用。
self指向当前的实例对象,所以只要该方法有self参数,在调用此方法的时候会先把这个对象的内存空间加载进来,以便在方法中使用该实例对象的属性或者方法

类方法由类调用，至少一个cls参数，并且需要装饰器@classmethod修饰
cls指向当前的类对象,类对象不等于实例对象,类对象和实例对象都有单独的内存空间存储,当调用一个含有@classmethod装饰的方法,则会先加载这个类的内存空间

静态方法由类调用，不需要参数，需要装饰器@staticmethod修饰
静态方法不不要使用实例对象的属性方法也不需要使用类对象的属性所有无论往静态方法中传一个self还是cls都会加载对应的资源,而静态方法又不使用,所有为了节省资源静态方法就应运而生.并且一直保存再来没有删除,尽管用到的次数很少.

### 3.2.3. 什么时候使用静态方法

静态方法不需要访问类的数据，但是不将它作为一个独立函数放在类外是因为当代码很多时，不易找到该类使用的函数，而若将之放在类中可以使得读者更容易将该函数与该类关联起来。

### 3.2.4. 继承抽象类

抽象有助于确保继承的类以预期的方式实现。
抽象类可以有抽象方法和普通方法，但没有具体实现其功能。所以说实例化该类是无意义的，因此抽象类定义是无法被实例化，只能被继承，且继承的子类必须实现该类的抽象方法。跟接口的定义有点类似。

在接口中使用抽象类的原因：
可以使用抽象来创建接口类



```python
class Dog:    #重复写方法，累赘
    def walk(self):
        pass
    def swim(self):
        pass
    def eat(self):
        pass
    
class Bird:
    def walk(self):
        pass
    def fly(self):
        pass
    def eat(self):
        pass
    
dog1 = Dog()
bird1 = Bird()
```


```python
from abc import ABCMeta,abstractmethod

class walk_feature(metaclass = ABCMeta): #指定这是一个抽象类
    @abstractmethod  #抽象方法
    def walk(self):
        pass         #抽象方法不包含任何可实现的代码，因此其函数体通常使用pass

class swim_feature(metaclass = ABCMeta): 
    @abstractmethod  
    def swim(self):
        pass     

class fly_feature(metaclass = ABCMeta): 
    @abstractmethod  
    def fly(self):
        pass 

class eat_feature(metaclass = ABCMeta): 
    @abstractmethod  
    def eat(self):
        pass

        
class Dog(walk_feature,swim_feature,eat_feature):  #要继承接口，需要把其中的每个方法全部实现，否则会报编译错误
    def walk(self):                                
        pass
    def swim(self):
        pass
    def eat(self):
        print('eat bones')
        
class Bird(walk_feature,fly_feature,eat_feature):
    def walk(self):
        pass
    def fly(self):
        pass
    def eat(self):
        pass

dog1 = Dog()
dog1.eat()
```

    eat bones


由于要继承接口，需要把其中的每个方法全部实现，否则会报编译错误，其实也可以直接定义一个class，其中的方法实现全部为pass，让子类重写这些函数。

### 3.2.5. 使用@classmethod来访问类的状态

类方法可以替代构造函数：通过传递一个类对象来创建多个构造函数。因为定义出来的类方法就能够在类对象实例化之前调用函数，就相当于多个构造函数。例如：当输入数值有多个类型时，使用@classmethod来装饰类型处理函数，就可以重构类。


```python
class A(object):
    bar = 1

    def func1(self):
        print('foo')

    @classmethod
    def func2(cls):
        print('func2')
        print(cls.bar)
        cls().func1()  # 调用 foo方法

A.func2()  #不需要实例化  通过@classmethod 进而使得cls代表这个类 直接调用类里面的方法和变量
```

    func2
    1
    foo



```python
class Data_test(object):
    day=0
    month=0
    year=0
    def __init__(self,year=0,month=0,day=0):
        self.day=day
        self.month=month
        self.year=year
 
    @classmethod
    def get_date(cls,data_as_string):  #类似一个接口，以便根据特定数据访问特定的类状态
        year,month,day=map(int,data_as_string.split('-'))
        date1=cls(year,month,day)
        #返回的是一个初始化后的类
        return date1
 
    def out_date(self):
        print('year :')
        print(self.year)
        print('month :')
        print(self.month)
        print('day :')
        print(self.day)
 
t=Data_test(2016,8,1)
t.out_date()

r=Data_test.get_date("2016-8-6")   
r.out_date()

#先调用get_date（）对字符串进行出来，然后才使用Data_test的构造函数初始化。
#这样的好处就是你以后重构类的时候不必要修改构造函数，只需要额外添加你要处理的函数，然后使用装饰符 @classmethod 就可以了。

```

    year :
    2016
    month :
    8
    day :
    6


一般来说，要使用某个类的方法，需要先实例化一个对象再调用方法。

而使用@staticmethod或@classmethod，就可以不需要实例化，直接类名.方法名()来调用。

这有利于组织代码，把某些应该属于某个类的函数给放到那个类里去，同时有利于命名空间的整洁。


既然@staticmethod和@classmethod都可以直接类名.方法名()来调用，那他们有什么区别呢

如果在@staticmethod中要调用到这个类的一些属性方法，只能直接类名.属性名或类名.方法名。
而@classmethod因为持有cls参数，可以来调用类的属性，类的方法，实例化对象等，避免硬编码。

### 3.2.6. 使用公有属性代替私有属性

使用前缀两个下划线可以防止子类意外覆盖继承的父类的属性，python解释器会自动进行名称改写，但是由于名称改写后名字变得复杂，大多人不喜欢，故约定一般使用单个下划线进行私有属性的命名，这种属性名不会被名称改写。


```python
class MyOtherObject(object):
    def __init__(self):
        self.__private_field = 71
 
    @classmethod
    def get_private_field_of_instance(cls, instance):  #想要在类外部访问类的私有属性，必须对应一个类方法
        return instance.__private_field
 
bar = MyOtherObject()
MyOtherObject.get_private_field_of_instance(bar)
```




    71




```python
class MyParentObject(object):
    def __init__(self):
        self.__private_field = 71
        
 
class MyChildObject(MyParentObject):
    def __init__(self):
        super().__init__()
        self.__private_field = 61
        
    def get_private_field(self):
        return self.__private_field
 
baz = MyChildObject()   #python解释器将__private_field转换成访问_MyChildObject__private_field
#baz.get_private_field()  #子类不可以访问父类的私有属性
print(baz.__dict__)
```

    {'_MyParentObject__private_field': 71, '_MyChildObject__private_field': 61}


大多数而言，应该让非公共名称以单下划线开头。但是如果代码涉及到子类，并且有些内部属性应该在子类中隐藏起来，那么才考虑使用双下划线方案。

## 3.3. 生成器和迭代器

### 3.3.1. 迭代器

序列式容器（列表、元组、字典和集合以及自定义的支持迭代的容器类对象）有一个共同的特性，它们都支持使用 for 循环遍历存储的元素，因此它们又称为迭代器。

可迭代对象通过调用内部的 __iter__ 方法返回一个实例化的迭代器对象（若对象没有实现 __iter__ 方法，但实现了 __getitem__ 方法，Python 会创建一个迭代器，尝试按顺序（从索引 0 开始）获取元素）；而迭代器要实现 __next__ 方法返回单个元素，此外还需要实现 __iter__ 方法返回迭代器本身。

若对象中实现了 __getitem__ 或者 __iter__ 方法，那么这个对象就是可迭代对象
若对象中实现了 __next__ 和 __iter__ 方法，那么这个对象就是迭代器

Python 从可迭代对象中获取迭代器，先使用iter()函数在迭代对象中获取迭代器，然后使用next()来获取下一个元素，关系如下图所示。

![Image](https://image-static.segmentfault.com/252/884/2528841056-92cb772437d0ede6_fix732)


```python
import re

RE_WORD = re.compile('\w+')

class Sentence:
    def __init__(self, text):
        self.text = text
        self.words = RE_WORD.findall(text)

    def __iter__(self):
        return SentenceIterator(self.words)  #返回一个实例化的迭代器


class SentenceIterator:
    def __init__(self, words):
        self.words = words
        self.index = 0

    def __next__(self):
        try:
            word = self.words[self.index]
            print('word',word)
        except IndexError:
            raise StopIteration()  #引发StopIteration异常，会自动退出循环
        self.index += 1
        return word

    def __iter__(self):  #迭代器不用再生成迭代器，故返回迭代器本身
        return self

for item in Sentence('abs'):  #每次执行for语句遍历可迭代对象时都生成了一个迭代器，遍历完后就废弃掉
    print(item)

#for item in SentenceIterator('abs'):  #该迭代器也可以使用for循环遍历
    #print(item)
```

    word abs
    abs


### 3.3.2. 生成器

生成器返回一个可迭代对象，但是一次只会生成一个对象，可以提高内存利用率。


```python
import re

RE_WORD = re.compile('\w+')

def Sentence(text):
    words = RE_WORD.findall(text)
    index = 0
    while index < len(words):
        index += 1
        yield words
    
for item in Sentence('abs'):
    print(item)
```

    ['abs']


### 3.3.3. yield关键字

调用一个使用了yield关键字的函数时，会返回一个生成器对象，在遇到yield关键字时，python会返回生成器提取的对象并暂停执行，直到提取了这个返回对象，之后就会继续执行yield后的代码，循环多次后直到生成器被耗尽，会抛出一个StopIteration异常，该异常会被for循环自动处理。


```python
def generate_numbers(nums):
    for item in range(nums):
        print('before yield')
        yield item
        print('after yield','item=',item)

numbers = generate_numbers(5)  #创建一个生成器对象
print(numbers)  

i = 0
for item in numbers:#第一次在for循环调用生成器对象时，遇到yield停止并返回循环中第一个值，当第二次被调用时，从yield关键字下一行开始执行。
    i += 1
    print(f'第{i}次被调用','item=',item)
```

    <generator object generate_numbers at 0x7f07403eb6d0>
    before yield
    第1次被调用 item= 0
    after yield item= 0
    before yield
    第2次被调用 item= 1
    after yield item= 1
    before yield
    第3次被调用 item= 2
    after yield item= 2
    before yield
    第4次被调用 item= 3
    after yield item= 3
    before yield
    第5次被调用 item= 4
    after yield item= 4


### 3.3.4. yield from

主要用途是拼接可迭代对象，从其他生成器返回一个值，可以省略for循环。


```python
def chain(*iterables):
    for it in iterables:
        for i in it:
            yield i

s = 'ABC'
t = tuple(range(3))
list(chain(s, t))
```




    ['A', 'B', 'C', 0, 1, 2]




```python
def chain(*iterables):
    for it in iterables:
        yield from it  #yield from x 表达式调用 iter(x)，从中获取迭代器
        
s = 'ABC'
t = tuple(range(3))
list(chain(s, t))
```




    ['A', 'B', 'C', 0, 1, 2]



yield from 的另一个功能是打开双向通道，把最外层的调用方与最内层的子生成器连接起来，这样二者可以直接发送和产出值，还可以直接传入异常，而不用在位于中间的协程中添加大量处理异常的样板代码。

yield from允许一个生成器将其部分操作委派给另一个生成器。其产生的主要动力在于使生成器能够很容易分为多个拥有send和throw方法的子生成器，像一个大函数可以分为多个子函数一样简单


```python
# 生成器的嵌套

# 子生成器
def average_gen():
    total = 0
    count = 0
    average = 0
    while True:
        new_num = yield average   #当返回average后，接收send值赋给new_num
        print('average',average)
        print('new_num',new_num)
        count += 1
        total += new_num
        average = total/count

# 委托生成器：在调用方与子生成器之间建立一个双向通道。
def proxy_gen():
    while True:
        yield from average_gen()

# 调用方：调用方可以通过send()直接发送消息给子生成器，而子生成器yield的值，也是直接返回给调用方。
def main():
    calc_average = proxy_gen()
    next(calc_average)           
    print(calc_average.send(10))   
    print(calc_average.send(20))  
    print(calc_average.send(30))  #传入30，那返回平均数(10+20+30)/3=20
    
main()
```

    average 0
    new_num 10
    10.0
    average 10.0
    new_num 20
    15.0
    average 15.0
    new_num 30
    20.0


使用委托生成器可以帮助处理异常，yield可以帮助自动捕获StopIteration异常，否则需要手动捕获。


```python
class SpamException(Exception):
    pass

# 子生成器
def average_gen():
    total = 0
    count = 0
    average = 0
    while True:
        new_num = yield average
        count += 1
        total += new_num
        average = total/count
        print('average:',average)
        

# 委托生成器
def proxy_gen(average_gen):
    average_gen.send(None)   #激活子生成器，使其可以开始接受数据
    while True:
        try:
            try:
                x = (yield)   # x接收send传进的数据
                #print('x',x)
            except Exception as e:   # 捕获异常
                average_gen.throw(e)
            else:
                average_gen.send(x)
        except StopIteration:    
            pass

# 调用方
def main():
    calc_average = proxy_gen(average_gen())
    #calc_average.send(None)      #激活委托生成器 
    next(calc_average) 
    calc_average.send(10)
    calc_average.send(20)  
    calc_average.send(30)  
    calc_average.throw(SpamException)
    
main()
```

    average: 10.0
    average: 15.0
    average: 20.0



    ---------------------------------------------------------------------------

    SpamException                             Traceback (most recent call last)

    /tmp/ipykernel_9471/2589033206.py in <module>
         40     calc_average.throw(SpamException)
         41 
    ---> 42 main()
    

    /tmp/ipykernel_9471/2589033206.py in main()
         38     calc_average.send(20)
         39     calc_average.send(30)
    ---> 40     calc_average.throw(SpamException)
         41 
         42 main()


    /tmp/ipykernel_9471/2589033206.py in proxy_gen(average_gen)
         24                 #print('x',x)
         25             except Exception as e:   # 捕获异常
    ---> 26                 average_gen.throw(e)
         27             else:
         28                 average_gen.send(x)


    /tmp/ipykernel_9471/2589033206.py in average_gen()
          8     average = 0
          9     while True:
    ---> 10         new_num = yield average
         11         count += 1
         12         total += new_num


    /tmp/ipykernel_9471/2589033206.py in proxy_gen(average_gen)
         21         try:
         22             try:
    ---> 23                 x = (yield)   # x接收send传进的数据
         24                 #print('x',x)
         25             except Exception as e:   # 捕获异常


    SpamException: 


### 3.3.5. 使用itertools

combinations:返回可迭代对象中所有长度为r的子序列,若r为None，则默认为这个可迭代对象的长度。


```python
from itertools import combinations
print(list(combinations(['1','2','3'],2)))
```

    [('1', '2'), ('1', '3'), ('2', '3')]


permutations：返回可迭代对象中所有长度为r的全排列子序列，若r为None，则默认为这个可迭代对象的长度。


```python
from itertools import permutations
print(list(permutations(['1','2','3'],2)))
```

    [('1', '2'), ('1', '3'), ('2', '1'), ('2', '3'), ('3', '1'), ('3', '2')]


count():是一个迭代器，返回从start开始step为步长的数字序列


```python
import itertools 

for num in itertools.count(1,4):
    if num > 24:
        break
    print(num)
```

    1
    5
    9
    13
    17
    21


### 3.3.6. iter函数的另一个用法

除了帮助可迭代对象获取迭代器，iter函数有另一个用法：传入两个参数，使用常规函数或任何可调用的对象创建迭代器。第一个参数必须是可调用的对象，用于不断调用并产出各个值，第二个参数是一个标记值，当可调用对象返回这个值时，触发迭代器抛出异常StopIteration，并且不返回该值。


```python
from random import randint
def random_numbers():
        return randint(1,6)

number_iter = iter(random_numbers,3)
print(number_iter)

for item in number_iter:
    print(item)
```

    <callable_iterator object at 0x7f0722e4efa0>
    6
    1

# 4. 循环import问题
```python
b.py
from a import A
class B:
  def __init__(self):
    self.a = A()  #creates instances of class A

a.py
from b import B
class A:
  def __init__(self, ref):
    assert isinstance(ref, B)
    self.ref = ref
```
```
import a
a = a.A(1)
>>>
ImportError: cannot import name 'b' from partially initialized module 'B' (most likely due to a circular import)
```
1 首次导入，a先进入sys模块的module表
2 然后执行from b import B这句
3 b首次导入，进入sys的module表
4 从b.py的第一句开始，执行from a import A这句，由于a已经在表中，略过，然后执行类B中A类的实例化，这时候a.py还没执行到给A类的构造的地方，所以导致异常。
```python
#修改如下：
class A:
    def __init__(self, ref):
        from b import B
        assert isinstance(ref, B)
        self.ref = ref
```
只要循环引入的模块是在函数中引用的（导致延迟导入），而不是在定义的阶段立即使用，循环引用就是可以正常使用的。这时，由于推迟了module b的导入，使得module b中module a的导入完成，故不会导致出现循环导入的情况。
需要注意的是：
from import创建到模块内部对象的引用，它的前提是import要成功；import创建到模块本身的引用，如果出现循环引用，由于import进来的模块可能还没有加载完成，导致from import查找不到相应对象。