# How to run dev server on Ubuntu 16.10?

First of all you have to be sure that you've installed Python3, and have support for virtualenvironments for Python.

Install Python3:

    $ sudo apt-get update
    $ sudo apt-get install -y python3.6

Install pip, virtualenv:

    $ sudo apt-get install -y python3-pip
    $ sudo apt-get install -y python3-venv

Create a virtualenvironment to install python packages, you can put it to ~/.env/LF/

    $ mkdir ~/.env/
    $ python3 -m LF ~/.env/

Change your environment to newly created one. Before running development server you have to change your environment too:

    $ source ~/.env/LF/bin/activate


Now you can install requirements:

    $ pip3 install -r requirements.txt

And run the development server:

    $ hug -f main.py
