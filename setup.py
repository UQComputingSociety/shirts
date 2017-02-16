from setuptools import setup, find_packages
import sys

requirements = [
    'stripe',
    'flask',
    'requests',
    'mako',
    'premailer',
]

if sys.version_info < (3, 5):
    requirements.append('typing')


setup(
    name='uqcs-shirts',
    version='1.0',
    packages=find_packages(),
    url='https://shirts.uqcs.org.au',
    install_requires=requirements,
    license='MIT',
    author='Tom Manderson',
    author_email='me@trm.io',
    description='The UQCS shirt preoder system'
)
