[query_title]
Есть ли в Python оператор switch-case?

[query_title]
Есть ли в Python оператор switch-case?

[answer_title]
Ответ №1

[answer_content]
В Python нет прямого оператора switch-case, как в других языках программирования. Однако, начиная с версии Python 3.10, появилась возможность использовать оператор match-case, который является аналогом switch-case в других языках. Он позволяет проверять значения на соответствие определенным шаблонам и выполнять соответствующее действие в зависимости от того, какой шаблон соответствует значению. Пример использования оператора match-case:
```py
def process_value(value):
    match value:
        case 1:
            print("Value is 1")
        case 2:
            print("Value is 2")
        case _:
            print("Value is not 1 or 2")

process_value(1)  # output: Value is 1
process_value(3)  # output: Value is not 1 or 2
```
Оператор match-case доступен только в версии Python 3.10 и выше, поэтому если вы используете более старую версию Python, то нужно воспользоваться другими способами для решения задачи, например, использовать условные выражения if-elif-else или словари.
