# Deploy local
#set -x

LOCAL_DIR="/my/src/drillize_back"
REMOTE_DIR="/var/www/drillize_back"

# Загружаем переменные окружения
source "${LOCAL_DIR}/deploy/.env.deploy" || { echo "Failed to load .env.deploy"; exit 1; }

# Проверяем, что все необходимые переменные заданы
: "${SSH_PWD:?Variable not set}"
: "${SSH_USER:?Variable not set}"
: "${SSH_IP:?Variable not set}"

# Копируем .env файл на сервер
sshpass -p "$SSH_PWD" scp ${LOCAL_DIR}/.env.prod "$SSH_USER@$SSH_IP:${REMOTE_DIR}/.env" || { echo "Failed to copy .env file"; exit 1; }

# Переходим в директорию
cd ${LOCAL_DIR} || { echo "Directory ${LOCAL_DIR} not found"; exit 1; }

# Добавляем изменения в git и отправляем их
git add . && git commit -m "Change $(date "+%d-%m-%Y %H:%M:%S")" && git push || { echo "Git commit or push failed"; exit 1; }

sshpass -p $SSH_PWD ssh $SSH_USER@$SSH_IP "bash ${REMOTE_DIR}/deploy/deploy_server_step_1.sh"
sshpass -p $SSH_PWD ssh $SSH_USER@$SSH_IP "bash ${REMOTE_DIR}/deploy/deploy_server_step_2.sh"
sshpass -p $SSH_PWD ssh $SSH_USER@$SSH_IP "bash ${REMOTE_DIR}/deploy/deploy_server_step_3.sh"
sshpass -p $SSH_PWD ssh $SSH_USER@$SSH_IP "bash ${REMOTE_DIR}/deploy/deploy_server_step_4.sh"

# Выводим URL для проверки
echo "http://${SSH_IP}:8000/"
echo "https://drillize.com"

# to do rename path ------ +
#echo 'copy backup'
#sshpass -p $SSH_PWD rsync -avz  --progress --ignore-existing $SSH_USER@$SSH_IP:${LOCAL_DIR}/data/backup/ ${LOCAL_DIR}/data/backup/prod/

#echo 'copy media'
#mkdir -p ${LOCAL_DIR}/data/backup/prod/$(date +"%Y-%m-%d")/media/
#sshpass -p $SSH_PWD rsync -avz  --progress --ignore-existing $SSH_USER@$SSH_IP:${LOCAL_DIR}/public/media/ ${LOCAL_DIR}/data/backup/prod/$(date +"%Y-%m-%d")/media/
# to do rename path ------ -

# copy log
#echo 'copy log'
#sshpass -p $SSH_PWD scp -r $SSH_USER@$SSH_IP:/my/src/dentist/log/ /Users/admin/my/src/dentist/log/prod/
#sshpass -p $SSH_PWD scp -r $SSH_USER@$SSH_IP:/var/log/nginx/error.log /Users/admin/my/src/dentist/log/prod/log/nginx_error.log


