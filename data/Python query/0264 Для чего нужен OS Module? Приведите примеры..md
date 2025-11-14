[query_title]
Для чего нужен OS Module? Приведите примеры.

[query_title]
Для чего нужен OS Module? Приведите примеры.

[answer_title]
Ответ №1

[answer_content]
Модуль OS - это модуль в Python, который предоставляет множество функций для работы с операционной системой. Он позволяет выполнять такие действия, как создание, удаление и переименование файлов и папок, получение информации о файлах и папках, работа с переменными окружения и многое другое.

Вот несколько примеров использования модуля OS:

+ Получение текущей директории
```py
import os

current_directory = os.getcwd()
print("Current directory:", current_directory)
```
+ Создание новой папки
```py
import os

new_folder = os.path.join(os.getcwd(), "new_folder")
os.mkdir(new_folder)
print("New folder created!")
```
+ Получение списка файлов в директории
```py
import os

directory = os.getcwd()
file_list = os.listdir(directory)
print("Files in", directory, ":", file_list)
```
+ Удаление файла

```py
import os

file_path_to_delete = "path/to/file.txt"
os.remove(file_path_to_delete)
```
+ Переименование файла
```py
import os

old_file_name = "old_name.txt"
new_file_name = "new_name.txt"

os.rename(old_file_name, new_file_name)
```
+ Запуск внешней программы:
```py
import os

os.system("notepad.exe")

```


+ Проверка существования файла или директории:
```py
import os
if os.path.exists('path/to/file_or_dir'):
    print('File or dir exists')
else:
    print('File or dir does not exist')

```
+ Обход всех файлов в директории и ее поддиректориях:
```py
import os
for root, dirs, files in os.walk('/path/to/dir'):
    for file in files:
        file_path = os.path.join(root, file)
        print(file_path)

```
