from distutils.core import setup
from pip.req import parse_requirements

install_req = parse_requirements('requirements/core.txt', session='skip')
req = [str(ir.req) for ir in install_req]


def read(filename):
    with open(filename) as file:
        return file.read()


setup(
    name='bg-kube',
    packages=['bgkube'],
    version='0.0.13',
    description='An interface for automating blue-green deployments using Kubernetes',
    long_description=read('README.rst'),
    author='Phivos Stylianides',
    author_email='stphivos@gmail.com',
    url='https://github.com/stphivos/bg-kube',
    keywords='Kubernetes microservices blue-green GKE AWS Kops CI/CD Continuous integration delivery deployment',
    classifiers=[],
    install_requires=req,
    entry_points={'console_scripts': ['bg-kube = bgkube.__main__:run', ], },
)
