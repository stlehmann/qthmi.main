from setuptools import setup, find_packages


version = '0.2.0'


setup(
    name='qthmi.main',
    version=version,
    description='',
    classifiers=[
        'Programming Language :: Python',
    ],
    keywords='',
    author='',
    author_email='',
    url='',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['qthmi'],
    include_package_data=True,
    test_suite='nose.collector',
    test_requires=['Nose'],
    zip_safe=False,
    install_requires=[
        'setuptools',
        'matplotlib',
    ],
)
