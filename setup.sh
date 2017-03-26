export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
sudo dpkg-reconfigure locales

sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv python3-setuptools

git clone https://github.com/linkfloyd/linkfloyd-api.git
cd linkfloyd-api/
python -m venv .env
source .env/bin/activate
pip3 install wheel
pip3 install -r requirements.txt
hug -f main.py
