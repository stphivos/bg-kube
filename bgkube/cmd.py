# docker
DOCKER_BUILD = 'docker build {context} -f {dockerfile} -t {image}:{tag}'

# docker-machine
DOCKERMACHINE_EVAL_ENV = 'which docker-machine && eval $(docker-machine env {})'

# gcloud
GCLOUD_CONTAINER_CLUSTER_GET_CREDENTIALS = 'gcloud container clusters get-credentials {cluster} --zone {zone}'
GCLOUD_DOCKER_PUSH = 'gcloud docker -- push {}'
