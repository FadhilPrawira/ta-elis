# Tugas Akhir Elis: Python Flask

## Deployment

### Local Windows

1. `pip install virtualenv`

2. `virtualenv venv # create virtual environment with name venv`

3. `source venv/scripts/activate`

4. `pip install -r requirements.txt # Microsoft Visual C++ 14.0 or greater is required https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#latest-microsoft-visual-c-redistributable-version`

### ECS Alibaba 8.215.13.198 Ubuntu 22.04

Based on [How to Deploy Flask with Gunicorn and Nginx (on Ubuntu) by Tony Teaches Tech](https://www.youtube.com/watch?v=KWIIPKbdxD0) and [Deploy Flask Application on Ubuntu VPS using Nginx by DevGuyAhnaf](https://www.youtube.com/watch?v=BpcK5jON6Cg).

1. `sudo apt update`

2. `sudo apt install python3-pip mariadb-server mariadb-client`

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

##### Set virtual environment for python

`python3 -m venv ~/env/flask_Tugas_Akhir`
`source ~/env/flask_Tugas_Akhir/bin/activate`

4. `cd ta-elis`

5. `mysql -u root -p`

```sql
CREATE DATABASE sql6709970;
EXIT;
```

6. `mysql -u root -p sql6709970 < sql6709970.sql`

7. `pip3 install Werkzeug==2.2.2`

8. `pip3 install flask==2.1.3`

9. `pip3 install mysqlclient==2.1.1`

10. `sudo apt install pkg-config`

11. `sudo apt install libmariadb-dev`

12. `pip3 install flask_mysqldb`

13. `pip3 install flask_login`

14. `pip3 install numpy==1.26.4`

15. `pip3 install opencv_python==4.8.1.78`

16. `sudo apt install libgl1-mesa-glx`

17. `pip3 install matplotlib==3.8.2`

18. `pip3 install ultralytics --no-cache-dir`

19. `pip3 install joblib mysql-connector`

20. `pip3 install scikit-learn`

21. `sudo apt install nginx`

22. `sudo nano /etc/nginx/sites-enabled/flask_app`

```
server {
    listen 80;
    location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

23. `sudo nginx -t`

24. `sudo unlink /etc/nginx/sites-enabled/default`

25. `sudo systemctl reload nginx`

Try accessing the server with `http://<YOUR_IP_ADDRESS>`. It should show a 502 Bad Gateway error.

26. `sudo apt install gunicorn3`

27. Try running it with `gunicorn3 --bind 0.0.0.0:5000 app:app`

28. If it works, run as a daemon with `gunicorn3 --bind 0.0.0.0:5000 app:app --daemon`

### Setting PHPMyAdmin

1. `sudo apt install php8.1-fpm phpMyAdmin`

2. `sudo mysql -u root -p`

```sql
CREATE USER 'padmin'@'localhost' IDENTIFIED BY 'pwdpwd8';
GRANT ALL PRIVILEGES ON _._ TO 'padmin'@'localhost' WITH GRANT OPTION;
EXIT;
```

3. `sudo nano /etc/nginx/snippets/phpmyadmin.conf`

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

4. `sudo nano /etc/nginx/sites-available/default`

```
        include snippets/phpmyadmin.conf;
```

5. `sudo nginx -t`

6. `sudo systemctl reload nginx`

7. `sudo systemctl reload php8.1-fpm`

## TODO:

1. Verify the deployment
2. Fix code so user doesn't asked about login again
3. Create a new non-root user
4. Create a new non-root user for the database (So the code doesn't need to be changed)
5. Deploy PHPMyAdmin together with the Flask app
6. Add domain name `tamonitoringkabel.my.id`
7. Add SSL certificate
