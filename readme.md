Quick readme, will be fixed later.

1. Be sure that Python3 is installed on your system. Use brew install python3 or apt-get install python3 if you're using Linux distros.
2. Clone this repository.
3. Optionally create virtualenvironment to install packages:

    sudo easy_install3.6 pip
    sudo pip3 install virtualenv virtualenvwrapper
    mkvirtualenv linkfloyd

4. Install packages:

    pip install -r requirements.txt

5. Run server:

    hug -f main.py
    

