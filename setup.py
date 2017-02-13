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
    packages=find_packages(),
    url='https://shirts.uqcs.org.au',
    install_requires=requirements,
    include_package_data=True,
    license='MIT',
    author='Tom Manderson',
    author_email='me@trm.io',
    description='The UQCS shirt preoder system',
    entry_points={
        'console_scripts': [
            'shirts_run = uqcs_shirts.__main__:main',
        ],
    },
)
