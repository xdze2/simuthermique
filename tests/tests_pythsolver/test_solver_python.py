import numpy as np
from simuthermique.pythsolver.solver_python import solve_model


nodes = [("int", 0.5, 0.2), ("wall", 1.0, 0.1)]

dt = 0.1
N_step = 456
time = np.linspace(0, 100, N_step)

sources = {"ext": np.sin(time)}

internal_links = [
    ("int", "wall", 0.7),
]
external_links = [
    ("int", "ext", 2.0),
]


# drawgraph(nodes, internal_links, external_links, sources)


T = solve_model(nodes, internal_links, external_links, sources, dt)

print(T.shape)
# print(T)
