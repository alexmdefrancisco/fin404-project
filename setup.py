from setuptools import setup, find_packages

setup(
    name='fin404-project',
    version='1.0.0',
    description='EPFL Fin404 Derivatives Project: The VIX and related derivatives',
    author='Gabriele Calandrino, Alex Martinez de Francisco, Federico Sabbatani Schiuma, Letizia Seveso',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        # List dependencies from environment.yml or requirements.txt
        # if you intend this to be a standalone package.
        # e.g., 'numpy', 'pandas', 'scipy', 'matplotlib'
    ],
    entry_points={
        'console_scripts': [
            'fin405=main:main',
        ],
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)