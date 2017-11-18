# docker
DOCKER_BUILD = 'docker build {context} -f {dockerfile} -t {image}:{tag}'

# docker-machine
DOCKERMACHINE_EVAL_ENV = 'which docker-machine && eval $(docker-machine env {})'

# gcloud
GCLOUD_CONTAINER_CLUSTER_GET_CREDENTIALS = 'gcloud container clusters get-credentials {cluster} --zone {zone}'
GCLOUD_DOCKER_PUSH = 'gcloud docker -- push {}'

# aws
AWS_ECR_GET_CREDENTIALS = '$(aws ecr get-login --no-include-email --region {region})'
AWS_KOPS_EXPORT_CONFIG = 'KOPS_STATE_STORE={store} kops export kubecfg --name {cluster}'
AWS_DOCKER_PUSH = 'docker push {}'

# kubectl
KUBECTL_EXEC = 'kubectl exec {pod} {command} {args}'
