from setuptools import setup, find_packages

setup(
    name='filedrop',  # Package name
    version='1.0.6',  # Version of the package
    packages=find_packages(),  # This will include all Python files in the "filedrop" directory
    install_requires=[
        'qrcode',
        'pypng'
    ],
    entry_points={
        'console_scripts': [
            'filedrop-server=filedrop.__main__:main',  # This points to the main function in __main__.py
        ],
    },
    include_package_data=True,  # Include other files (like style.css, etc.)
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Minimum Python version
    long_description=open('README.md').read(),  # Read the long description from the README
    long_description_content_type='text/markdown',
    license='MIT',  # License for the package
)
