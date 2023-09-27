import numpy as np
from simuthermique.pythsolver.solver_python import solve_model

import matplotlib.pyplot as plt


nodes = [("int", 2.5, 1.82), ("wall", 1.0, 0.1)]

dt = 0.1
N_step = 456
time = np.linspace(0, 10, N_step)

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


plt.figure(figsize=(12, 3))
plt.plot(sources["ext"], label="ext")

for k, (name, _, _) in enumerate(nodes):
    plt.plot(T[k, :], label=name)

plt.legend()
plt.xlabel("time")
plt.show()
