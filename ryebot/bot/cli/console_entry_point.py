import sys
from importlib import metadata

import click

from ryebot.bot.cli.daemon_manager import start_daemon, log_command
from ryebot.bot.cli.status_displayer import StatusDisplayer
from ryebot.bot.cli.wiki_manager import display_wiki_list, add_wiki, remove_wiki, go_online_on_wiki, go_offline_on_wiki
from ryebot.bot.scripts import __availablescripts__


# allow using both "-h" and "--help" for help (default is only "--help")
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS, help='Welcome to the Ryebot menu! Specify one of the commands below to perform an action.\n\nEach command has a "-h" option for help about its usage.')
@click.version_option(metadata.version('ryebot'), '-v', '--version') # enable version option
def main():
    """This is the entry point function called from the command line via `$ ryebot`, as defined in `setup.py`."""
    # code here is *always* executed when the command "ryebot" is called from the command line, no matter the arguments and options
    start_daemon()
    log_command(sys.argv)


@click.group(context_settings=CONTEXT_SETTINGS, help='Use this menu to display the wikis that the bot has access to, and to add or remove wikis from that list.\n\nEach command has a "-h" option for help about its usage.', short_help='Manage the wikis that the bot has access to.')
def wiki():
    """Entry function into the "wiki" sub-group. Executed when "$ ryebot wiki" is called."""
    pass



@click.command(context_settings=CONTEXT_SETTINGS, name='status')
@click.option('-w', '--wiki', multiple=True, help='Display status only for this wiki (can be used multiple times).')
def main_status(wiki):
    """Display the online/offline status of the bot."""
    StatusDisplayer(wiki).display()


@click.command(context_settings=CONTEXT_SETTINGS, name='list')
def main_list():
    """List all available scripts."""
    click.echo('\n'.join((
        'These are the names of the available scripts:',
        '    '.join(__availablescripts__),
        'Use "ryebot scriptinfo" to get information about a script, or "ryebot start" or "ryebot stop" to start/stop one.'
    )))


@click.command(context_settings=CONTEXT_SETTINGS, name='scriptinfo')
@click.option('-s', '--scriptname', required=True, help='Name of the script for which to display info')
def main_scriptinfo(scriptname):
    """Display information about a script."""
    if scriptname not in __availablescripts__:
        click.echo(f'The script "{scriptname}" is not available. See "ryebot list" for a list of available scripts.')
    else:
        click.echo(f'This is some info about the script "{scriptname}".')


@click.command(context_settings=CONTEXT_SETTINGS, name='up', no_args_is_help=True)
@click.option('-w', '--wiki', multiple=True, help='Wiki on which to go online (can be used multiple times).')
@click.option('-a', '--all', is_flag=True, help='Go online on all wikis.')
def main_up(wiki, all):
    """Go online on a wiki."""
    go_online_on_wiki(wiki, all)


@click.command(context_settings=CONTEXT_SETTINGS, name='down', no_args_is_help=True)
@click.option('-w', '--wiki', multiple=True, help='Wiki on which to go offline (can be used multiple times).')
@click.option('-a', '--all', is_flag=True, help='Go offline on all wikis.')
def main_down(wiki, all):
    """Go offline on a wiki."""
    go_offline_on_wiki(wiki, all)


@click.command(context_settings=CONTEXT_SETTINGS, name='start')
@click.option('-s', '--scriptname', type=click.Choice(__availablescripts__, case_sensitive=False), prompt='Name of the script to start')
@click.option('-w', '--wiki', prompt='Wiki to start the script on')
def main_start(scriptname, wiki):
    """Start a script."""
    click.echo(f'Starting the "{scriptname}" script on the "{wiki}" wiki...')



@click.command(context_settings=CONTEXT_SETTINGS, name='list')
@click.option('-c', '--count', help='Display only the number of wikis.', is_flag=True)
def wiki_list(count):
    """Display a list of wikis that the bot has access to."""
    display_wiki_list(count)


@click.command(context_settings=CONTEXT_SETTINGS, name='add')
@click.option('-n', '--name', prompt='Name of the wiki')
def wiki_add(name):
    """Grant the bot access to a new wiki."""
    add_wiki(name)


@click.command(context_settings=CONTEXT_SETTINGS, name='remove')
@click.option('-n', '--name', prompt='Name of the wiki')
@click.confirmation_option('-y', '--yes', prompt='Are you sure you want to withdraw access from this wiki? This will permanently delete all local information that the bot has collected about the wiki, such as logs about script executions on the wiki.')
def wiki_remove(name):
    """Withdraw access to a wiki from the bot."""
    remove_wiki(name)


# register the command group structure:
# all commands for "$ ryebot"
main.add_command(main_status)
main.add_command(main_list)
main.add_command(main_scriptinfo)
main.add_command(main_up)
main.add_command(main_down)
main.add_command(main_start)
main.add_command(wiki)

# all commands for "$ ryebot wiki"
wiki.add_command(wiki_list)
wiki.add_command(wiki_add)
wiki.add_command(wiki_remove)
