# treed
Methods to compute the edit distance between (ordered)
trees.


[The Tree-to-tree correction problem, Kho-Chung Tai](https://dl.acm.org/doi/10.1145/322139.322143)

[Simple Fast Algorithms for the Editing Distance between Trees and Related Problems, K. Zhang and D. Shasha](https://epubs.siam.org/doi/10.1137/0218082)

## Specifying the cost function
The problem specification allows for three modifications in
order to transform one tree into another. Deleting an existing node
in the source tree, adding a new node to the target tree, and then
modifying a node by relabeling. 

These are specified by the following arguments to `tree_distance`. Note
that in all of the below the integer variables represent indexes into the
trees nodes in a postorder iteration;
* `delete_node_cost_fn: (i: int, t: Tree) -> int | float` representing the
  cost of deleteing the `i`th node of tree `t`, (in postorder).
* `insert_node_cost_fn: (j: int, t: Tree) -> int | float` represing the
  cost of inserting the `j`th node into tree `t`.
* `modify_node_cost_fn: (i: int, j: int, t1: Tree, t2: Tree) -> int | float`
  the cost of relabelling the `i`th node of `t1` to the `j`th node of `t2`.


```python
def modify_node_cost_fn(
    i: int, j: int, t1: Tree, t2: Tree
) -> int:
    """Cost incurred if we have to relabel"""
    n1 = t1.nodes[i]; n2 = t2.nodes[j]
    return 0 if n1.name == n2.name else 1

tree_dist = tree_distance(
    t1, t2,
    modify_node_cost_fn=modify_node_cost_fn)
    
td = tree_dist[(len(t1.nodes)-1, len(t2nodes)-1)]
```