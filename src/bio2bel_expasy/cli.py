# -*- coding: utf-8 -*-

import logging

import click

from .constants import DEFAULT_CACHE_CONNECTION
from .manager import Manager


@click.group()
def main():
    """ExPASy to BEL"""
    logging.basicConfig(level=10)


@main.command()
@click.option('-c', '--connection', help='Defaults to {}'.format(DEFAULT_CACHE_CONNECTION))
def populate(connection):
    """Populates the database"""
    m = Manager(connection=connection)
    m.populate()


@main.command()
@click.option('-y', '--yes', is_flag=True)
@click.option('-c', '--connection', help='Defaults to {}'.format(DEFAULT_CACHE_CONNECTION))
def drop(yes, connection):
    """Drops the database"""
    if yes or click.confirm('Drop database?'):
        m = Manager(connection=connection)
        m.drop_all()


@main.command()
@click.option('-c', '--connection', help='Defaults to {}'.format(DEFAULT_CACHE_CONNECTION))
@click.option('-v', '--debug', is_flag=True)
@click.option('-p', '--port')
@click.option('-h', '--host')
def web(connection, debug, port, host):
    """Run the web app"""
    from .web import create_app
    app = create_app(connection=connection, url='/')
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
