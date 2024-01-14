from typing import List
from dataclasses import dataclass, field

# TODO(dant): Really we want this
#   to be interface like?
@dataclass
class Node:
    children: List['Node']

@dataclass
class Tree:
    """Represents a tree as an array of nodes, and index pointers to their parents."""
    nodes: List['Node']
    parent_indices: List[int]
    order: str = 'post'
