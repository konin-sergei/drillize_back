[query_title]
Как отправить почту из скрипта Python?

[query_title]
Как отправить почту из скрипта Python?

[answer_title]
Ответ №1

[answer_content]
Для отправки электронной почты из скрипта Python можно использовать библиотеку smtplib. Вот простейший пример кода, отправляющий email с текстом:
```py
import smtplib

sender_email = "your_email@example.com"
receiver_email = "recipient_email@example.com"
message = "Привет от Питона!"

smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
smtp_server.starttls()
smtp_server.login(sender_email, "your_password")
smtp_server.sendmail(sender_email, receiver_email, message)
smtp_server.quit()
```
Замените "your_email@example.com" на свой электронный адрес отправителя, "recipient_email@example.com" на адрес получателя и "your_password" на пароль для входа в вашу учетную запись электронной почты. Также вы можете изменить содержимое переменной message. Обратите внимание, что для отправки почты через Gmail придется разрешить отправку писем из ненадежных приложений в настройках вашей учетной записи Google.
