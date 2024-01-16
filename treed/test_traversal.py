from typing import Optional
from .traversal import (
    preorder_iter,
    postorder_iter
)
# TODO(dant): Probbly don't want this dependency
from anytree import Node, PreOrderIter, PostOrderIter


r1 = Node(name='f', children=[
    Node(name='d', children=[
        Node(name='a'),
        Node(name='c', children=[
            Node(name='b')
        ])
    ]),
Node(name='e')
]
)

def test_preorder_traversal():
    x = [n.name for n in PreOrderIter(r1)]
    y = [n.name for n in preorder_iter(r1)]
    assert x == y

def test_postorder_traversal():
    x = [n.name for n in PostOrderIter(r1)]
    y = [n.name for n in postorder_iter(r1)]
    assert x == y

def test_projection_traversal():
    x = [
        (n.name, n.parent.name if n.parent else None)
            for n in PostOrderIter(r1)
    ]
    def proj_fn(n: 'Node', i: int, parent: Optional['Node'] = None):
        return (n.name, parent.name if parent else None)
    y = [x for x in postorder_iter(r1, proj_fn)]

    assert x == y
