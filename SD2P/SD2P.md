# SD2P

Structured Data Deployment Pipeline

*Deploys structured json files of any size into clustered containers*

*
    `Ubuntu >= 16.04 LTS`
    `virtualenv`
    `nginx`
    `rabbitmq`
    `python3 depencies in requirements.txt`

# python 3.5 +
```
#update & upgrade
    sudo apt update
    sudo apt install software-properties-common
#repo
    sudo add-apt-repository ppa:deadsnakes/ppa
    Press [ENTER] to continue or Ctrl-c to cancel adding it.
#install
    sudo apt install python3.7
#check
    python3.7 --version
```
# pip 
```
#install
    python3 -m pip install --upgrade pip
#upgrade
    pip3 install --upgrade setuptools
    pip3 install -r requirements.txt
```

# virtualenv
```
#install
    pip3 install virtualenv
#check
    which virtualenv
#test
    virtualenv
#activate 
    source venv/bin/activate
#deactivate 
    deactivate
```
# nginx
```
#install
    sudo apt install nginx
    sudo apt-get install libnginx-mod-http-geoip
#firewall
    sudo ufw app list
    sudo ufw allow 'Nginx HTTP'
    sudo ufw status
#status
    systemctl status nginx
#stop
    sudo systemctl stop nginx
#start
    sudo systemctl start nginx
#restart
    sudo systemctl restart nginx
#reload
    sudo systemctl reload nginx
#confiure
    sudo vi /etc/nginx/sites-enabled/defaul
    #update with values from default file
    
```
# rabbitmq
```
#Install RabbitMQ on Ubuntu [port 5672]
echo 'deb http://www.rabbitmq.com/debian/ testing main' | sudo tee /etc/apt/sources.list.d/rabbitmq.list
wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | sudo apt-key add -

#update apt cache and install RabbitMQ server 
sudo apt-get update
sudo apt-get install rabbitmq-server

#Manage RabbitMQ Service
#Using Init –
sudo update-rc.d rabbitmq-server defaults
sudo service rabbitmq-server start
sudo service rabbitmq-server stop

#Uisng Systemctl –
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
sudo systemctl stop rabbitmq-server

#RabbitMQ Web Management Console
sudo rabbitmq-plugins enable rabbitmq_management

#set uname for remote authentication
sudo rabbitmqctl add_user i3d5mok3 WE_DONT_IDE
sudo rabbitmqctl set_user_tags i3d5mok3 administrator
sudo rabbitmqctl set_permissions -p / i3d5mok3 ".*" ".*" ".*"

#sample remote uri ..connect to broker
uri = 'amqp://i3d5mok3:WE_DONT_IDE@192.168.0.51:5672/%2F?heartbeat=60'
pool = amqpstorm_pool.QueuedPool(
    create=lambda: amqpstorm.UriConnection(uri),
    max_size=10,
    max_overflow=10,
    timeout=10,
    recycle=3600,
    stale=45,
)
#enable websocket [port 15674]
rabbitmq-plugins enable rabbitmq_web_stomp 
```
# deploy clusters
```
#script format
    bash nanobin.sh JSON_FILE[VIDEO_DATA.JSON] JSON_FILE_SIZE [100000] JSON_FILE_TYPE [SOCIAL/VIDEO/NM/LIVECAM]

#example
    bash nanobin.sh vide_data.json 100000 social
```
# start clusters
```
    bash start_containers.sh
```
# stop clusters
```
    bash stop_containers.sh
```
