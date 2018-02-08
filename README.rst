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
* Easily extensible to support multiple cloud providers (other than just GKE and AWS/kops).
* Minimal setup/resources - does not live in the cloud and can be invoked from a CI service like Travis.

Workflow
========
1. Builds and tags a container image from a Dockerfile using ``docker build`` command.
2. Pushes the tagged image to the container registry (GCR and ECR only at this point).
3. Creates a ``Job`` workload for the database migrations (Optional - should be backwards compatible).
4. Creates a ``Deployment`` workload using the new image.
5. Creates a ``Service`` for health checking which runs the specified smoke tests command (Optional).
    * If the tests were successful, it updates the public ``Service`` workload to point to the new deployment.
    * If the tests have failed, the public service remains unaffected.

Installation
============
::

    $ pip install bg-kube

Prerequisites
=============

* `Docker <https://docs.docker.com/engine/installation>`_
* `Kubernetes command-line tool <https://kubernetes.io/docs/tasks/tools/install-kubectl/>`_

Google Kubernetes Engine
------------
* `Create project <https://console.cloud.google.com/projectcreate>`_
* `Create cluster <https://console.cloud.google.com/kubernetes/add>`_
* `Install SDK <https://cloud.google.com/sdk/downloads>`_
* Login using ``gcloud init``
* Select project using ``gcloud config set project <project-id>``

AWS using kops
--------------
* `Install AWS CLI <http://docs.aws.amazon.com/cli/latest/userguide/installing.html>`_
* `Install kops CLI <https://github.com/kubernetes/kops/blob/master/docs/install.md>`_
* `Setup environment <https://github.com/kubernetes/kops/blob/master/docs/aws.md>`_

Minimal configurations example
==============================

Service Config - Public
-----------------------
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
        color: $COLOR
        type: pod
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
        color: $COLOR
        type: pod
      type: LoadBalancer


Deployment Config
-----------------
.. code-block:: yaml

    apiVersion: extensions/v1beta1
    kind: Deployment
    metadata:
      labels:
        color: $COLOR
        run: $SERVICE_RUN_LABEL
      name: $DEPLOYMENT_NAME-$COLOR
      namespace: default
    spec:
      replicas: 2
      selector:
        matchLabels:
          color: $COLOR
          run: $SERVICE_RUN_LABEL
      template:
        metadata:
          labels:
            run: $SERVICE_RUN_LABEL
            color: $COLOR
            tag: "$TAG"
            type: pod
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

    $ bg-kube --env-file .env.prod publish

Arguments
---------
::

  positional arguments:
    {publish,rollback,build,push}
    command_args

  optional arguments:
    -h, --help: show this help message and exit
    -e ENV_FILE, --env-file ENV_FILE: .env file for the options below and application vars in the configs
    -c CLUSTER_NAME, --cluster-name CLUSTER_NAME: unique name of the cluster
    -z CLUSTER_ZONE, --cluster-zone CLUSTER_ZONE: zone name of the cluster location
    -m DOCKER_MACHINE_NAME, --docker-machine-name DOCKER_MACHINE_NAME: name of the docker machine if applicable
    --docker-build-args DOCKER_BUILD_ARGS arguments supplied to docker build command separated with spaces
    -i IMAGE_NAME, --image-name IMAGE_NAME: name of the container image to build using docker
    -s SERVICE_NAME, --service-name SERVICE_NAME: name of the main service intended to serve clients
    --service-config SERVICE_CONFIG: config of the main service
    --service-timeout SERVICE_TIMEOUT timeout secs to wait for healthy state or return an error
    --deployment-config DEPLOYMENT_CONFIG config of the deployment containing the main service pods
    --deployment-timeout DEPLOYMENT_TIMEOUT timeout secs to wait for healthy state or return an error
    -x CONTEXT, --context CONTEXT: docker context path used to build the container image
    -d DOCKERFILE, --dockerfile DOCKERFILE: Dockerfile path
    --smoke-service-config SMOKE_SERVICE_CONFIG config of the smoke service lb exposed for health checks
    --smoke-tests-command SMOKE_TESTS_COMMAND: shell command to run health checks against the smoke service
    --db-migrations-job-config-seed DB_MIGRATIONS_JOB_CONFIG_SEED: job config to populate the database with initial data
    --db-migrations-job-timeout DB_MIGRATIONS_JOB_TIMEOUT timeout secs to wait for healthy state or return an error
    --db-migrations-status-command DB_MIGRATIONS_STATUS_COMMAND: shell command executed on any of the running deployment pods to return the current migrations status
    --db-migrations-apply-command DB_MIGRATIONS_APPLY_COMMAND: shell command executed on any of the running deployment pods to apply the latest migrations generated in the current image
    --db-migrations-rollback-command DB_MIGRATIONS_ROLLBACK_COMMAND: shell command executed on any of the running deployment pods with the migrations status command stdout as argument -   retrieved before applying migrations, to perform a rollback to that state
    --kops-state-store KOPS_STATE_STORE: aws cluster state storage bucket name
    --container-registry CONTAINER_REGISTRY: container registry alias or implementation class 

Future Improvements
===================
* Checks to enforce database migrations are backwards compatible
* Support for more cloud providers
* Better test coverage
