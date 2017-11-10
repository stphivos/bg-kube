from distutils.core import setup
from pip.req import parse_requirements

install_req = parse_requirements('requirements/core.txt', session='skip')
req = [str(ir.req) for ir in install_req]

setup(
    name='bg-kube',
    packages=['bgkube'],
    version='0.0.4',
    description='An interface that uses gcloud and kubectl to achieve blue-green deployments to GKE',
    author='Phivos Stylianides',
    author_email='stphivos@gmail.com',
    url='https://github.com/stphivos/bg-kube',
    keywords=['kubernetes', 'blue-green', 'google cloud'],
    classifiers=[],
    install_requires=req,
    entry_points={'console_scripts': ['bg-kube = bgkube.__main__:run', ], },
)
