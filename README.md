# treed

[The Tree-to-tree correction problem, Kho-Chung Tai](https://dl.acm.org/doi/10.1145/322139.322143)

[Simple Fast Algorithms for the Editing Distance between Trees and Related Problems, K. Zhang and D. Shasha](https://epubs.siam.org/doi/10.1137/0218082)



```python
def modify_node_cost_fn(
    i: int, 
    j: int,
    t1: Tree,
    t2: Tree
) -> int:
    """Cost incurred if we have to relabel"""
    n1 = t1.nodes[i]; n2 = t2.nodes[j]
    return 0 if n1.name == n2.name else 1

tree_dist = tree_distance(
    t1, t2,
    modify_node_cost_fn=modify_node_cost_fn,
    return_mapping=True)
    
td = tree_dist[(len(t1.nodes)-1, len(t2nodes)-1)]
```