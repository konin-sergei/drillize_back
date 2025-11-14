# /deploy/deploy_server_step_3.sh
# SERVICES ONLY: GUNICORN + CELERY
set -x

sudo systemctl daemon-reload
sudo systemctl stop drillize.uvicorn.service

sudo systemctl start drillize.uvicorn.service
while ! systemctl is-active --quiet drillize.uvicorn.service; do
    echo "Waiting for drillize.uvicorn.service to start..."
    sleep 1
done
echo "drillize.uvicorn.service has started."

sudo systemctl status drillize.uvicorn.service

sudo systemctl restart nginx

#sudo visudo
#dentist ALL=(ALL) NOPASSWD: /bin/systemctl start drillize.uvicorn.service
#dentist ALL=(ALL) NOPASSWD: /bin/systemctl stop drillize.uvicorn.service
#dentist ALL=(ALL) NOPASSWD: /bin/systemctl status drillize.uvicorn.service
#dentist ALL=(ALL) NOPASSWD: /bin/systemctl restart nginx


