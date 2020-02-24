# zbat

0)  Checkout source
git checkout https://github.com/kevinwlip/Automation.git


QA Automation setup
-------------------
Objective: Setup zbat project for automation test

### 1. Setup environment variable
Setup environment vaiables for node env, zbat project path and jmeter path.


<b>ZBAT_HOME</b>: absolute path to your zbat project</br>
<b>ZBAT_UNAME</b>: zbat login username</br>
<b>NODE_ENV</b>: nodejs environment for express framework (e.g. production, testing, staging)</br>
<b>JMETER_HOME</b>: absolute path to your jmeter</br>

Example:


```
export ZBAT_HOME=/home/ubuntu/zbat/
export ZBAT_UNAME=test@abc.com
export NODE_ENV=production
export JMETER_HOME=/home/automation/apache-jmeter-3.2/
```

To setup integration test for SMS and Email alert notifications, exports the following environment variables.


<b>ZBAT_TENANT_INTERNAL_ID</b>: 32 characters hash code for tenant</br>
<b>KAFKA_PRODUCER</b>: absolute path to your kafka producer (Should be in 3p folder)</br>
<b>ZBAT_O365_EMAIL_ACCOUNT</b>: email address of O365 email account for receiving email notification</br>
<b>ZBAT_O365_EMAIL_PWD</b>: password of O365 email account</br>
<b>ZBAT_TEXT_NOW_UNAME</b>: username of TextNow account for receiving SMS notification</br>
<b>ZBAT_TEXT_NOW_PWD</b>: password of TextNow account</br>

Example:


```
export ZBAT_TENANT_INTERNAL_ID=ABCDEFGHIJKLMNOPQRSTUVWXYZ012345
export KAFKA_PRODUCER=/home/ubuntu/zbat/3p/kafka_2.11-0.8.2.1/bin/kafka-console-producer.sh
export ZBAT_O365_EMAIL_ACCOUNT=your_email@host.com
export ZBAT_O365_EMAIL_PWD=your_password
export ZBAT_TEXT_NOW_UNAME=jeffreylee
export ZBAT_TEXT_NOW_PWD=your_password
```

To setup test for SIEM server, exports the following environment variables.


<b>ZBAT_SPLUNK_UNAME</b>: username of the splunk server</br>
<b>ZBAT_SPLUNK_PWD</b>: password of the splunk server</br>

Example:


```
export ZBAT_SPLUNK_UNAME=your_username
export ZBAT_SPLUNK_PWD=your_password
```

To setup test for PANFW, exports the following environment variables.


<b>ZBAT_PANFW_UNAME</b>: username of the PANFW</br>
<b>ZBAT_PANFW_PWD</b>: password of the PANFW</br>

Example:


```
export ZBAT_PANFW_UNAME=your_username
export ZBAT_PANFW_PWD=your_password
```

To setup test for Connectiv, exports the following environment variables.


<b>ZBAT_CONNECTIV_UNAME</b>: username of the Connectiv</br>
<b>ZBAT_CONNECTIV_PWD</b>: password of the Connectiv</br>
<b>ZBAT_CONNECTIV_CLIENT_ID</b>: client id of the Connectiv</br>
<b>ZBAT_CONNECTIV_CLIENT_SECRET</b>: client secret of the Connectiv</br>

Example:


```
export ZBAT_CONNECTIV_UNAME=your_username
export ZBAT_CONNECTIV_PWD=your_password
export ZBAT_CONNECTIV_CLIENT_ID=your_client_id
export ZBAT_CONNECTIV_CLIENT_SECRET=your_client_secret
```

To setup tests for customer onboarding, exports the following environment variables.


<b>ZBAT_CUSTOMERS_ADMIN_PANEL_UNAME</b>: username of the customers admin panel</br>
<b>ZBAT_CUSTOMERS_ADMIN_PANEL_PWD</b>: password of the customers admin panel</br>

Example:


```
export ZBAT_CUSTOMERS_ADMIN_PANEL_UNAME=your_username
export ZBAT_CUSTOMERS_ADMIN_PANEL_PWD=your_password
```

To setup policy alert automation test, you will need traffic generator (Drone), Redis and Kafka, exports the following environment variables. 


<b>ZBAT_TG_HOST</b>: host of the traffic generator</br>
<b>ZBAT_TG_UNAME</b>: username of the traffic generator</br>
<b>ZBAT_TG_PWD</b>: password of the traffic generator</br>

<b>ZBAT_REDIS_HOST</b>: host name of Redis</br>
<b>ZBAT_REDIS_PWD</b>: password of Redis</br>

<b>ZBAT_KAFKA_BROKER</b>: Kafka broker list </br>

```
export ZBAT_TG_HOST=your_host_name
export ZBAT_TG_UNAME=your_username
export ZBAT_TG_PWD=your_password

export ZBAT_REDIS_HOST=your_host_name
export ZBAT_REDIS_PWD=your_password

export ZBAT_KAFKA_BROKER=broker_list
```



Since user, reseller and customer onboarding requires deleting a user from database, we setup rules to ONLY able to delete users with 'zbat' keyword in email. Therefore, if you want to setup user onboarding tests, export <b>ZBAT_USER_ONBOARD_EMAIL</b>, <b>ZBAT_RESELLER_ONBOARD_EMAIL</b>, <b>ZBAT_CUSTOMER_ONBOARD_EMAIL</b> with 'zbat' keyword.

Please confirm that 3 email accounts are different from each others. And <b>ZBAT_O365_EMAIL_ACCOUNT</b> can read emails from those 3 alias emails.

Example:


```
export ZBAT_O365_EMAIL_ACCOUNT=qa@host.com
export ZBAT_USER_ONBOARD_EMAIL=zbatdist@host.com
export ZBAT_RESELLER_ONBOARD_EMAIL=zbatres@host.com
export ZBAT_CUSTOMER_ONBOARD_EMAIL=zbatcus@host.com

```

For slack bot to work, please export ZBAT_SLACK_WEBHOOK_URL.


<b>ZBAT_SLACK_WEBHOOK_URL</b>: url from slack bot incoming webhook integration.</br>

Example for channel '#zingbots':


```
export ZBAT_SLACK_WEBHOOK_URL=webhook_url_from_slack_channel
```

To run JIRA automation tests, please export ZBAT_JIRA_UNAME, ZBAT_JIRA_PWD.
For more details, please visit [Confluence documentation](https://zingbox.atlassian.net/wiki/spaces/QH/pages/88247160/ZBat+JIRA+automation).

<b>ZBAT_JIRA_UNAME</b>: JIRA username, not email.</br>
<b>ZBAT_JIRA_PWD</b>: JIRA password.</br>

Example:


```
export ZBAT_JIRA_UNAME=my_name
export ZBAT_JIRA_PWD=my_password
```

To run tests related to Open Vulnerability Assessment, please export OPENVAS_UNAME, OPENVAS_UNAME.

<b>OPENVAS_UNAME</b>: OPENVAS username.</br>
<b>OPENVAS_PWORD</b>: OPENVAS password.</br>

Example:


```
export OPENVAS_UNAME=my_name
export OPENVAS_PWORD=my_password
```

### 2. Activate virtual environment
Setup [python virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) so keep the dependencies required by different projects in separate places and pip will also not pollute global packages.

If you get an error like this when running ```pip install -r requirements.txt``` to install packages:

*Could not install packages due to an EnvironmentError: [Errno 13] Permission denied: '/usr/local/lib/python3.6/site-packages/apipkg.py'
Consider using the `--user` option or check the permissions.*

Then you can follow this guide [[Errno 13] Permission Denied.](https://github.com/googlesamples/assistant-sdk-python/issues/236)

If taking the virtual environment option, while in the virtual environment manually install the package with 'pip install', then try running ```pip install -r requirements.txt``` again.

### 3. Install required dependencies
Project dependencies are stored in [requirements.txt](https://github.com/ZingBox/zbat/blob/master/requirements.txt). Install all of them using

```
python3 -m  pip install -r requirements.txt --user

OR

pip install -r requirements.txt
```

Problem with Python 'requests' package?
```
pip install requests
```

Problem with Python "ERROR: Failed building wheel for tre"?
```
sudo apt-get install libtre-dev
```

### 4. Install 3rd parties applications
Some 3rd party app like Jmeter and Kafka needed to be installed.

For Kafka
```
tar -xzf kafka_2.11-0.11.0.0.tgz
mv kafka_2.11-0.11.0.0 /home/ubuntu/zbat/3p/kafka
export KAFKA_PRODUCER=/home/ubuntu/zbat/3p/kafka/bin/kafka-console-producer.sh
```

For Jmeter, follow installation below

For tcpreplay, follow the [directions](http://tcpreplay.appneta.com/wiki/installation.html) to install it.


### 5. Run tests
If the installation is fine, everything is up and running. To test it out, type in terminal

```
cd tests/api
pytest -v
```

================================================

API Automation
--------------

Contributor can find most of the API routes from [ZingCloud project](https://github.com/ZingBox/zingcloud/blob/master/nodejs/https/server/api/app.js), be aware that usually only GET requests will be tested.

================================================

UI Automation
--------------
Objectives: Setup UI automation evironment.

## Linux version: 

### 1. Remove old version of Nodejs
```
sudo apt-get remove nodejs
```

### 2. Manually removing all traces of node and npm
```
cd /usr/local; sudo rm -rf node*
sudo rm -rf /usr/local/{lib/node{,/.npm,_modules},bin,share/man}/{npm*,node*,man1/node*}
sudo rm -rf /usr/local/bin/npm /usr/local/share/man/man1/node* /usr/local/lib/dtrace/node.d ~/.npm ~/.node-gyp /opt/local/bin/node opt/local/include/node /opt/local/lib/node_modules
cd /usr/local/lib/; rm -rf node_modules/
cd /usr/local/include/; rm -rf node_modules/
```

### 3. Update apt-get
```
sudo apt-get update
sudo apt-get install build-essential libssl-dev
```

### 4. Install nvm and nodejs
Reference from this [link](https://www.liquidweb.com/kb/how-to-install-nvm-node-version-manager-for-node-js-on-ubuntu-12-04-lts/)
```
cd ~
curl -sL https://raw.githubusercontent.com/creationix/nvm/v0.33.2/install.sh -o install_nvm.sh
bash install_nvm.sh
source ~/.profile
nvm install node
nvm alias default node
nvm use default
node -v
nvm ls
```

### 5. Update Chrome Browser
```
sudo apt-get upgrade google-chrome-stable
sudo apt-get install chromium-browser
```

### 6. Install Selenium webdriver-manager
```
npm install -g webdriver-manager
webdriver-manager update
```

### 7. Setup environment variables
```
export NODE_ENV=testing
export ZBAT_UNAME=your_username
export ZBAT_PWD=your_password

```

### 8. Install pytest for python3 and python in the correct order:
```
sudo -H pip3 install pytest
sudo -H pip install pytest
```

## Mac version:
### 1. Remove old version of Nodejs, including all traces ([reference](http://stackabuse.com/how-to-uninstall-node-js-from-mac-osx/))
```
brew uninstall node
```

### 2. Update brew
```
brew update
```

### 3. Install nvm and nodejs
[reference1](https://treehouse.github.io/installation-guides/mac/node-mac.html)
[reference2](https://www.codementor.io/mercurial/how-to-install-node-js-on-macos-sierra-mphz41ekk)
```
brew install node
node -v
npm -v

touch ~/.bash_profile
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.32.1/install.sh | bash
nvm --version
```

### 4. Update Chrome Browser
```
brew cask install --force google-chrome
brew cask install chromium
```

### 5. Install Chrome Driver
```
brew cask install chromedriver
```

### 6. Install Selenium webdriver-manager
```
npm install -g webdriver-manager
webdriver-manager update
```

### 7. Setup environment variables
```
export NODE_ENV=testing
export ZBAT_UNAME=your_username
export ZBAT_PWD=your_password

```

### 8. Install pytest for python3 and python in the correct order:
```
sudo -H pip3 install pytest
sudo -H pip install pytest
```

Add more vars from "QA automation setup" section, depends on what you need to test.

### Install Mozilla Observatory Package
```
cd ~
git clone https://github.com/mozilla/http-observatory.git
cd http-observatory
sudo -H pip3 install --upgrade .
sudo -H pip3 install --upgrade -r requirements.txt
```

## Automation Hints and Debugging
- Implementing a UI Test
    - Use https://testing.zingbox.com/ for the UI
    - Create the code for individual UI tests in zbat/lib/ folder
        1. from common.zbSelenium import zbSelenium
            - this includes Selenium functions such as find single/multi CSS, sendKeys, click, waitCSS, get URL, etc...
        2. You can use past automation codes as a template
    - Create the code for running the tests in zbat/tests/ui
    - Create a test case in JIRA-->https://zingbox.atlassian.net/secure/Dashboard.jspa > Tests > Create a Test
        1. Issue type: Test
        2. Summary: Name of test
        3. Components: 'qa'
        4. Description: Objective of test
        5. Automation ID: /tests/ui/test_Dashboard.py::Test_Dashboard::test_DeviceCategory[chrome]
        6. Test Details: input steps of code and the expected results
- Running a Test
    - Run webdriver in separate terminal:
    
        Linux
        ```
        webdriver-manager start
        ```
        
        OR
        
        Mac OS	
        ```        
        selenium-server -port 4444
        ```
    - Run pytest:
        ```
        pytest -v "test_name"
        ```
	
	If following error appears:
	```
	"unknown command: Cannot call non W3C standard command while in W3C mode"
	```
	Will need to add the following line to the respective browser type in lib/common/zbSelenium.py (is fixed for Chrome) [Detailed Solution](https://stackoverflow.com/questions/56111529/cannot-call-non-w3c-standard-command-while-in-w3c-mode-seleniumwebdrivererr)
	```
	options.add_experimental_option('w3c', False)
	```
	
- Debugging Tips
    - If CSS element is not found, but CSS is correct. Use "pdb.set_trace()" to debug it. If the CSS is found using the pdb, most likely, it is a wait/loading error.
        - Either use a waitLoadProgresDone from zbUIShared.py
        - or use selenium.waitCSS from zbUISelenium

================================================

Reverse SSH Tunnel setup
---------------------
This is needed in order for zbat system in cloud to access local premise resources like Traffic Generator, Inspector, Splunk, PanFW, etc...

Currently, we're using system 192.168.10.40 as the initiator of tunnel to zbat001.azure.zingbox.com and zbat001.cloud.zingbox.com.  To setup tunnel to estalish during setup:

-  SSH to 192.168.10.40
	``` 
	ssh -l automation 192.168.10.40
	```

-  Copy zbat.pem certificate to .ssh/.  If you don't have a certificate already created, you can create one.
	```
	1)  On local host generate a private/public key pair.  Name your cert 'zbat' and leave passphrase empty
        	ssh-keygen -t rsa -b 2048 -v
	2)  Copy public key over to remote host.  This is the same thing as copy the content of zbat.pub into remote host file .ssh/authorized_keys
        	ssh-copy-id -i .ssh/zbat.pub automation@zbat001.cloud.zingbox.com
	```

-  Copy ZBAT script file /util/startReverseSSHTunnel.py to local host at /home/automation/startReverseSSHTunnel.py.  Edit script for any minor modification made to certificate names or remote IP address or ports.

	
-  Edit crontab to add command to run this script every 5 minute.  Script will check if tunnel is not there, then it will bring up.
	```
	crontab -e
	
	# then add line
	*/5 * * * * python /home/automation/startReverseSSHTunnel.py
	```
	
-  Reboot the system, then wait for the 60 seconds delay and run command to check reverse SSH process is running
	```
	ps -ef | grep ssh
	# look for output to show reverse ssh processes started
	```
	
-  On zbat001.azure.zingbox.com, confirm that tunnel is there
	```
	netstat -tanpu | grep -e 22443 -e 22089 -e 22022
	# should see port is listening on localhost
	```

=================================================

Policy Alert Automation
--------------
- install sshpass
    ```
    sudo apt-get install sshpass (Linux)
    brew install https://raw.githubusercontent.com/kadwanev/bigboybrew/master/Library/Formula/sshpass.rb (mac)
    ```
- To test blacklist and whitelist (under tests/rule_engine1)
    ```
    pytest test_policy_alert.py -v -s
    ```
- To test threat (under tests/rule_engine1)
    ```
    # test all threats from all files (default)
    pytest test_ml.py -v -s --alerts=all
    # test a list of allerts
    pytest test_ml.py -v -s --alerts="alert names seperated by comma"
    ```
- Tests are implemented in whitebox testing logic. If you want to force checking Kibana and Kafka, add --forcewhitebox to your command.
   ```
   pytest test_policy_alert.py -v -s --forceall
   ```

================================================

Weekly report Automation
--------------
Optical Character Recognition(OCR) is used to run weekly report automation. To carry out OCR, [pypdfocr](https://pypi.python.org/pypi/pypdfocr) and [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) have to be installed.

- Run pip install
    ```
    pip install -r requirements.txt
    ```
- Install Tre, Tesseract Imagemagick and other dependencies needed to parse Images to text
    ```
    # For ubuntu
    sudo apt-get install tesseract-ocr
    sudo apt-get install poppler-utils
    sudo apt-get install libjpeg-dev
    sudo apt-get install imagemagick
    sudo apt-get install tre-agrep libtre5 libtre-dev
    
    # For MAC
    brew install imagemagick
    brew install tesseract --all-languages
    brew install ghostscript # You may also need ghostscript
    brew install poppler
    brew install tre
    ```
- Download a weekly report and test if pypdfocr is working locally
    ```
    pypdfocr <PATH OF THE DOWNLOADED REPORT>
    ```
    Example, report.pdf will be parsed and output to report_ocr.pdf

================================================

Security Automation
--------------
For security automation, we're using openvas that's running on a docker instance.  For our current deployment, we're deploying this docker instance on machine 192.168.10.40.  We bring up the docker instance at boot up with command:

	```
	# edit crontab
		crontab -e
	# add the following line
		@reboot   sleep 120 && docker run -d -p 9443:443 -p 9390:9390 -p 9400:22 --name openvas kaiyizingbox/openvas-ssh
	```


=================================================
Docker setup
--------------

There are 2 ways to get zbat docker image - Build docker image locally or pull from remote registry.

### Build docker image locally
```
    # First, use git to check out the source.  Let's say you checked it out to /home/automation/zbat
    
    # Next set environment variable ZBAT_HOME
    export ZBAT_HOME=/home/automation/zbat/
    
    # decrypt the .bash_profile_enc file needed by the deployment
    cd $ZBAT_HOME
    openssl enc -aes-256-cbc -d -in .bash_profile_enc -out .bash_profile -k <qa_pasword>
    
    # Go to docker directory
    cd $ZBAT_HOME/docker
    
    # Run docker-compose to bring up container with -d option to detach the container
    docker-compose up -d
    or
    docker-compose up -d <specific_service_name>

    # To run tests
    docker exec -it <CONTAINER_ID> bash    
```

### Pull from remote registry
Reminder: Make sure you login Zingbox docker account and having a valid cert.

```

    docker login -u automation -p <PASSWORD> docker.cloud.zingbox.com:5000/

    sudo docker pull docker.cloud.zingbox.com:5000/zbat:latest # Pull from docker registry
    # End of getting an image

    # To run tests
    sudo docker run -it --rm docker.cloud.zingbox.com:5000/zbat:latest bash -c "source ~/.bash_profile; nohup xvfb-run webdriver-manager start & echo webdriver_running; sleep 10 && pytest tests/ui/test_dashboard.py -v -s --remoteserver 127.0.0.1:4444"

```

### Update docker image
```

    docker-compose up -d # Build an image locally after modification
    docker image tag <IMAGE_ID> docker.cloud.zingbox.com:5000/zbat:latest
    docker image push <IMAGE_ID> docker.cloud.zingbox.com:5000/zbat:latest

```

================================================

# The following section is optional, and if you wanted to run automation tools manually

JMeter manual setup
--------------------
Objective: Setup JMeter manually to run performance tests

### 1. Install Java
Make sure [Java](https://www.digitalocean.com/community/tutorials/how-to-install-java-on-ubuntu-with-apt-get) is installed. Otherwise, you cannot run JMeter.

### 2. Download JMeter source
Download [JMeter 3.2](http://www.apache.org/dist/jmeter/binaries/apache-jmeter-3.2.tgz), extract it and place in your work space. Setup <b>JMETER_HOME</b> environment variable.

Example:


`
export JMETER_HOME=/home/automation/apache-jmeter-3.2/
`

#####Optional
You may also want to alias jmeter command to open it conveniently from CLI.

`
alias jmeter='/home/automation/apache-jmeter-3.2/bin/jmeter'
`

### 3. Download JMeter plugin manager
Download [JMeter plugin manager 0.13](https://jmeter-plugins.org/get/), place the **jmeter-plugins-manager-0.13.jar** file to $JMETER_HOME/lib/ext directory.

This installs plugin manager to JMeter, allowing you to download plugins in JMeter GUI.

### 4. Install plugins
Some plugins were used when designing the tests. We do not have an exhausted list, but our objective here is to install all the plugins to make sure JMeter does not fire errors because of missing any plugins.

Start JMeter, open plugin manager through Options->Plugin Managers.

In tab "Available Plugins", select all of the plugins and click "Apply Changes and Restart JMeter".

### 5. Test JMeter

Restart JMeter, open [Perf_All_API.jmx](https://github.com/ZingBox/zbat/blob/master/3p/jmeter/Perf_All_API.jmx). This open the designed Test Plan
    
    Default parameter of test run:
    -  server:  prouduction-candidate.zingbox.com
    -  tenant:  baycare
    -  tests:   all


Run the tests, view test results from Summary Report or View Result Tree

#####Note
If JMeter complains about missing plugin, go back to step 4.

### 6. Modify tests

      Edit 
            User Defined - Configuration
                  test-to-run: ${__P(test-to-run,all)}.  The "all" can be change to run specific test.  Values can be:
                        ip:  run only IoT Profile test
                        ds:  run only Dashboard Series test
                        ra:  run only Dashboard Risk Assessment test
                        ns:  run only Network Summary test
                        dv:  run only Device Subnet VLAN test
                        ee:  run only External Endpoint test
                        td:  run only Top Device test
                        ta:  run only Top Application test
			    is:  run only Device Inventory Series test
			   dis:  run only Device Inventory Sankey Chart test
			   did:  run only Device Inventory Uniq Dest test
			   dia:  run only Device Inventory Applications tes
            User Defined - Server Info
                  server:  ${__P(server,production-candidate.zingbox.com)}.  The "production-candidate.zingbox.com" can be change to:
                        testing.zingbox.com
                        staging.zingbox.com
                        production-candidate.zingbox.com
                        enterprise.zingbox.com
                  tenantid:  ${__P(tenantid,baycare)}.  The "baycare" can be change to:
                        any tenantid that you want.  Make sure that tenantid matches is presennt on your server.

Encrypting and decrypting
--------------------
To decrypt the file, use openssl with our usual password to decrypt it,
```
openssl enc -aes-256-cbc -d -in <ENCRYPTED_FILE> -out <DECRYPT_FILE> -k <PASSWORD>
```

To encrypt the file, use openssl,
```
openssl enc -aes-256-cbc -salt -in <FILE_TO_BE_ENCRYPTED> -out <OUTPUT_DECRYPTED_FILE> -k <PASSWORD>
```


Installing Ostinato traffic generator (We are using version 0.8.1)
-------------------------------------
Obtain the installation files
```
$ZBAT_HOME/3p/ostinato/
```
Install simple_ostinato library
```
pip install simple-ostinato==0.0.4
```

Install python-ostinato library
```
pip install $ZBAT_HOME/3p/ostinato/python-ostinato-0.8.tar
```

Start Ostinato drone on traffic generation system
```
ssh to machine
sudo drone
```

Installing GeoIP, needed to search Maxmind .dat.  This is for testing Device Detail's org/city
--------------------------------------------------
For Mac, run command
```
brew install GeoIp
```

For Ubuntu
```
sudo apt-get install libgeoip-dev -y
sudo pip install geoip
```

Zingcloud setup required for ZBAT
--------------------------------------------------
Some ZBAT tests require some preliminary setup on Zingcloud web portal
```
# need the following subnets/vlan to be set
# needed for tests test_subnet.py::Test_Subnet
192.168.40.1/32
# needed for rule_engine1 and rule_engine2 tests
81.0.0.0/8
91.0.0.0/8
```
