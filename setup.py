import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

setup(
    name="arvanApi",
    version="0.0.1",

    author="Mahdi Heidari",
    author_email="mahdih3idari@gmail.com",

    description="Simple Arvan api",
    long_description=README,
    long_description_content_type="text/markdown",

    url="https://github.com/mheidari98/arvanApi",

    license='MIT License',

    packages=['arvanApi'],

    extras_require={
        "dev": [
            "pytest >= 3.7",
            "twine"
        ]
    },

    

    install_requires=['requests'],

    classifiers=[
        # https://pypi.org/classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: POSIX :: Linux',        
        "Programming Language :: Python :: 3",
    ],

    python_requires='>=3',
)