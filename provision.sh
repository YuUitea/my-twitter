#!/usr/bin/env bash

echo 'Start!'

sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.6 9

cd /docker

sudo apt-get update
sudo apt-get install tree

# setup mysql8
if ! [ -e /docker/mysql-apt-config_0.8.19-1_all.deb ]; then
	wget -c https://dev.mysql.com/get/mysql-apt-config_0.8.19-1_all.deb
fi

sudo dpkg -i mysql-apt-config_0.8.19-1_all.deb
sudo DEBIAN_FRONTEND=noninteractivate apt-get install -y mysql-server
sudo apt-get install -y libmysqlclient-dev

if [ ! -f "/usr/bin/pip" ]; then
  sudo apt-get install -y python3-pip
  sudo apt-get install -y python-setuptools
  sudo ln -s /usr/bin/pip3 /usr/bin/pip
else
  echo "pip3 installed"
fi

# install and upgrade using requirements
sudo pip install --upgrade setuptools
sudo pip install --ignore-installed wrapt
# install latest pip
sudo pip install -U pip
# install pip based on requirements.txt to ensure compatibility
sudo pip install -r requirements.txt

# set up database user
# create 'twitter' database
sudo mysql -u root << EOF
	ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'anticipation';
	flush privileges;
	show databases;
	CREATE DATABASE IF NOT EXISTS twitter;
EOF
# fi

# superuser
USER="admin"
# superuser password
PASS="anticipation"
# superuser email
MAIL="admin@wejoy.com"
script="
from django.contrib.auth.models import User;
username = '$USER';
password = '$PASS';
email = '$MAIL';
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password);
    print('Superuser created.');
else:
    print('Superuser creation skipped.');
"
printf "$script" | python manage.py shell

echo 'All Done!'
