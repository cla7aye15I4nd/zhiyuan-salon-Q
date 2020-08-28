# zhiyuan-salon-Q

## Config

### nginx config

```
server {
        listen 80 default_server;
        listen [::]:80 default_server;

        server_name _;

        location /salon {
                 proxy_pass http://localhost:5000;
        }
}
```
### /etc/systemd/system/salon.service
```
[Unit]
Description=Zhiyuan Salon Query
After=network.target

[Service]
User=admin
Group=www-data
WorkingDirectory=/home/admin/zhiyuan-salon-Q/src
ExecStart=/usr/bin/gunicorn3 -w 4 -b 127.0.0.1:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```
