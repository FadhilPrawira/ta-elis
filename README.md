# Tugas Akhir Elis: Python Flask

## Deployment

### Local Windows

1. `pip install virtualenv`

2. `virtualenv venv # create virtual environment with name venv`

3. `source venv/scripts/activate`

4. `pip install -r requirements.txt # Microsoft Visual C++ 14.0 or greater is required https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#latest-microsoft-visual-c-redistributable-version`

### ECS Alibaba 8.215.13.198 Ubuntu 22.04

1. `sudo apt-get update`

2. `sudo apt install curl git pkg-config python3-pip build-essential mariadb-server mariadb-client libmariadb-dev libgl1-mesa-glx php8.1-fpm nginx`

3. `sudo mysql_secure_installation`

```
Enter current password for root (enter for none): Enter
Switch to unix_socket authentication [Y/n] y
Change the root password? [Y/n] y
New password:
Re-enter new password:
Remove anonymous users? [Y/n] y
Disallow root login remotely? [Y/n] n
Remove test database and access to it? [Y/n] y
Reload privilege tables now? [Y/n] y
```

4. `sudo apt install phpMyAdmin`

5. `sudo mysql -u root -p`

```

CREATE USER 'padmin'@'localhost' IDENTIFIED BY 'pwdpwd8';
GRANT ALL PRIVILEGES ON _._ TO 'padmin'@'localhost' WITH GRANT OPTION;
EXIT;

```

6. `sudo nano /etc/nginx/snippets/phpmyadmin.conf`

```

location /phpmyadmin {
root /usr/share/;
index index.php index.html index.htm;
location ~ ^/phpmyadmin/(.+\.php)$ {
try_files $uri =404;
        root /usr/share/;
        fastcgi_pass unix:/run/php/php8.1-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
include /etc/nginx/fastcgi_params;
}

    location ~* ^/phpmyadmin/(.+\.(jpg|jpeg|gif|css|png|js|ico|html|xml|txt))$ {
        root /usr/share/;
    }

}

```

7. `sudo nano /etc/nginx/sites-available/default`

```

        include snippets/phpmyadmin.conf;

```

8. `sudo nginx -t`

9. `sudo systemctl reload nginx`

10. `sudo systemctl reload php8.1-fpm`

11. `sudo ssh-keygen`

12. `sudo cat /root/.ssh/id_rsa.pub`

13. `git clone git@github.com:FadhilPrawira/ta-elis.git`

14. `cd ta-elis`

15. `pip3 install flask flask_login flask_mysqldb matplotlib opencv-python pymysql Flask-SQLAlchemy joblib mysql-connector`

16. `pip3 install ultralytics --no-cache-dir`

17. `sudo nano /etc/nginx/sites-enabled/flask_app`

```

server {
listen 80;
location / {
proxy_pass http://127.0.0.1:8000;
proxy_set_header Host $host;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
}

```

18. `sudo apt install gunicorn3`

19. `gunicorn3 --workers=3 app:app`

```

```
