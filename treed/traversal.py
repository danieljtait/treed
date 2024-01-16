from typing import Callable, Optional
from .tree import Node

def preorder_iter(
    root: Node,
    apply_fn: Optional[Callable] = None
):
    if apply_fn is None:
        apply_fn = lambda n, i, p: n
    idx = 0
    def _visit_fn(node: Node, parent: Optional[Node] = None):
        nonlocal idx
        node_idx = idx
        idx += 1
        yield apply_fn(node, node_idx, parent)
        for child in node.children:
            yield from _visit_fn(child, node)
    return _visit_fn(root)


def postorder_iter(
    root,
    apply_fn: Optional[Callable] = None
):
    """Post order iteration of a tree.
    
    Args:
        root: A node instance giving the root
          of the node
        apply_fn: An optional projection
          function used to determine what should
          be yielded at each node.
    """
    if apply_fn is None:
        apply_fn = lambda n, i, p: n

    idx = 0
    def _visit_fn(node: Node, parent: Optional[Node] = None):
        nonlocal idx
        for child in node.children:
            yield from _visit_fn(child, node)
        yield apply_fn(node, idx, parent)
        idx += 1
    return _visit_fn(root)