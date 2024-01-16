from typing import List, Tuple, Mapping
from dataclasses import dataclass, field

# TODO(dant): Really we want this
#   to be interface like?
@dataclass
class Node:
    name: str
    children: List['Node'] = field(default_factory=list)


@dataclass
class Tree:
    """Represents a tree as an array of nodes, and index pointers to their parents."""
    nodes: List[Node]
    leftmost_leaf_index: List[int]
    parent: List[int]

    @property
    def leftmost_leaves(self) -> Mapping[int, int]:
        pass

    @classmethod
    def from_root(clz, root: Node) -> 'Tree':

        parent_indices: List[int] = []

        def _visit_fn(node: Node,
                      idx: int,
                      acc: Tuple[List[Node], List[int]]):
            """Postorder visit to collect the nodes and the index of
            their leftmost leaves."""
            leftmost_index: int | None = None

            child_indices = []
            for i, child in enumerate(node.children):
                idx, li_cand, acc = _visit_fn(child, idx, acc)
                if i == 0:
                    leftmost_index = li_cand
                child_indices.append(idx-1)  # ugly decr

            if leftmost_index is None:
                leftmost_index = idx  # a leaf is its own leftmost leaf
                
            a1, a2 = acc
            a1.append(node)
            a2.append(leftmost_index)

            # initialize the space to record this childs parent
            # when we have it
            parent_indices.append(-1)
            for cidx in child_indices:
                parent_indices[cidx] = idx

            return idx+1, leftmost_index, (a1, a2)
        
        _, _, acc = _visit_fn(root, 0, ([], []))
        return Tree(*acc, parent=parent_indices)

