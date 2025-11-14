[query_title]
Иерархия исключений Python?

[query_title]
Иерархия исключений Python?

[answer_title]
Ответ №1

[answer_content]
В Python все исключения являются экземплярами класса, производного от класса BaseException. В Python есть встроенная иерархия исключений, которая позволяет вам перехватывать определенные типы исключений. Вот неполный список некоторых классов исключений в Python, перечисленных в соответствии с их иерархией наследования:
```
BaseException
 +-- SystemExit
 +-- KeyboardInterrupt
 +-- Exception
      +-- StopIteration
      +-- ArithmeticError
      |    +-- ZeroDivisionError
      +-- AssertionError
      +-- AttributeError
      +-- BufferError
      +-- EOFError
      +-- ImportError
      +-- LookupError
      |    +-- IndexError
      |    +-- KeyError
      +-- NameError
      |    +-- UnboundLocalError
      +-- OSError
      |    +-- FileNotFoundError
      +-- ReferenceError
      +-- RuntimeError
      |    +-- NotImplementedError
      +-- SyntaxError
      +-- IndentationError
           +-- TabError

```
Это не исчерпывающий список всех встроенных классов исключений, но он охватывает некоторые важные. При обработке исключений с помощью блока try-except можно перехватить несколько исключений, указав кортеж классов исключений после ключевого слова exclude. Например:

```py
try:
    # некоторый код, который может вызывать различные исключения
except (ValueError, TypeError):
    # обрабатывать ValueError или TypeError
except OSError as e:
    # обрабатывать OSError, используя ключевое слово as, чтобы получить экземпляр исключения
except:
    # обрабатывать любое другое исключение
```
Вы также можете создавать свои собственные классы исключений, создавая подклассы любого существующего класса исключений или самого класса BaseException.
