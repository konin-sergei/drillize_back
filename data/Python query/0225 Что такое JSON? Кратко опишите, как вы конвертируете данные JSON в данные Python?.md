[query_title]
Что такое JSON? Кратко опишите, как вы конвертируете данные JSON в данные Python?

[query_title]
Что такое JSON? Кратко опишите, как вы конвертируете данные JSON в данные Python?

[answer_title]
Ответ №1

[answer_content]
JSON (JavaScript Object Notation) - это формат обмена данными, основанный на языке JavaScript. Он часто используется для передачи данных между веб-сервером и веб-браузером, но может быть использован в любом другом контексте, где необходима передача структурированных данных.

Для конвертации данных JSON в данные, можно использовать модуль json. Пример:
```py
import json

# JSON-строка
json_string = '{"name": "John Smith", "age": 35, "city": "New York"}'

# Конвертация JSON-строки в Python-объект
data = json.loads(json_string)

# Вывод данных Python
print(data)
```
Вывод:
```py
{'name': 'John Smith', 'age': 35, 'city': 'New York'}
```
Обратите внимание, что вы можете использовать метод json.dump() для записи Python объекта в файл в формате JSON.
```py
# Python-объект
data = {
    "name": "John Smith",
    "age": 35,
    "city": "New York"
}

# Записываем данные в файл в формате JSON
with open('data.json', 'w') as f:
    json.dump(data, f)
```
Этот пример создаст файл data.json со следующим содержимым:
```py
{"name": "John Smith", "age": 35, "city": "New York"}
```
