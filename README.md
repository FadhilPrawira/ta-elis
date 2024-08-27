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

<table>
    <tr>
        <th>Type</th>
        <th>Name</th>
        <th>Value</th>
        <th>TTL</th>
        <th>Priority</th>
    </tr>
    <tr>
        <td>A</td>
        <td>@</td>
        <td>&lt;YOUR IP ADDRESS&gt;</td>
        <td>3600</td>
        <td>-</td>
    </tr>
    <tr>
        <td>A</td>
        <td>www</td>
        <td>&lt;YOUR IP ADDRESS&gt;</td>
        <td>3600</td>
        <td>-</td>
</table>

3. Wait for the DNS to propagate. You can check the propagation status using [DNS Checker](https://dnschecker.org/). It may take up to 48 hours.

### Setting database

1. `sudo apt install mariadb-server mariadb-client`

2. `sudo mysql_secure_installation`

```
Enter current password for root (enter for none): [enter]
Switch to unix_socket authentication [Y/n] y
Change the root password? [Y/n] y
New password:<YOUR_NEW_PASSWORD>
Re-enter new password:<YOUR_NEW_PASSWORD>
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

10. `sudo apt install pkg-config libmariadb-dev libgl1-mesa-glx`

11. `pip3 install Werkzeug==2.2.2 Flask==2.1.3 Flask-MySQLdb==1.0.1 Flask-Login==0.6.3 numpy==1.26.4 opencv_python==4.8.1.78 matplotlib==3.8.2 joblib mysql-connector scikit-learn==1.5.1`

12. `pip3 install ultralytics==8.2.50 --no-cache-dir`

13. `sudo nano /etc/nginx/sites-enabled/flask_app`

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

31. Try running it with `gunicorn3 --bind 0.0.0.0:5000 --timeout 600 app:app`

32. If it works, run as a daemon with `gunicorn3 --bind 0.0.0.0:5000 --timeout 600 app:app --daemon`

You can close the terminal now.

### Setting PHPMyAdmin

1. `sudo apt install php8.1-fpm phpmyadmin`

```
[Configuring phpmyadmin]

Please choose the web server that should be automatically configured to run phpMyAdmin.

Web server to reconfigure automatically:
[ ] apache2
[ ] lighttpd
<Ok>
```

Just click OK using `TAB`

```
[Configuring phpmyadmin]

The phpmyadmin package must have a database installed and configured before it can be used. This can be optionally handled with dbconfig-common.

If you are an advanced database administrator and know that you want to perform this configuration manually, or if your database has already been installed and configured, you should refuse this option. Details on what needs to be done should most likely be provided in /usr/share/doc/phpmyadmin.

Otherwise, you should probably choose this option.

Configure database for phpmyadmin with dbconfig-common?

<Yes>                            <No>
```

Choose `Yes`

```
[Configuring phpmyadmin]
Please provide a password for phpmyadmin to register with the database server. If left blank, a random password will be generated.

MySQL application password for phpmyadmin:

___________________________________________

<Ok>                            <Cancel>
```

Enter the password for the MySQL database.

```
[Configuring phpmyadmin]
Password confirmation:

_________________________________

<Ok>          <Cancel>
```

Enter the MySQL password again.

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

Add this line

```
include snippets/phpmyadmin.conf;
```

So it change like this:

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

```
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Enter email address (used for urgent renewal and security notices)
 (Enter 'c' to cancel): <YOUR_EMAIL_ADDRESS>

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please read the Terms of Service at
https://letsencrypt.org/documents/LE-SA-v1.4-April-3-2024.pdf. You must agree in
order to register with the ACME server. Do you agree?
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: y

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Would you be willing, once your first certificate is successfully issued, to
share your email address with the Electronic Frontier Foundation, a founding
partner of the Let's Encrypt project and the non-profit organization that
develops Certbot? We'd like to send you email about our work encrypting the web,
EFF news, campaigns, and ways to support digital freedom.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: n
Account registered.
Requesting a certificate for tamonitoringkabel.my.id and www.tamonitoringkabel.my.id

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/tamonitoringkabel.my.id/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/tamonitoringkabel.my.id/privkey.pem
This certificate expires on 2024-11-25.
These files will be updated when the certificate renews.
Certbot has set up a scheduled task to automatically renew this certificate in the background.

Deploying certificate
Successfully deployed certificate for tamonitoringkabel.my.id to /etc/nginx/sites-enabled/flask_app
Successfully deployed certificate for www.tamonitoringkabel.my.id to /etc/nginx/sites-enabled/flask_app
Congratulations! You have successfully enabled HTTPS on https://tamonitoringkabel.my.id and https://www.tamonitoringkabel.my.id

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If you like Certbot, please consider supporting our work by:
 * Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
 * Donating to EFF:                    https://eff.org/donate-le
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
```

12. `sudo systemctl status snap.certbot.renew.service`

13. `sudo certbot renew --dry-run`

### Kill Gunicorn

1. `ps ax|grep gunicorn`

```
ta-elisrara@TA-ElisRara:~$ ps ax|grep gunicorn
  19309 pts/2    S+     0:01 /usr/bin/python3 /usr/bin/gunicorn3 --bind 0.0.0.0:5000 --timeout 600 app:app
  19318 pts/2    S+     0:28 /usr/bin/python3 /usr/bin/gunicorn3 --bind 0.0.0.0:5000 --timeout 600 app:app
  19720 pts/0    S+     0:00 grep --color=auto gunicorn
```

2. `kill -9 <PID_NUMBER>`

```
kill -9 19309
kill -9 19318
```

## TODO:

1. Verify the deployment
2. Fix code that have bugs
