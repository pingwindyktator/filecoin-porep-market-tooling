import click

from cli import utils
from cli.commands.admin import _utils as admin_utils


@click.command(hidden=True)
def get_devnet_sps():
    click.echo(utils.json_pretty(admin_utils.get_devnet_sps()))
