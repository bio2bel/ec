from collections import defaultdict
from itertools import chain

from bio2bel_expasy.parser.database import get_expasy_database
from bio2bel_expasy.parser.tree import get_expasy_tree

__all__ = [
    'get_expasy_closed_tree',
]


def _concept(c):
    return (
        c['namespace'],
        c['identifier'],
        c.get('name'),
    )


def get_expasy_closed_tree():
    """Return a mapping from ec-code to list of child concepts (other enzymes, proteins, and domains)."""
    rv = defaultdict(set)
    expasy_database = get_expasy_database()
    expasy_tree = get_expasy_tree()

    for expasy_id, data in expasy_database.items():
        try:
            expasy_tree[data['parent']['identifier']]['children'].append(data['concept'])
        except KeyError:
            print(data)
            raise
        for concept in chain(data['proteins'], data['domains']):
            rv[expasy_id].add(_concept(concept))

    for level in 3, 2, 1:
        for expasy_id, data in expasy_tree.items():
            if data['level'] == level:
                for child_concept in data['children']:
                    rv[expasy_id].add(_concept(child_concept))
                    for grandchild_concept in rv[child_concept['identifier']]:
                        rv[expasy_id].add(grandchild_concept)

    return rv


if __name__ == '__main__':
    import json

    with open('d.json', 'w') as file:
        json.dump(get_expasy_closed_tree(), file, indent=2)
