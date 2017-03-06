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



There are three steps to follow:
######  Step 1 - Join the Copyright Hub ecosystem
###### Step 2 - Create a Repository Instance from the AWS Marketplace
###### Step 3 -  Configure the Repository Instance


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
2. Create a DNS entry in Route52 that points the Elastic IP address to your preferred subdomain on your site (e.g. repo.mydomain.org)


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
***Restart nginx**
```
sudo nginx -s reload
```
If it wasn’t already running then just 
```
sudo nginx
```

Go to yourdomain:8080 (the blazegraph admin) and create a namespace in Blazegraph that corresponds to the repo id of your organisation.

