# a Python Thermal dynamic solver

solve "electric circuit like" dynamic thermal model


## Model definition

* Nodes: list of tuples [(node id, mass, T0) , ...]
* Sources: Dict {name: array (nbr time step), ...}
* Internal links: list ot tuples [(node A, node B, conductance value), ...]
* External links (i.e. with a source):
* list ot tuples [(internal node, source name, conductance value), ...]
* use conductance=None if it is a direct heat source
* dt: time step value


## Graph the model

- using graphviz

![example graph](example_graph.svg)