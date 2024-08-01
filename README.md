# Tugas Akhir Elis: Python Flask

## Deployment

### Local Windows

1. `pip install virtualenv`

2. `virtualenv venv # create virtual environment with name venv`

3. `source venv/scripts/activate`

4. `pip install -r requirements.txt # Microsoft Visual C++ 14.0 or greater is required https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#latest-microsoft-visual-c-redistributable-version`

### ECS Alibaba 8.215.13.198 Ubuntu 22.04

1. `sudo apt-get update`

2. `sudo apt install curl git pkg-config python3-pip build-essential mariadb-server mariadb-client libmariadb-dev libgl1-mesa-glx nginx php8.1-fpm`

`sudo apt-get install libffi-dev`

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

#### Setting Up Python Flask

1. `sudo ssh-keygen`

```
Enter file in which to save the key (/root/.ssh/id_rsa): Enter
Enter passphrase (empty for no passphrase): Enter
Enter same passphrase again: Enter
```

2. `sudo cat /root/.ssh/id_rsa.pub`

Something like this:

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDZ
```

3. `git clone git@github.com:FadhilPrawira/ta-elis.git`

```
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
```

4. `cd ta-elis`

5. `pip3 install flask==2.1.3`

6. `pip3 install Werkzeug==2.2.2`

7. `pip3 install opencv_python==4.8.1.78`

8. `pip3 install flask_login flask_mysqldb joblib mysql-connector ultralytics --no-cache-dir`

9. `sudo nano /etc/nginx/sites-enabled/flask_app`

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

9. `sudo nginx -t`

10. `sudo unlink /etc/nginx/sites-enabled/default`

11. `sudo systemctl reload nginx`

12. `sudo ufw allow 5000`

13. `sudo apt install gunicorn3`

14. Try running it with `gunicorn3 --workers=3 app:app`

15. If it works, run as a daemon with `gunicorn3 --workers=3 app:app`

### Setting PHPMyAdmin

4. `sudo apt install phpMyAdmin`

5. `sudo mysql -u root -p`

```sql
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
