import sys

import click

from .tree import write_expasy_tree

@click.group()
def main():
    """Tools for writing EC"""

@main.command()
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
def write(output):
    write_expasy_tree(output)

if __name__ == '__main__':
    main()