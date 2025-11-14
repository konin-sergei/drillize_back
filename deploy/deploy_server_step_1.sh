# Deploy remote
#set -x

REMOTE_DIR="/var/www/retolu_back"

cd ${REMOTE_DIR}
git reset --hard HEAD
git pull

