# Deploy remote
#set -x

REMOTE_DIR="/var/www/drillize_back"

cd ${REMOTE_DIR}
git reset --hard HEAD
git pull

