from .tree import Tree
from anytree import Node

r1 = Node(
    name='i',
    children=[
        Node(
            name='c',
            children=[
                Node(name='a'),
                Node(name='b')
            ]),
        Node(
            name='h',
            children=[
                Node(
                    name='f',
                    children=[
                        Node(name='d'),
                        Node(name='e')
                    ]
                ),
                Node(
                    name='g'
                )
             ])
        ]
)

def test_leftmost_leaf_index():
    tree = Tree.from_root(r1)
    assert tree.leftmost_leaf_index == [0, 1, 0, 3, 4, 3, 6, 3, 0]