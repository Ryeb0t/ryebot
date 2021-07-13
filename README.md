# Ryebot

This project is a collection of scripts for automated actions on Gamepedia/Fandom wikis, particularly the [Terraria Wiki](https://terraria.fandom.com). It includes a command line tool to start and stop the execution of these scripts.

The project includes a customized version of the [mwcleric package](https://github.com/RheingoldRiver/mwcleric) by RheingoldRiver.


## Prerequisites

Running Ryebot scripts or the command line tool requires a Linux machine with **Ubuntu 20.04**. Windows is currently not supported.


## Installation

Run the following code to install Ryebot:

```
$ sudo apt-get install -y git
$ git clone https://github.com/Ryeb0t/ryebot.git ~/ryebot
$ chmod u+x ~/ryebot/setup_first_install.sh
$ ~/ryebot/setup_first_install.sh
```

This code first installs Git (if not already installed), then clones this repository to the directory `ryebot` in the user's home directory, and lastly executes the [first-install shell script](https://github.com/Ryeb0t/ryebot/blob/main/setup_first_install.sh). That script installs Python 3.8 on the machine, creates a [virtual environment](https://docs.python.org/3/library/venv.html), and installs Ryebot into it. This means that the user's Python installation will remain unaffected by Ryebot and Ryebot's required dependency modules.


## Usage

### Starting the command line tool

Ryebot can be used very easily inside the virtual environment by executing a simple command:

```
$ ryebot
```

This will display a help page with further commands for the different possible actions.

It is important to note that *this will only work inside the virtual environment!* The virtual environment can be entered (or "activated") by running the following command:

```
$ source ~/ryebot/localdata/.ryebotvenv/bin/activate
```

This will replace the default shell prompt with something like this:

```
(.ryebotvenv) user@machine:~$
```

All other commands from outside the virtual environment will still be available and work as expected. The only relevant difference is that the `ryebot` command will be available.

The virtual environment can be exited at any time by running the following command:

```
$ deactivate
```

Exiting the virtual environment will not terminate any running Ryebot scripts, and it can be entered again using the command from above.

### Logging in to a wiki

In order to perform most actions, Ryebot will need to login to the wiki in question. It takes the credentials from a file named `wiki_account_bot.json` in the directory `~/ryebot/localdata/global_config`. This file will need to be created, with the respective username and bot password. This repository comes with an examplary file, which can be edited to include the correct credentials, and then simply be moved to the correct location:

```
$ mv ~/ryebot/wiki_account_example.json ~/ryebot/localdata/global_config/wiki_account_bot.json
```


## Contributing

Contributions to this project are welcome!


## Licensing

This project is licensed under the MIT License.