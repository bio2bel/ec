# -*- coding: utf-8 -*-

import logging
import sys

import click

from .constants import DEFAULT_CACHE_CONNECTION
from .manager import Manager


@click.group()
@click.option('-c', '--connection', help='Defaults to {}'.format(DEFAULT_CACHE_CONNECTION))
@click.pass_context
def main(ctx, connection):
    """ExPASy to BEL"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    ctx.obj = Manager(connection=connection)


@main.command()
@click.pass_obj
def populate(manager):
    """Populates the database"""
    manager.populate()


@main.command()
@click.option('-y', '--yes', is_flag=True)
@click.pass_obj
def drop(yes, manager):
    """Drops the database"""
    if yes or click.confirm('Drop database?'):
        manager.drop_all()


@main.command()
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
@click.pass_obj
def write_bel_namespace(manager, output):
    """Write the BEL namespace"""
    manager.write_bel_namespace(output)


@main.command()
@click.pass_obj
def deploy_bel_namespace(manager):
    """Deploy the BEL namespace"""
    manager.deploy_bel_namespace()


@main.command()
@click.option('-v', '--debug', is_flag=True)
@click.option('-p', '--port')
@click.option('-h', '--host')
@click.pass_obj
def web(manager, debug, port, host):
    """Run the web app"""
    from .web import get_app
    app = get_app(connection=manager, url='/')
    app.run(host=host, port=port, debug=debug)


@main.group()
def enzyme():
    """Enzyme utils"""


@enzyme.command()
@click.argument('expasy_id')
@click.pass_obj
def get(manager, expasy_id):
    m = manager.get_enzyme_by_id(expasy_id)
    click.echo('Enzyme class: {}'.format(m.expasy_id))
    click.echo('Description: {}'.format(m.description))


if __name__ == '__main__':
    main()
