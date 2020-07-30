# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import numpy as np
import matplotlib.pylab as plt

# %load_ext autoreload
# %autoreload 2

from solver_python import * 
from graphmodel import drawgraph

# +
# ==================
#  Define the model
# ==================

# Nodes: list of tuples [(name, mass, T0) , ...]
# Sources: Dict {name: array (nbr time step), ...}
# Internal links: list ot tuples [(node A, node B, conductance value), ...]
# External links (i.e. with a source):
# list ot tuples [(internal node, source name, conductance value), ...]
# use conductance=None if it is a direct heat source

nodes = [('int',  0.5,  0.2), 
         ('wall', 1.0,  0.1)]

time    = np.linspace(0, 100, 456)
sources = {'ext':np.sin(time)}

internal_links = [('int', 'wall', .7), ]
external_links = [('int', 'ext', 2.0), ]

dt = .1
# -

drawgraph(nodes,
          internal_links,
          external_links,
          sources)

# +
T = solve_model_noOptim(nodes,
                internal_links,
                external_links,
                sources,
                dt)

plt.figure(figsize=(12, 3))
plt.plot(sources['ext'], label='ext')

for k, (name, _, _) in enumerate(nodes):
    plt.plot(T[k, :], label=name)
    
plt.legend(); plt.xlabel('time');

# +
T = solve_model(nodes,
                internal_links,
                external_links,
                sources,
                dt)

plt.figure(figsize=(12, 3))
plt.plot(sources['ext'], label='ext')

for k, (name, _, _) in enumerate(nodes):
    plt.plot(T[k, :], label=name)
    
plt.legend(); plt.xlabel('time');
# -

# %%timeit
T = solve_model(nodes,
                internal_links,
                external_links,
                sources,
                dt)

# %%timeit
T = solve_model_noOptim(nodes,
                internal_links,
                external_links,
                sources,
                dt)

# %%timeit
A, B =   assemble(nodes,
                internal_links,
                external_links,
                sources)




