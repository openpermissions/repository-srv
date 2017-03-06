Standalone Repository Service
==================

Creating a standalone repository service allows you to store and have control over the licensing data that you are publishing into the Copyright Hub (CH) ecosystem.
In order to make that as simple as possible we have created an Amazon Web Services (AWS) Image that you can set up in your AWS with minimal config changes.
In this document we will describe the steps required to get up and running with your own (CH) repository.

Before your start
-----------------------

To fully complete this process you will need to have:

1. An AWS account.

2. A domain with an SSL certificate (e.g. https://copyrighthub.org).

3. The SSL keys for the above certificate.

4. An ssh key to log into the machine you will create (see [here](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/) for instructions on how to generate ssh keys)



There are four steps to follow:
#####Step 1 - Join the Copyright Hub ecosystem
#####Step 2 - Create a Repository Instance from the AWS Marketplace
#####Step 3 - Configure the Repository Instance
#####Step 4 - Test that it has worked



### Step 1 - Join the Copyright Hub ecosystem

This is currently a process that requires authorisation at every step, so we recommend that you liaise with a CH admin when you are ready to do this, in order to complete the steps in quick succession.

**Go to http://services.copyrighthub.org/** 

**Create an account on http://services.copyrighthub.org/signup**

You will receive an email requesting that you click a link to verify your email address. Note that even after clicking on this link, you may still have to logout of the service.copyrighthub.org system and then re-login in order to fully activate your account.

**Click on "Create a New Organization" and fill in the form.**

Only organization name is a required field.
You will not get any on-screen confirmation that your request has been sent in, but you will get an email saying it has been sent in. The request has to be approved by a CH admin. When that happens, you will get an email confirming your request has been approved.

**Join your organisation by using the “Join Existing Organisation” button**

Again, you will get an email saying you have requested to join.
Once the request has been authorised, you will get an email telling you it has been authorised.

**Select the Organisation from the “Existing Organisations” dropdown**

**Click on "Create a New Service"**

"Location" is the URL where you intend the repo to be available, e.g. “https://myrepo.mydomain.org”.
"Service Type" is “Repository”.

Make a note of the client Secret.

As above, this request has to be approved. You will get an email saying your request has been sent in. And you will get an email when it has been approved.

**Go to “Repositories” and select “Create a new Repository”**

Select the repository service you have just created above and give it a name.
Again, you will get an email acknowledging your request, and an email when it has been approved.

Make a note of the repository id 

**You have completed Step 1!**

### Step 2 - Create an Instance from the AWS Marketplace


**Go to [link to AMI]**

Choose the region you want the instance deployed in

Wait for the machine to go through the pending state and be running

Your instance will have an IP address. At this point we recommend that you:

1. Obtain an Amazon Elastic IP address (i.e. a permanent IP address. This is a service you pay for) and assign it to your new instance.

2. Create a DNS entry in AWS Route52 that points the Elastic IP address to your preferred subdomain on your site (e.g. repo.mydomain.org)


More instructions here....

### Step 3 - Configure the Repository Instance

**ssh into the machine**

```
ssh -i ~/.ssh/your-key-pair.pub ubuntu@{your-instance-IP}
```

**Edit the file at /srv/repository/current/config/local.conf**


Enter your client secret, and service id (see Step 1 above. Confusingly, service_id = repository_id), e.g. 

```
service_id = 91b43242eb3e95ecdb178d36204b8f69
client_secret = DSxnM9PRB3CdK9lAV5pTTqD1mDnokj
use_ssl = False
```

**Restart the repository service**

```
sudo supervisorctl
restart repository
```

**Edit the nginx config at  /etc/nginx/conf.d/opp.conf**

Make sure ssl_certificate and ssl_certificate_key match the location of your SSL cert and key, eg:
```
server {
  listen  8765 ssl;
  ssl_certificate   /etc/ssl/certs/{redacted}.crt;
  ssl_certificate_key  /srv/{redacted}.key;
```
##### Permissions on SSL files
Make sure that the certificate files have the right permissions and owners:

###### Public key (.key)
```
sudo chmod 775 {keyfile}
sudo chown ubuntu:ubuntu {keyfile}
```

###### Certificate (.crt)
```
sudo chmod 775 {certfile}
sudo chown root:root {certfile}
```
**Restart nginx**
```
sudo nginx -s reload
```
If it wasn’t already running then just 
```
sudo nginx
```

**Go to yourdomain:8080 (the blazegraph admin)**

Click on the "Namespaces" tab and create a namespace that corresponds to the repo id of your organisation (see Step 1 above).

###You have finished!


### Step 4 - Test that it has worked

At this point, you should have a repository that is fully connected to the Copyright Hub ecosystem. To test it, you can use the onboarding and query services provided by the Copyright Hub.

Save this document to a Makefile in your local machine (and substitute in your client, secret and repo ids) :

```
.DEFAULT_GOAL := onboard

SRV_AUTH  = https://acc.copyrighthub.org
SRV_ON    = https://on.copyrighthub.org
CLIENT    = <your client id here>
SECRET    = <your client secret here>
REPO      = <your repository id here>

AUTH_FILE = auth.json
DATA_FILE = on.csv

clean:
	-rm $(AUTH_FILE) $(DATA_FILE)

$(AUTH_FILE) :
	curl -k $(SRV_AUTH)/v1/auth/token --user $(CLIENT):$(SECRET) --data "grant_type=client_credentials&scope=delegate[https://on.copyrighthub.org]:write[$(REPO)]" -o $@

auth: $(AUTH_FILE)

$(DATA_FILE) :
	echo source_id_types,source_ids,offer_ids,description                                         > $@
	echo danpicspictureid,DSC_012344567,,"Leopard eating Gazelle in Africa" >> $@

data: $(DATA_FILE)

onboard: clean auth data
	$(eval TOKEN := $(shell python -c "import sys, json; print(json.loads(open('${AUTH_FILE}').read())['access_token'])"))
	curl -k $(SRV_ON)/v1/onboarding/repositories/$(REPO)/assets --data-binary @$(DATA_FILE) --header "Accept: application/json" --header "Content-Type: text/csv; charset=utf-8" --header "Authorization: $(TOKEN)"

verify: clean auth data
	$(eval TOKEN := $(shell python -c "import sys, json; print(json.loads(open('${AUTH_FILE}').read())['access_token'])"))
	curl -k $(SRV_AUTH)/v1/auth/verify --header "Accept: application/json" --header "Content-Type: application/x-www-form-urlencode" --header "Authorization: BASIC [$(CLIENT):$(SECRET)]" --data-binary "requested_access=r&token=$(TOKEN)&resource_id=$(REPO)"

```

Then run 
``` 
make
```

If all is well, you should get something like this as a response:

```
{
	"status": 200,
	"data": [{
		"entity_id": "74c2436fae9e4a13a9d85a6f5a4578e4",
		"source_ids": [{
			"source_id": "DSC_012344567",
			"source_id_type": "danpicspictureid"
		}],
		"hub_key": "https://openpermissions.org/s1/hub1/f74c5de3db2e49c693c152a2da87e6d7/asset/74c2436fae9e4a13a9d85a6f5a4578e4",
		"entity_type": "asset"
	}]
}
```


