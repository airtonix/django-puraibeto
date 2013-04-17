from setuptools import setup, find_packages

import puraibeto as app

setup(name="django-puraibeto",
	version=app.__version__,
	description="Django project that allows private file attachments to any model.",
	author="Zenobius Jiricek",
	author_email="airtonix@gmail.com",
	packages=find_packages(),
	include_package_data=True,
	install_requires=[
		'django-appconf==0.4.1',
		'django-classy-tags',
		'django-guardian',
		'surlex',
	],
)

