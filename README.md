# ExtensiveAutomation

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/extensiveautomation-server)
![](https://github.com/ExtensiveAutomation/extensiveautomation-server/workflows/Python%20Package/badge.svg)
![](https://github.com/ExtensiveAutomation/extensiveautomation-server/workflows/Docker%20Image/badge.svg)

| | |
| ------------- | ------------- |
| ExtensiveAutomation | Python automation server |
| Copyright |  Copyright (c) 2010-2020  Denis Machard <d.machard@gmail.com> |
| License |  LGPL2.1 |
| Homepage |  https://www.extensiveautomation.org/ |
| Docs |  https://extensiveautomation.readthedocs.io/en/latest/ |
| Github |  https://github.com/ExtensiveAutomation |   
| Docker Hub | https://hub.docker.com/u/extensiveautomation |   
| PyPI |  https://pypi.org/project/extensiveautomation-server/ |
| Google Users | https://groups.google.com/group/extensive-automation-users |
| Twitter | https://twitter.com/Extensive_Auto |
| | |

## Table of contents
* [Introduction](#introduction)
* [Server Installation](#installation)
	* [PyPI package](#pypi-package)
	* [Docker image](#docker-image)
	* [Source code](#source-code)
	* [Adding plugins](#adding-plugins)
* [Connecting to server](#connecting-to-server) 
	* [Connection to server with curl](#connection-to-server-with-curl)
	* [Connection to server with the web client](#connection-to-server-with-the-web-client)
	* [Connection to server with the app client](#connection-to-server-with-the-app-client)
* [How to execute a task from REST API](#how-to-execute-a-task-from-rest-api) 
	* [Get api secret key](#get-api-secret-key)
	* [Run basic task](#run-basic-task)
	* [Get task logs](#get-task-logs)
* [How to write and execute a SSH task](#how-to-write-and-execute-a-ssh-task)
	* [Describe your YAML task](#describe-your-yaml-task)
    * [Execute the task from web interface](#execute-the-task-from-web-interface)
    * [Display the result of the task from the web interface](#display-the-result-of-the-task-from-the-web-interface)
* [Security](#security)
	* [Adding ReverseProxy](#reverse-proxy)
	* [LDAP users authentication](#ldap-users-authentication)

## Introduction

**ExtensiveAutomation**  is a generic automation framework in 100% Python for integration, regression and end-to-end usages. The framework provided a rich and collaborative workspace environment. 

## Server Installation

### PyPI package

1. Run the following command

        python3 -m pip install extensiveautomation_server

2. Type the following command on your shell to start the server

        extensiveautomation --start

3. Finally, check if the [server is running fine](#connection-to-server-with-curl).

### Docker image

1. Downloading the image

        docker pull extensiveautomation/extensiveautomation-server:latest

2. Start the container

        docker run -d -p 8081:8081 -p 8082:8082 -p 8083:8083 \
                   --name=extensive extensiveautomation

   If you want to start the container with persistant tests data, go to [Docker Hub](https://hub.docker.com/r/extensiveautomation/extensiveautomation-server) page.

3. Finally, check if the [server is running fine](#connection-to-server-with-curl).
   
### Source code
 
1. Clone this repository on your linux server

        git clone https://github.com/ExtensiveAutomation/extensiveautomation-server.git
        cd extensiveautomation-server/
        
2. As precondition, install the additional python libraries with `pip` command: 
   
        python3 -m pip install wrapt pycnic lxml jsonpath_ng pyyaml

3. Start the server. On linux the server is running as daemon.

        cd src/
        python3 extensiveautomation.py --start
        
4. Finally, check if the [server is running fine](#connection-to-server-with-curl).
 
### Adding plugins

Plugins allow to interact with the system to be controlled. But by default the server is provided without plugins. So you need to install them one by one according to your needs.

* [CLI plugin (ssh)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-cli)

        pip install extensiveautomation_plugin_cli
        ./extensiveautomation --reload
         
* [WEB plugin (http/https)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-web)

        pip install extensiveautomation_plugin_web
        ./extensiveautomation --reload
         
* [GUI plugin (selenium, sikulix and adb)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-gui)
* [And many others...](https://github.com/ExtensiveAutomation/extensiveautomation-plugins-server)

## Connecting to server

### Connection to server with curl

1. Please to take in consideration the following points:
	
	 - The server is running on the following tcp ports (don't forget to open these ports on your firewall):
	    - tcp/8081: REST API
	    - tcp/8081: Websocket tunnel for app client
	    - tcp/8082: Websocket tunnel for agents
	 - The `admin`, `tester` and `monitor` users are available and the default passoword is `password`. 
	 - The `Common` project is created by default, attached to the previous users.
	 - Swagger for the REST API is available in the `scripts/swagger` folder.
    
2. Checking if the REST api working fine with curl or postman.

       curl -X POST http://127.0.0.1:8081/session/login \
            -H "Content-Type: application/json" \
            -d '{"login": "admin", "password": "password"}'

   success response:

        {
            "cmd": "/session/login", 
            "message": "Logged in", 
            "session_id": "MjA1OWI1OTc1MWM0NDU2NDg4MjQxMjRjNWFmN2FkNThhO", 
            "expires": 86400, 
            "user_id": 1, 
            "levels": ["Administrator"], 
            "project_id": 1, 
            "api_login": "admin", 
            "api_secret": "6977aa6a443bd3a6033ebb52557cf90d24c79857", 
            "client-available": false, 
            "version": "",
            "name": ""
        }

### Connection to server with the web client

To use the server from the web interface, please to read the following [documentation](https://github.com/ExtensiveAutomation/extensiveautomation-webclient#web-interface-for-extensiveautomation).
This user interface enables to:
- manage users
- manage projects
- manage variables
- and more...

### Connection to server with the app client
  
To use the server from the rich application, please to read the following [documentation](https://github.com/ExtensiveAutomation/extensiveautomation-appclient#qt-application-for-extensiveautomation).

## How to execute a task from REST API

### Get api secret key

Get the API secret for the user admin

        python3 extensiveautomation.py --apisecret admin
        API key: admin
        API secret: 6977aa6a443bd3a6033ebb52557cf90d24c79857

### Run basic task 

Tasks samples are available in the default data storage <projectpath_install>/var/tests/1/

Curl command:

        curl  --user admin:6977aa6a443bd3a6033ebb52557cf90d24c79857 \
              -d '{"project-id": 1,"test-extension": "yml", "test-name": "01_testunit",
              "test-path": "YAML_samples/Framework_Tests/"}' \
              -H "Content-Type: application/json" \
              -X POST http://127.0.0.1:8081/tasks/schedule
              
Success response:

        {
            "cmd": "/tasks/schedule",
            "message": "background", 
            "task-id": 2,
            "test-id": "e57aaa43-325d-468d-8cac-f1dea822ef3a", 
            "tab-id": 0,
            "test-name": "01_testunit"
        }
        
### Get task logs

Curl command:

        curl  --user admin:6977aa6a443bd3a6033ebb52557cf90d24c79857 \
              -d '{"test-id": "e57aaa43-325d-468d-8cac-f1dea822ef3a", "project-id": 1}' \
              -H "Content-Type: application/json" \
              -X POST http://127.0.0.1:8081/results/details
        
Success response:

        {
            "cmd": "/results/details",
            "test-id": "e57aaa43-325d-468d-8cac-f1dea822ef3a", 
            "test-status": "complete", 
            "test-verdict": "pass", 
            "test-logs": "10:50:10.7241 task-started
            10:50:10.7243 script-started 01_testunit
            10:50:10.7309 script-stopped PASS 0.007
            10:50:10.7375 task-stopped 0.006909608840942383", 
            "test-logs-index": 156
        }

## How to write and execute a SSH task

This example describe how to:
- execute a ssh commands on a remote server
- detect specific content on the output of the command
- save a part of the output to execute a second command with-it

### Describe your YAML task

The SSH plugin must be installed, please refer to [Adding plugins](#adding-plugins).

Go inside your data storage, you can execute the following command to find the path.

        python3 extensiveautomation.py --datastorage
        /<install_project>/ea/var/tests/
        
        cd /<install_project>/ea/var/tests/

Create your YAML file in the default project (1)

        cd 1/
        touch task_ssh.yml
        
Add the following content inside the file:

        properties:
          parameters:
          - name: SERVERS
            type: json
            value: |-
              [
                  {
                      "SSH_DEST_HOST": "10.0.0.55",
                      "SSH_DEST_PORT": 22,
                      "SSH_DEST_LOGIN": "root",
                      "SSH_DEST_PWD": "bonjour",
                      "SSH_PRIVATE_KEY": null,
                      "SSH_PRIVATE_KEY_PATH": null,
                      "SSH_AGENT": { "name": "agent.win.ssh01", "type": "ssh" },
                      "SSH_AGENT_SUPPORT": false
                  }
              ]
        testplan:
        - alias: Get hostname of the machine
          file: Common:YAML_snippets/Protocols/01_Send_SSH.yml
          parameters:
          - name: COMMANDS
            type: text
            value: |-
                # check status
                uname -n && echo {}
                .*{}.*\n[!CAPTURE:MACHINE_HOSTNAME:]\n{}.*
                
        - alias: Ping hostname
          file: Common:YAML_snippets/Protocols/01_Send_SSH.yml
          parameters:
          - name: COMMANDS
            type: text
            value: |-
                # send ping 
                clear && ping -c 3 [!CACHE:MACHINE_HOSTNAME:]
                .*3 packets transmitted, 3 received, 0% packet loss.*
                

### Execute the task from web interface

Install the web interface as describe on the page [Connection to server with the web client](#connection-to-server-with-the-web-client).

Go to the menu Automation > Task > Add Task

Select the File "task_ssh" and click on the button 'CREATE'

### Display the result of the task from the web interface

Go to the menu Automation > Run  and display Logs


## Security

### Adding reverse proxy

Adding a reverse proxy in the front of server enables to expose only one tcp port (8080) 
and to have a TLS link between the client and the server. 
Also, the default behaviour of the QT client and toolbox is to try to connect 
on the tcp/8080 port with ssl (can be modifed).

If you want to install a reverse proxy, please to follow this procedure.

1. Install the example provided `scripts\reverseproxy\extensiveautomation_api.conf` in your apache instance. If you install the reverse proxy on a new server, don't forget to replace the 127.0.0.1 address by the ip of your extensive server.

        Listen 8080

        <VirtualHost *:8080>
          SSLEngine on

          SSLCertificateFile /etc/pki/tls/certs/localhost.crt
          SSLCertificateKeyFile /etc/pki/tls/private/localhost.key

          LogLevel warn
          ErrorLog  /var/log/extensiveautomation_api_error_ssl_rp.log
          CustomLog /var/log/extensiveautomation_api_access_ssl_rp.log combined

          Redirect 307 / /rest/session/login

          ProxyPass /rest/ http://127.0.0.1:8081/
          ProxyPassReverse /rest/ http://127.0.0.1:8081/
          
          ProxyPass /wss/client/ ws://127.0.0.1:8082 disablereuse=on
          ProxyPassReverse /wss/client/ ws://127.0.0.1:8082 disablereuse=on

          ProxyPass /wss/agent/ ws://127.0.0.1:8083 disablereuse=on
          ProxyPassReverse /wss/agent/ ws://127.0.0.1:8083 disablereuse=on
        </VirtualHost>

    With this configuration in apache, the REST API is now running on the port tcp/8080 (tls).

2. Checking if the REST api working fine with curl command.

       curl -X POST https://127.0.0.1:8080/rest/session/login --insecure \ 
         -H "Content-Type: application/json" \
         -d '{"login": "admin", "password": "password"}'
         
### LDAP users authentication

By default, users are authenticated locally from database (by checking hash password).
This behavior can be modified by using a remote authentication server. In this mode, you always need to add users in the local database.

Follow this procedure to enable LDAP authentication:

1. Install python dependancies with the `pip` command:

        python3 -m pip install ldap3

2. Configure the `settings.ini`  file to enable ldap authentication and other stuff

        [Users_Session]
        
        ; enable ldap user authentication for rest api session only
        ; 0=disable 1=enable
        ldap-authbind=1
        ; remote addresses of your ldap servers
        ; ldaps://127.0.0.1:636 
        ldap-host=[ "ldap://127.0.0.1:389" ]
        ; username form
        ; uid=%%s,ou=People,dc=extensive,dc=local
        ldap-dn=[ "uid=%%s,ou=People,dc=extensive,dc=local" ]


3. Restart the server

        cd src/
        python3 extensiveautomation.py --stop
        python3 extensiveautomation.py --start
        
4. Check the new user authentication method

       curl -X POST http://127.0.0.1:8081/session/login \
            -H "Content-Type: application/json" \
            -d '{"login": "admin", "password": "password"}'
