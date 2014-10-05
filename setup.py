from os.path import dirname, join
from setuptools import setup, find_packages

README = "README.txt"
with open(join(dirname(__file__), 'VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()

setup(
    name='ytwl2pl',
    version=version,
    author='Ruslan Portnoy',
    author_email='ruslanoid@gmail.com',
    description='YouTube WatchLater 2 Playlist exporter-importer',
    long_description=open(README).read(),
    url='http://github.com/ruslanoid/ytwl2pl',
    license='GPL',
    # packages=['ytwl2pl'],
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    keywords="yotube playlist",
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: GPL License',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ],
    install_requires=[
        "argparse>=1.2.1",
        "certifi>=14.05.14",
        "google-api-python-client>=1.2",
        "httplib2>=0.9",
        "requests>=2.4.0",
        "wsgiref>=0.1.2"
    ]
)

# setup(
#     entry_points={
#         'console_scripts': ['scrapy = scrapy.cmdline:execute']
#     },
# )