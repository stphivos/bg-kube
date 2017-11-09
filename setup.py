from distutils.core import setup

setup(
    name='bg-kube',
    packages=['bgkube'],
    version='0.0.1',
    description='An interface that uses gcloud and kubectl to achieve blue-green deployments to GKE',
    author='Phivos Stylianides',
    author_email='stphivos@gmail.com',
    url='https://github.com/stphivos/bg-kube',
    keywords=['kubernetes', 'blue-green', 'google cloud'],
    classifiers=[],
    install_requires=['pykube>=0.15.0', 'PyYAML>=3.12'],
    entry_points={'console_scripts': ['bg-kube = bgkube.__main__:run', ], },
)
