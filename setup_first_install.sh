# Install Python
sudo apt-get install -y python3.8

# Install virtual environments for Python
sudo apt-get install -y python3.8-venv

# Make a virtual environment and setup the project in it
python3 -m venv ~/ryebot/localdata/.ryebotvenv
source ~/ryebot/localdata/.ryebotvenv/bin/activate
python3 -m pip install ~/ryebot

# Make directory structure
mkdir -p ~/ryebot/localdata/global_config
mkdir -p ~/ryebot/localdata/wikis