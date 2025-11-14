[query_title]
Как получить доступ к файлу на Linux-сервере с помощью Python?

[query_title]
Как получить доступ к файлу на Linux-сервере с помощью Python?

[answer_title]
Ответ №1

[answer_content]
Для получения доступа к файлу на Linux-сервере с помощью Python можно использовать модуль paramiko. Этот модуль позволяет создавать SSH-соединения с удаленными серверами и выполнять на них команды, включая работу с файлами.

Вот простой пример, который показывает, как прочитать содержимое файла с помощью модуля paramiko:
```py
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('hostname', username='username', password='password')
stdin, stdout, stderr = ssh.exec_command('cat /path/to/file.txt')
print(stdout.read().decode())
ssh.close()
```
В этом примере мы создаем SSH-соединение с удаленным сервером, указываем имя пользователя и пароль, и выполняем команду 'cat /path/to/file.txt', которая выводит содержимое файла на экран. Затем мы просто выводим результат в консоль.

Кроме того, вы можете использовать SCP (Secure Copy), чтобы скопировать файл с сервера на локальную машину:
```py
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('hostname', username='username', password='password')

scp = ssh.open_sftp()
scp.get('/path/to/remote/file', '/path/to/local/file')
scp.close()

ssh.close()
```
В этом примере мы подключаемся к удаленному серверу, создаем объект SCP, запрашиваем файл и копируем его на локальную машину.

Оба примера использования модуля paramiko требуют установки этого модуля на вашей системе:
```bash
pip install paramiko
```
