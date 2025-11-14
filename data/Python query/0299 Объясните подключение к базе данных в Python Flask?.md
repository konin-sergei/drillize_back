[query_title]
Объясните подключение к базе данных в Python Flask?

[query_title]
Объясните подключение к базе данных в Python Flask?

[answer_title]
Ответ №1

[answer_content]
Для подключения к базе данных в Flask можно использовать библиотеку SQLAlchemy. Вот пример кода, демонстрирующий подключение к базе данных SQLite:
```py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()
```
В этом примере мы создаем объект приложения Flask, затем устанавливаем настройку SQLALCHEMY_DATABASE_URI, которая определяет, какую базу данных использовать (в этом случае мы используем SQLite). Мы также создаем экземпляр класса SQLAlchemy, который мы будем использовать для работы с базой данных.

Затем мы создаем модель базы данных User, которая содержит имя пользователя. Обратите внимание, что эта модель является подклассом db.Model, который является частью SQLAlchemy. Это означает, что SQLAlchemy сможет выполнить миграции базы данных и создать таблицу для этой модели.

Наконец, мы запускаем приложение Flask и можем использовать модель пользователя, чтобы сохранять данные в базе данных.

Это был пример простого подключения к базе данных SQLite в Flask, но SQLAlchemy также поддерживает другие базы данных, такие как PostgreSQL, MySQL и другие.
