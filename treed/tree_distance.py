from typing import Tuple, Mapping, List, Optional, Callable
from dataclasses import dataclass, field
import numpy as np
from .tree import Node, Tree


@dataclass
class TreeMapping:
    """Note: The responsibility of keeping track of the
        source/target tree pairs is delegated."""
    deleted_nodes: List[int] = field(default_factory=list)
    inserted_nodes: List[int] = field(default_factory=list)
    modified_nodes: List[Tuple[int, int]] = field(default_factory=list)

def compose_tree_mappings(m1: TreeMapping, m2: TreeMapping) -> TreeMapping:
    return TreeMapping(
        m1.deleted_nodes+m2.deleted_nodes,
        m1.inserted_nodes+m2.inserted_nodes,
        m1.modified_nodes+m2.modified_nodes)

@dataclass
class Item:
    value: float
    mapping: Optional[TreeMapping] = None

    def __add__(self, other: 'Item'):
        return Item(self.value+other.value,
                    compose_tree_mappings(self.mapping, other.mapping))

    def __lt__(self, other: 'Item'):
        return self.value < other.value


ForestDistKey = Tuple[int, int, int, int]
ForestDistVal = int | float | Item

TreeDistKey = Tuple[int, int]
TreeDistVal = ForestDistVal


def get_lr_keyroots(t: Tree):
    left_leaf_indices = np.array(t.leftmost_leaf_index)
    b = np.triu(
        left_leaf_indices[:, None] == left_leaf_indices[None, :],
        k=1
    )

    return np.where(~ b.any(axis=-1)) [0]


def _wrap_cost_fn(fn, key):
    def wrapped_fn(*args, **kwargs):
        val = fn(*args, **kwargs)
        mapping_kwargs = {
            f'{key}_nodes': [args[:2] if key == 'modified' else args[0]]
        }
        mapping = TreeMapping(**mapping_kwargs)
        return Item(val, mapping)
    return wrapped_fn
    

def return_mapping(fn):
    """Modify the cost functions to box both the cost, and the action incurring that cost"""
    def wrapped_fn(*args, **kwargs):
        if kwargs.get('return_mapping', False):
            kwargs['delete_node_cost_fn'] = _wrap_cost_fn(
                kwargs.get('delete_node_cost_fn', lambda i, t: 1), 'deleted')
            kwargs['insert_node_cost_fn'] = _wrap_cost_fn(
                kwargs.get('insert_node_cost_fn', lambda i, t: 1), 'inserted')
            kwargs['modify_node_cost_fn'] = _wrap_cost_fn(
                kwargs.get('modify_node_cost_fn', lambda i, j, t1, t2: 1), 'modified')
        return fn(*args, **kwargs)
    return wrapped_fn


@return_mapping
def forest_distance(
    i: int, j: int,
    t1: Tree, t2: Tree,
    treedist_cache: Mapping[ForestDistKey, ForestDistVal],
    delete_node_cost_fn: Callable[[int, Tree], float] =lambda i, t: 1,
    insert_node_cost_fn: Callable[[int, Tree], float] = lambda i, t: 1,
    modify_node_cost_fn: Callable[[int, int, Tree, Tree], float] = lambda i, j, t1, t2: 1,
    return_mapping: bool = False
) -> Mapping[ForestDistKey, ForestDistVal]:
    """Compute the distance between relevant subforests."""

    empty = (-1, -1)  # store the empty tree has an invalid range

    # initialize the forest_distance with the empty case
    forest_dist: Mapping[ForestDistKey, ForestDistVal] = { 
        (*empty, *empty): Item(0., TreeMapping()) if return_mapping else 0.
    }
    
    def get_forest_dist(*k: ForestDistKey) -> ForestDistVal:
        """Adds a guard for the case where start > end in range"""
        a, b, c, d = k
        if a > b: a, b = empty
        if c > d: c, d = empty
        return forest_dist[(a, b, c, d)]

    # Find the left most leaf indices of the range stops
    li = t1.leftmost_leaf_index[i]
    lj = t2.leftmost_leaf_index[j]

    # initialize the base cases which give the cost of transforming
    # each forest to the empty case
    for i1 in range(li, i+1):
        forest_dist[(li, i1, *empty)] = get_forest_dist(li, i1-1, *empty) \
            + delete_node_cost_fn(i1, t1)
    for j1 in range(lj, j+1):
        forest_dist[(*empty, lj, j1)] = get_forest_dist(*empty, lj, j1-1) \
            + insert_node_cost_fn(j1, t2)
        
    for i1 in range(li, i+1):
        for j1 in range(lj, j+1):
            li1 = t1.leftmost_leaf_index[i1]
            lj1 = t2.leftmost_leaf_index[j1]
            # del T1[i1]
            opt1 = get_forest_dist(li, i1-1, lj, j1) + delete_node_cost_fn(i1, t1)
            # insert T2[j1]
            opt2 = get_forest_dist(li, i1, lj, j1-1) + insert_node_cost_fn(j1, t2)
            opt3 = (
                # modify T1[i1] -> T2[j1]
                get_forest_dist(li, i1-1, lj, j1-1) + modify_node_cost_fn(i1, j1, t1, t2)
                if li1 == li and lj1 == lj
                # or compose the mapping from T[li:li]-1 -> T[lj:lj-1]
                # with the mapping from T[i1] to T[j1]
                else get_forest_dist(li, li1-1, lj, lj1-1) + treedist_cache[(i1, j1)]
            )

            fd_insert_key = (li, i1, lj, j1)
            opts = [opt1, opt2, opt3]
            fd_insert_val = min(opts)

            forest_dist[fd_insert_key] = fd_insert_val

            if li1 == li and lj1 == lj:
                # store the tree distance
                treedist_cache[(i1, j1)] = fd_insert_val

    return forest_dist


def tree_distance(
    t1: Tree, t2: Tree, 
    delete_node_cost_fn: Callable[[int, Tree], float] = lambda i, t: 1,
    insert_node_cost_fn: Callable[[int, Tree], float] = lambda i, t: 1,
    modify_node_cost_fn: Callable[[int, int, Tree, Tree], float] = lambda i, j, t1, t2: 1,
    return_mapping: bool = False
) -> Mapping[TreeDistKey, TreeDistVal]:
    """Compute the tree distance between two trees.
    Args:
        t1: The 'source' tree for the mapping
        t2: The 'target' tree for the mapping
        delete_node_cost_fn: A callable, giving the cost of deleting
            the `i`th node of tree `t1`.
        insert_node_cost_fn: A callable giving the cost of inserting 
            node `j` into tree `t2`.
        modify_node_cost_fn: A callable incurred from transforming
            node `i` of `t1` to the `j`th node of `t2`.
        return_mapping: An optional boolean, default `False` giving
            whether to return the mapping that achieves the tree distance
            along with the value.
    """
    lr_keyroots1 = get_lr_keyroots(t1)
    lr_keyroots2 = get_lr_keyroots(t2)

    td = {}
    for i in lr_keyroots1:
        for j in lr_keyroots2:
            _ = forest_distance(i, j, t1, t2, td,
                                delete_node_cost_fn=delete_node_cost_fn,
                                insert_node_cost_fn=insert_node_cost_fn,
                                modify_node_cost_fn=modify_node_cost_fn,
                                return_mapping=return_mapping)
    
    return td


def pad_trees(t1: Tree,
              t2: Tree,
              mapping: TreeMapping,
              pad_token: str = '_'):
    """Pad two mapped trees to that they have common shape."""
    nodes_1, parent_1 = [], []
    nodes_2, parent_2 = [], []

    deleted = [i for i in mapping.deleted_nodes]
    inserted = [j for j in mapping.inserted_nodes]
    modified = [(i, j) for (i, j) in mapping.modified_nodes]

    mapping_1, mapping_2 = {}, {}

    i = 0
    while i < len(t1.nodes):
        if len(deleted) > 0 and deleted[0] == i:
            _ = deleted.pop(0)
            nodes_1.append(t1.nodes[i].name)
            mapping_1[i] = len(nodes_1) - 1  # store where the node got mapped to

            pi = t1.parent[i]
            parent_1.append(pi)

            nodes_2.append(pad_token)
            parent_2.append(None)
    
        else:
            i1, j1 = modified.pop(0)
            while len(inserted) > 0 and inserted[0] < j1:
                j = inserted.pop(0)

                nodes_1.append(pad_token)
                parent_1.append(None)

                nodes_2.append(t2.nodes[j].name)
                mapping_2[j] = len(nodes_2)-1
                parent_2.append(t2.parent[j])
            
            nodes_1.append(t1.nodes[i1].name)
            mapping_1[i1] = len(nodes_1) - 1

            pi1 = t1.parent[i1]
            parent_1.append(pi1 if pi1 == -1 else pi1)

            nodes_2.append(t2.nodes[j1].name)
            mapping_2[j1] = len(nodes_2)-1
            parent_2.append(t2.parent[j1])

        i+=1

    for par, map in zip([parent_1, parent_2, mapping_1, mapping_2]):
        # Now loop back over the parents (extra O(n) cost)
        for i, pi in enumerate(par):
            if pi is None or pi == -1:
                continue
        par[i] = map[pi]
    
    merged_parent = [
        b if a is None else a for (a, b) in zip(parent_1, parent_2)
    ]

    return nodes_1, nodes_2, merged_parent


if __name__ == '__main__':
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

    t1 = Tree.from_root(r1)
    t2 = Tree.from_root(r2)

    def modify_node_cost_fn(i: int, j: int, t1: Tree, t2: Tree):
        """Cost incurred if we have to relabel"""
        n1 = t1.nodes[i]; n2 = t2.nodes[j]
        return 0 if n1.name == n2.name else 1

    tree_dist = tree_distance(t1, t2,
                              modify_node_cost_fn=modify_node_cost_fn,
                              return_mapping=True)
    
    td = tree_dist[(len(t1.nodes)-1, len(t2.nodes)-1)]
    print(td)