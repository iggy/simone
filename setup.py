try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Simone - Django Webmail App',
    'author': 'Iggy',
    'url': 'https://github.com/iggy/simone',
    'download_url': 'https://github.com/iggy/simone',
    'author_email': 'iggy@theiggy.com',
    'version': '0.1.0',
    'install_requires': [],
    'packages': ['simone'],
    'scripts': [],
    'name': 'simone'
}

setup(**config)
