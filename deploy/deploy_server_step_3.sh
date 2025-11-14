# /deploy/deploy_server_step_3.sh
# SERVICES ONLY: GUNICORN + CELERY
set -x

sudo systemctl daemon-reload
sudo systemctl stop retolu.uvicorn.service

sudo systemctl start retolu.uvicorn.service
while ! systemctl is-active --quiet retolu.uvicorn.service; do
    echo "Waiting for retolu.uvicorn.service to start..."
    sleep 1
done
echo "retolu.uvicorn.service has started."

sudo systemctl status retolu.uvicorn.service

sudo systemctl restart nginx

#sudo visudo
#dentist ALL=(ALL) NOPASSWD: /bin/systemctl start retolu.uvicorn.service
#dentist ALL=(ALL) NOPASSWD: /bin/systemctl stop retolu.uvicorn.service
#dentist ALL=(ALL) NOPASSWD: /bin/systemctl status retolu.uvicorn.service
#dentist ALL=(ALL) NOPASSWD: /bin/systemctl restart nginx


