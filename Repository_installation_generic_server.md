Standalone Repository Service
===============================

Creating a standalone repository service allows you to store and have control over the licensing data that you are publishing into the Copyright Hub (CH) ecosystem.
In this document we describe the steps required to get up and running with your own (CH) repository in your own server.

Before your start
-----------------------

To fully complete this process you will need to have:

1. A domain with an SSL certificate (e.g. `https://your_repo.example.com`).
2. The SSL keys for the above certificate.

Join the Copyright Hub ecosystem
-----------------------

This is currently a process that requires authorisation at every step, so we recommend that you liaise with a CH admin when you are ready to do this, in order to complete the steps in quick succession.

**Go to http://services.copyrighthub.org/**

**Create an account on http://services.copyrighthub.org/signup**

You will receive an email requesting that you click a link to verify your email address. Note that even after clicking on this link, you may still have to logout of the service.copyrighthub.org system and then re-login in order to fully activate your account.

**Click on "Create a New Organization" and fill in the form.**

Only organization name is a required field. You will not get any on-screen confirmation that your request has been sent in, but you will get an email saying it has been sent in. The request has to be approved by a CH admin. When that happens, you will get an email confirming your request has been approved.

**Join your organisation by using the "Join Existing Organisation" button**

Again, you will get an email saying you have requested to join. Once the request has been authorised, you will get an email telling you it has been authorised.

**Select the Organisation from the "Existing Organisations" dropdown**

**Click on "Create a New Service"**

"Location" is the URL where you intend the repo to be available, e.g. “https://myrepo.mydomain.org:8765”. "Service Type" is “Repository”. Please make sure to specify the port to which the repository will be responding. In this instructions we'll install the repository responding to requests in port 8765.

As above, this request has to be approved. You will get an email saying your request has been sent in. And you will get an email when it has been approved.

**Go to "Repositories" and select "Create a new Repository"**

Select the repository service you have just created above and give it a name. Again, you will get an email acknowledging your request, and an email when it has been approved.

Proxy to serve SSL requests
-----------------------

We will use a proxy server, **nginx** to redirect SSL requests to the repository server. Specifically, we will redirect requests from ``https://your_repo.example.com:8765/v1/repository`` to ``http://localhost:8004/v1/repository``.

1. Install **nginx** with root privileges using `yum` or `apt-get`.

	Please refer to documentation at <https://www.nginx.com/resources/admin-guide/installing-nginx-open-source>
    
    
2. Configure **nginx** to work as a proxy to SSL requests to port: Create the file `/etc/nginx/conf.d/opp.conf` with the following contents, replacing the ssl settings with the corresponding certificate files:
	```nginx
	server {
		listen  8765 ssl;
		ssl_certificate   /{path}/{your-domain}.crt; # path to your SSL certificate
		ssl_certificate_key  /{path}/{your-domain}.key;	# path to your SSL public key
		server_name  _;
		client_max_body_size 10M;

		location /v1/repository {
			proxy_pass http://localhost:8004;
		}
	}
	```
3. Start **nginx** daemon:

	``service nginx start`` 


Install Blazegraph
-----------------------

The repository relies on Blazegraph graph database. Installation instructions can be found at <https://wiki.blazegraph.com/wiki/index.php/Quick_Start> and <https://wiki.blazegraph.com/wiki/index.php/Installation_guide>.

As an example, we are going to deploy Bazegraph in [Jetty](https://www.eclipse.org/jetty/), a servlet container.

### Jetty installation

The following instructions have been tested in a CentOS Linux distribution and have been extracted from <https://www.unixmen.com/install-jetty-web-server-centos-7/> and <https://hostpresto.com/community/tutorials/how-to-install-jetty-9-on-ubuntu-14-04/>.

Being logged with a user with root privileges,
1. Install Java 1.8

```shell
yum install java-1.8.0-openjdk
```
2. Download Jetty

```shell
wget "http://central.maven.org/maven2/org/eclipse/jetty/jetty-distribution/9.4.4.v20170414/jetty-distribution-9.4.4.v20170414.tar.gz"
```
2. Extract it to /opt/
```shell
tar zxvf jetty-distribution-9.4.4.v20170414.tar.gz -C /opt/

mv /opt/jetty-distribution-9.4.4.v20170414/ /opt/jetty9
``` 

3. Create a system group and user and give appropriate permissions

```shell
groupadd --system jetty

useradd --system -g jetty --no-create-home jetty

usermod -s /sbin/nologin -c "Jetty 9" -d /opt/jetty9 -g jetty jetty

chown -R jetty:jetty /opt/jetty9

chmod u=rwx,g=rxs,o= /opt/jetty9
```

4. Configure Jetty

Create the PID directory

```shell
mkdir /var/run/jetty

chown -R jetty:jetty /var/run/jetty
```

Create a default configuration file ``/etc/default/jetty9`` with content below:

```ini
JETTY_USER=jetty
JETTY_HOME=/opt/jetty9
JETTY_SHELL=/bin/bash
```

Configure logging
```
cd /opt/jetty9/resources

java -jar ../start.jar --add-to-start=requestlog
```

5. Configure Jetty as a service
```
# Create service script
ln -s /opt/jetty9/bin/jetty.sh /etc/init.d/jetty9
# Add script as a service
chkconfig --add jetty9
# Ensure auto-start on boot
chkconfig --level 345 jetty9
```

### Blazegraph Web Application deployment
Download ``blazegraph.war`` from <https://sourceforge.net/projects/bigdata/files/bigdata/2.1.1/> and save it into ``/opt/jetty9/webapps``

Give appropriate permissions and start Jetty server
```shell
chown jetty:jetty /opt/jetty9/webapps/blazegraph.war

service jetty9 start
```

Accessing Blazegraph

You should now be able to access your Blazegraph instance accessing <http://your_repo.example.com:8080/blazegraph>

Install Repository
-----------------------

### Clone the sources of the repository
```
cd /opt/
git clone https://github.com/openpermissions/repository-srv.git
```

### Install dependencies
```
cd /opt/repository-srv
pip install -r requirements/dev.txt
```

### Setup the repository
```
cd /opt/repository-srv
python setup.py develop
```

### Configuring the repository

Create the configuration file ``/opt/repository-srv/config/local.conf`` with the following contents:
```
name = "repository"
port = 8004
processes = 0
version = "0.1.0"
env = "prod"

standalone=True

url_auth = "https://auth.copyrighthub.org"
url_accounts = "https://acc.copyrighthub.org"
url_index = "https://index.copyrighthub.org"

repo_db_path="/blazegraph/namespace/"

use_ssl =  False

## Set the  "Repository ID" as displayed in "https://services.copyrighthub.org/organisation", "Repositories" menu:
service_id = "{repository_id}"

## Set the "Client Secret" as displayed in "https://services.copyrighthub.org/organisation", "Services" menu, clicking the "Edit" link in the repository: 
client_secret = "{client_secret}" 

```

### Launching the repository process
```
python /opt/repository-srv/repository
```

### Further optional configurations

You can execute the repository process with the single command ``python /opt/repository-srv/repository``.

You might prefer to use some kind of process manager to handle the execution of the process like, for exampe, [Supervisor](http://supervisord.org/).

It might also be convenient to avoid executing the repository process from a root-privileged user, but to create a specific user for it.
