from setuptools import setup, find_packages

requirements = [
    'stripe',
    'flask',
    'requests',
    'mako',
    'premailer',
]

setup(
    name='uqcs-shirts',
    version='1.0',
    packages=[''],
    url='https://shirts.uqcs.org.au',
    install_requires=requirements,
    license='MIT',
    author='Tom Manderson',
    author_email='me@trm.io',
    description='The UQCS shirt preoder system'
)
