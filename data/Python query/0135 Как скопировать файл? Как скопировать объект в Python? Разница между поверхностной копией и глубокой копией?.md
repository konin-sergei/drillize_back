[query_title]
Как скопировать файл? Как скопировать объект в Python? Разница между поверхностной копией и глубокой копией?

[query_title]
Как скопировать файл? Как скопировать объект в Python? Разница между поверхностной копией и глубокой копией?

[answer_title]
Ответ №1

[answer_content]
В Python вы можете использовать модуль shutil для копирования файлов или директорий, а также метод copy() для копирования объектов.

Вот пример копирования файла с помощью shutil:
```py
import shutil

# path to the source file
src_file = '/path/to/source/file.txt'

# path to the destination directory
dst_dir = '/path/to/destination/directory/'

# copy the file to the destination directory
shutil.copy(src_file, dst_dir)
```
А вот пример копирования объекта с помощью copy():
```py
class MyClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b

# create an instance of MyClass
obj1 = MyClass(1, 2)

# make a copy of the object
obj2 = obj1.copy()

# modify the values of the copy
obj2.a = 3
obj2.b = 4

# print the values of the original object and its copy
print(obj1.a, obj1.b)  # Output: 1 2
print(obj2.a, obj2.b)  # Output: 3 4
```

Обратите внимание, что если объект содержит ссылки на другие объекты (например, списки или словари), они также останутся ссылками, и в скопированном объекте они будут указывать на те же самые объекты, что и в оригинальном объекте. Для полного копирования объекта, включая все вложенные объекты, можно использовать функцию deepcopy() из модуля copy.
