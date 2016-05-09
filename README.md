Open Permissions Platform Repository Service
============================================

This repository contains the Repository Service for the Open Permissions Platform.

The Repository Service provides the mechanisms for storage and retrieval of licensing data.
It provides a multi-tenant facility, with each client's data stored in repositories which have their own access control policy.

The REStful interface is very similar to that of the Query Service, in order to support end users directly communicating with a repository or via a federating service.

Running locally
===============
#### blazegraph data store

Follow the instruction on blazegraph in [developer environment setup doc]( https://github.com/openpermissions/dev-environment#blazegraph).

#### repository service application

```
pip install -r requirements/dev.txt
python setup.py develop
python repository/
```

To show a list of available CLI parameters:

```
python repository/ -h [--help]
```

To start the service using test.service.conf:

```
python repository/ -t [--test]
```

Running tests and generating code coverage
==========================================
To have a clean target from build artifacts:

```
make clean
```

To install requirements. By default, prod requirement is used:

```
make requirements [REQUIREMENT=test|dev|prod]
```

To run all unit tests and generate an HTML code coverage report along with a
JUnit XML report in tests/unit/reports:

```
make test
```

To run pyLint and generate a HTML report in tests/unit/reports:

```
make pylint
```

To run create the documentation for the service in _build:

```
make docs
```


Loading initial data
====================

To add inital data to the repository, run the following command:

```
python repository load_data fixtures
```
