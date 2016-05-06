# Repository Service Low Level Design
The repository service is responsible for maintaining repositories.

## Contents
+ [Classes](#classes)
+ [Class Relationship](#class-relationship)
  + [Triple Store](#triple-store)
  + [Asset](#asset)
  + [Offer](#offer)
  + [Repository](#repository)
+ [Onboarding assets](#onboarding-assets)

## Classes
+ assets
+ offers
+ repository

## Class Relationship
![](./images/entity-relationship.png)

### Asset
An **asset** is an enttiy which can be copyrighted. The assets are stored adhering to an
ontology based on Open Digital Rights Language (ODRL).

More information on ODRL can be found [here](https://www.w3.org/ns/odrl/2/)

### Offers
An **offer** outlines the usage guidelines for an asset. The offers
are stored adhering to an ontology based on ODRL.

### Repository
A **repository** stores information on assets and their offers.

### Triple Store
A **triple store** is used as a multi-tenant host for several repositories.

## Onboarding assets
![](./images/sequence-new-data-notification.png)
