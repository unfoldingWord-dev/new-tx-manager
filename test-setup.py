from setuptools import setup

setup(
    name='tx-manager',
    version='0.2.65',
    package_dir={
        'client_callback': 'functions/client_callback',
        'client_webhook': 'functions/client_webhook',
        'convert_md2html': 'functions/convert_md2html',
        'convert_usfm2html': 'functions/convert_usfm2html',
        'door43_deploy': 'functions/door43_deploy',
        'list_endpoints': 'functions/list_endpoints',
        'register_module': 'functions/register_module',
        'request_job': 'functions/request_job',
        'start_job': 'functions/start_job',
        'client': 'libraries/client',
        'converters': 'libraries/converters',
        'aws_tools': 'libraries/aws_tools',
        'door43_tools': 'libraries/door43_tools',
        'general_tools': 'libraries/general_tools',
        'gogs_tools': 'libraries/gogs_tools',
        'lambda_handlers': 'libraries/lambda_handlers',
        'manager': 'libraries/manager',
        'resource_container': 'libraries/resource_container'
    },
    packages=[
        'client_callback',
        'client_webhook',
        'convert_md2html',
        'convert_usfm2html',
        'door43_deploy',
        'list_endpoints',
        'register_module',
        'request_job',
        'start_job',
        'client',
        'converters',
        'aws_tools',
        'door43_tools',
        'general_tools',
        'gogs_tools',
        'lambda_handlers',
        'manager',
        'resource_container'
    ],
    package_data={'converters': ['templates/*.html']},
    author='unfoldingWord',
    author_email='unfoldingword.org',
    description='Unit test setup file.',
    keywords=[
        'tX manager',
        'unfoldingword',
        'usfm',
        'md2html',
        'usfm2html'
    ],
    url='https://github.org/unfoldingWord-dev/tx-manager',
    long_description='Unit test setup file',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
        'requests==2.13.0',
        'responses==0.5.1',
        'boto3==1.4.4',
        'bs4==0.0.1',
        'gogs_client==1.0.3',
        'coveralls==1.1',
        'python-json-logger==0.1.5',
        'markdown==2.6.8',
        'markdown2==2.3.4',
        'future==0.16.0',
        'pyparsing==2.1.10',
        'usfm-tools==0.0.12',
        'mock',  # travis reports syntax error in mock setup.cfg if we give version
        'moto==1.0.1',
        'PyYAML==3.12'
    ],
    test_suite='tests'
)

