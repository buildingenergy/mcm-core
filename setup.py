from setuptools import setup, find_packages

from mcm import VERSION

setup(
    name='mcm-core',
    version='.'.join(map(str, VERSION)),
    description='map-clean-merge functionality for importing CSV data.',
    long_description=open('README.md').read(),
    author='Gavin McQuillan',
    author_email='gavin.mcquillan@buildingenergy.com',
    url='http://github.com/buildingenergy/mcm-core',
    license='Apache2',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    package_data = { '': ['README.md'] },
    install_requires=[
        'unicodecsv',
        'fuzzywuzzy',
        'nose',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache2 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
