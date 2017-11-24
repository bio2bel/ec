# -*- coding: utf-8 -*-

import logging
import sys

import click

from .constants import DEFAULT_CACHE_CONNECTION
from .database import Manager
from .query import write_gene_ec_mapping
from .tree import write_expasy_tree


@click.group()
def main():
    """Tools for writing EC"""
    logging.basicConfig(level=10)


@main.command()
@click.option('-e', '--eoutput', type=click.File('w'), default=sys.stdout)
def write(eoutput):
    write_expasy_tree(eoutput)


@main.command()
@click.option('-bo', '--boutput', type=click.File('w'), default=sys.stdout)
def write_bel(boutput):
    write_gene_ec_mapping(boutput)


@main.command()
@click.option('-c', '--connection', help='Defaults to {}'.format(DEFAULT_CACHE_CONNECTION))
def populate(connection):
    """Populates the database"""
    m = Manager(connection=connection)
    m.populate()


@main.command()
@click.option('-c', '--connection', help='Defaults to {}'.format(DEFAULT_CACHE_CONNECTION))
def drop(connection):
    """Drops the database"""
    m = Manager(connection=connection)
    m.drop_all()


@main.command()
@click.option('-c', '--connection', help='Defaults to {}'.format(DEFAULT_CACHE_CONNECTION))
def web(connection):
    """Run the web app"""
    from .web import create_app
    app = create_app(connection=connection)
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
