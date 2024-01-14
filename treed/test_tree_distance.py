from .tree import Tree
from .tree_distance import tree_distance

from anytree import Node

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

r2 = Node(
    name='f', children=[
        Node(name='c', children=[
            Node(name='d', children=[
                Node(name='a'),
                Node(name='b')
            ])
        ]),
        Node(name='e')
    ]
)
    

def test_treedistance():
    t1 = Tree.from_root(r1)
    t2 = Tree.from_root(r2)

    def modify_node_cost_fn(i, j, t1, t2):
        return 0 if t1.nodes[i].name == t2.nodes[j].name else 1

    tree_dist = tree_distance(
        t1, t2, 
        modify_node_cost_fn=modify_node_cost_fn)
    
    td = tree_dist[(len(t1.nodes)-1, len(t2.nodes)-1)]
    assert td == 2