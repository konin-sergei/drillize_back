[query_title]
Что используется для создания строки Unicode в Python?

[query_title]
Что используется для создания строки Unicode в Python?

[answer_title]
Ответ №1

[answer_content]
Для создания строки Unicode в Python можно использовать префикс "u". Например:
```py
unicode_str = u"Это строка Unicode"
```
Однако, начиная с версии Python 3.x, все строки по умолчанию являются "Unicode strings", так что префикс "u" больше не является необходимым. Просто использование двойных кавычек для создания строки будет создавать строку Unicode:
```py
unicode_str = "Это строка Unicode"
```
