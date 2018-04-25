# -*- coding: utf-8 -*-

import sys

import click

from .manager import Manager

main = Manager.get_cli()


@main.command()
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
@click.pass_obj
def write_bel_namespace(manager, output):
    """Write the BEL namespace"""
    manager.write_bel_namespace(output)


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
