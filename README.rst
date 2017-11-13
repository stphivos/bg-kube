.. image:: https://img.shields.io/pypi/v/bg-kube.svg
    :target: https://pypi.python.org/pypi/bg-kube

.. image:: https://travis-ci.org/stphivos/bg-kube.svg
    :target: https://travis-ci.org/stphivos/bg-kube

.. image:: https://codecov.io/github/stphivos/bg-kube/coverage.svg
    :target: https://codecov.io/github/stphivos/bg-kube

*******
bg-kube
*******
An interface for automating blue-green deployments on a Kubernetes cluster.

**Please note that this project is in initial development and it's not ready for production use yet.
Use with caution in a test/staging environment.**

Features
========
* Publish/Rollback functions.
* Dynamic variables in YAML configuration files.
* Smoke tests for health checking before promoting a new environment.
* Easily extensible to support multiple cloud providers (other than just Google Cloud Platform).
* Minimal setup/resources - does not live in the cloud and can be invoked from a CI service like Travis.

Workflow
========
1. Builds and tags a container image from a Dockerfile using ``docker build`` command.
2. Pushes the tagged image to the container registry (Google Container Registry only at this point).
3. Creates a ``Job`` workload for the database migrations (Optional - should be backwards compatible).
4. Creates a ``Deployment`` workload using the new image.
5. Creates a ``Service`` workload for health checking which runs the specified smoke tests command (Optional).
    * If the tests were successful, it updates the public ``Service`` workload to point to the new deployment.
    * If the tests have failed, the public service remains unaffected.

Installation
============
::

    $ pip install bg-kube

Prerequisites
=============

* `Docker <https://docs.docker.com/engine/installation>`_
* Google Cloud
    * `Create project <https://console.cloud.google.com/projectcreate>`_
    * `Create cluster <https://console.cloud.google.com/kubernetes/add>`_
    * `Install SDK <https://cloud.google.com/sdk/downloads>`_
    * Login using ``gcloud init``
    * Select project using ``gcloud config set project <project-id>``


Example Setup
=============

Service Config - Public
------------------------------
.. code-block:: yaml

    apiVersion: v1
    kind: Service
    metadata:
      annotations:
        external-dns.alpha.kubernetes.io/hostname: $DOMAIN_NAME.
      labels:
        run: $SERVICE_RUN_LABEL
      name: $SERVICE_NAME
      namespace: default
    spec:
      ports:
      - protocol: TCP
        port: $SERVICE_PORT
        targetPort: $CONTAINER_PORT
      selector:
        run: $SERVICE_RUN_LABEL
        type: deployment
        color: $COLOR
      type: LoadBalancer


Service Config - Health Checks
------------------------------
.. code-block:: yaml

    apiVersion: v1
    kind: Service
    metadata:
      labels:
        run: $SERVICE_RUN_LABEL
      name: $SMOKE_SERVICE_NAME
      namespace: default
    spec:
      ports:
      - protocol: TCP
        port: $SERVICE_PORT
        targetPort: $CONTAINER_PORT
      selector:
        run: $SERVICE_RUN_LABEL
        type: deployment
        color: $COLOR
      type: LoadBalancer


Deployment Config
-----------------
.. code-block:: yaml

    apiVersion: extensions/v1beta1
    kind: Deployment
    metadata:
      labels:
        run: $SERVICE_RUN_LABEL
      name: $DEPLOYMENT_NAME-$COLOR
      namespace: default
    spec:
      replicas: 2
      selector:
        matchLabels:
          run: $SERVICE_RUN_LABEL
      template:
        metadata:
          labels:
            run: $SERVICE_RUN_LABEL
            type: deployment
            color: $COLOR
        spec:
          containers:
          - command: ["gunicorn", "django_app.wsgi", "--name", "todoapp", "-b", ":$CONTAINER_PORT"]
            env:
            - name: ENV
              value: $ENV
            - name: DB_URL
              value: $DB_URL
            image: $IMAGE_NAME:$TAG
            name: $CONTAINER_NAME
            ports:
            - containerPort: $CONTAINER_PORT
              protocol: TCP

env
---
::

    ENV=prod
    DB_URL=postgres://user:pass@1.2.3.4:5432/todoapp

    IMAGE_NAME=gcr.io/todoapp-12345/todo-api
    CONTAINER_PORT=8000
    CONTAINER_NAME=cnt-todo-api

    PROJECT_NAME=todoapp-12345
    CLUSTER_NAME=todoapp-cluster
    CLUSTER_ZONE=us-central1-a
    DOMAIN_NAME=todoapp.example.com

    SERVICE_PORT=80
    SERVICE_NAME=svc-todo-api
    SERVICE_CONFIG=./config/service.yaml
    SERVICE_RUN_LABEL=todo-api

    DEPLOYMENT_NAME=dep-todo-api
    DEPLOYMENT_CONFIG=./config/deployment.yaml

Publish using
-------------
::

    $ bg-kube --env-file env publish

Future Improvements
===================
* Capability to unapply database migrations on unsuccessful deployments
* Checks to enforce database migrations are backwards compatible
* Support for more cloud providers
* Better test coverage
