# Tugas Akhir Elis: Python Flask

## Deployment on VPS

Here are the steps to deploy the application on a VPS that runs Ubuntu 22.04:

Based on [How to Deploy Flask with Gunicorn and Nginx (on Ubuntu) by Tony Teaches Tech](https://www.youtube.com/watch?v=KWIIPKbdxD0), [Deploy Flask Application on Ubuntu VPS using Nginx by DevGuyAhnaf](https://www.youtube.com/watch?v=BpcK5jON6Cg), and [Run a Flask App with WSGI and NGINX on EC2
](http://nitya.online/index.php/2020/10/11/run-a-flask-app-with-wsgi-and-nginx-on-ec2/).

1. `sudo apt update`

2. `sudo apt install python3-pip`

### Set the domain

1. Buy a domain from registar

2. Go to DNS Management and add an A record with the IP address of the server

3. Wait for the DNS to propagate. You can check the propagation status using [DNS Checker](https://dnschecker.org/). It may take up to 48 hours.

### Setting database

1. `sudo apt install mariadb-server mariadb-client`

2. `sudo mysql_secure_installation`

```
Enter current password for root (enter for none): [enter]
Switch to unix_socket authentication [Y/n] y
Change the root password? [Y/n] y
New password:
Re-enter new password:
Remove anonymous users? [Y/n] y
Disallow root login remotely? [Y/n] n
Remove test database and access to it? [Y/n] y
Reload privilege tables now? [Y/n] y
```

### Setting Up Python Flask

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

3. Add the public key to the [Github SSH keys](https://github.com/settings/ssh/)

4. `sudo apt install nginx`

5. `cd /var/www`

6. `sudo git clone git@github.com:FadhilPrawira/ta-elis.git`

```
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
```

7. `cd ta-elis`

8. `mysql -u root -p`

```sql
CREATE DATABASE sql6709970;
EXIT;
```

9. `mysql -u root -p sql6709970 < sql6709970.sql`

10. `pip3 install Werkzeug==2.2.2`

11. `pip3 install flask==2.1.3`

12. `sudo apt install pkg-config`

13. `sudo apt install libmariadb-dev`

14. `pip3 install flask_mysqldb`

15. `pip3 install flask_login`

16. `pip3 install numpy==1.26.4`

17. `pip3 install opencv_python==4.8.1.78`

18. `sudo apt install libgl1-mesa-glx`

19. `pip3 install matplotlib==3.8.2`

20. `pip3 install joblib mysql-connector`

21. `pip3 install scikit-learn`

22. `pip3 install ultralytics --no-cache-dir`

23. `sudo nano /etc/nginx/sites-enabled/flask_app`

```
server {
    listen 80;
    server_name tamonitoringkabel.my.id www.tamonitoringkabel.my.id;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

24. `sudo nginx -t`

25. `sudo unlink /etc/nginx/sites-enabled/default`

26. `sudo systemctl reload nginx`

27. `sudo chown -R ta-elisrara: /var/www/ta-elis/static/uploads`

28. `sudo mkdir -p /var/www/ta-elis/static/images && sudo chown ta-elisrara:ta-elisrara /var/www/ta-elis/static/images`

Try accessing the server with `http://<YOUR_IP_ADDRESS>`. It should show a 502 Bad Gateway error.

29. `python3 app.py`

It should display the Flask app. But when you try to add a new data, it will show error 504. To fix this, we need to run the app with Gunicorn.

30. `sudo apt install gunicorn3`

31. Try running it with `gunicorn3 --bind 0.0.0.0:5000 app:app`

32. If it works, run as a daemon with `gunicorn3 --bind 0.0.0.0:5000 app:app --daemon`

You can close the terminal now.

### Setting PHPMyAdmin

1. `sudo apt install php8.1-fpm`

2. `sudo apt install phpmyadmin`

3. `sudo mysql -u root -p`

```sql
CREATE USER 'padmin'@'localhost' IDENTIFIED BY 'gTUGfbb99U';
GRANT ALL PRIVILEGES ON _._ TO 'padmin'@'localhost' WITH GRANT OPTION;
EXIT;
```

4. `sudo nano /etc/nginx/snippets/phpmyadmin.conf`

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

5. `sudo nano /etc/nginx/sites-enabled/flask_app`

Change it to this:

```
    server {
    include snippets/phpmyadmin.conf;
    listen 80;
    server_name tamonitoringkabel.my.id www.tamonitoringkabel.my.id;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

5. `sudo nginx -t`

6. `sudo systemctl reload nginx`

7. `sudo systemctl reload php8.1-fpm`

### Setting SSL/HTTPS

1. `sudo snap install core; sudo snap refresh core`

2. `sudo apt remove certbot`

3. `sudo snap install --classic certbot`

4. `sudo ln -s /snap/bin/certbot /usr/bin/certbot`

5. `sudo ufw status`

6. `sudo ufw enable`

7. `sudo ufw allow 'OpenSSH'`

8. `sudo ufw allow 'Nginx Full'`

9. `sudo ufw delete allow 'Nginx HTTP'`

10. `sudo ufw status`

11. `sudo certbot --nginx -d tamonitoringkabel.my.id -d www.tamonitoringkabel.my.id`

12. `sudo systemctl status snap.certbot.renew.service`

13. `sudo certbot renew --dry-run`

## TODO:

1. Verify the deployment
2. Fix code that have bugs
