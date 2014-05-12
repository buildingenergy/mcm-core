from setuptools import setup, find_packages

from mcm import VERSION

setup(
    name='mcm-core',
    version='.'.join(map(str, VERSION)),
    description='Map Clean Merge: Convert CSV Data into Python Objects.',
    long_description=open('README.md').read(),
    author='Gavin McQuillan',
    author_email='gavin.mcquillan@buildingenergy.com',
    url='https://github.com/buildingenergy/mcm-core/',
    license='Apache2',
    packages=find_packages(),
    include_package_data=True,
    package_data = { '': ['README.md'] },
    install_requires=[
        'fuzzywuzzy',
        'nose',
        'python-dateutil',
        'unicodecsv'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: Mozilla',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License 2.0',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
