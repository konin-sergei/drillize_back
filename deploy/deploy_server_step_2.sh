# /deploy/deploy_server_step_2.sh
# Deploy remote
#set -x

REMOTE_DIR="/var/www/drillize_back"

cd ${REMOTE_DIR}

echo 'git pull'
git pull origin main

#source ${REMOTE_DIR}/venv/bin/activate
source /my/venvs/drillize/bin/activate

# echo 'start backup'
# ${REMOTE_DIR}/venv/bin/python ${REMOTE_DIR}/manage.py command_backup

# echo 'install requirements'
# ${REMOTE_DIR}/venv/bin/python -m pip install -r ${REMOTE_DIR}/requirements.txt > /dev/null 2>&1
