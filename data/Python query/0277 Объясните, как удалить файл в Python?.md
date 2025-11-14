[query_title]
Объясните, как удалить файл в Python?

[query_title]
Объясните, как удалить файл в Python?

[answer_title]
Ответ №1

[answer_content]
Чтобы удалить файл в Python, можно использовать метод os.remove() из модуля os.
```py
import os
os.remove('filename.txt') # замените filename.txt на имя вашего файла
```
Однако, убедитесь, что у вас есть необходимые разрешения на удаление файла.

Если вам нужно также удалить пустую директорию, то вы можете использовать os.rmdir(). Если директория не пуста, вы должны использовать shutil.rmtree() чтобы удалить её вместе с содержимым.
```py
import os
import shutil

# удаление директории если она пустая
os.rmdir('directory_name') # замените directory_name на имя вашей директории

# удаление директории со всем содержимым
shutil.rmtree('directory_name') # замените directory_name на имя вашей директории
```
