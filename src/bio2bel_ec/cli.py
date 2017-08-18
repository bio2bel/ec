import sys

import click

from .tree import write_expasy_tree
from .query import write_gene_ec_mapping

@click.group()
def main():
    """Tools for writing EC"""

@main.command()
@click.option('-e', '--eoutput', type=click.File('w'), default=sys.stdout)
def write(eoutput):
    write_expasy_tree(eoutput)

@main.command()
@click.option('-bo', '--boutput', type=click.File('w'), default=sys.stdout)
def write_bel(boutput):
    write_gene_ec_mapping(boutput)
if __name__ == '__main__':
    main()