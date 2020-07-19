# -*- coding: utf-8 -*-
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

import numpy as np
import matplotlib.pylab as plt



# +
# to check:

# len(mass) == len(nodes)
# no same id node & source
# no link with unknown node id
# no external link with no node_id
# no internal link with source_id
# all sources have same length
# -

def solve_model(nodes,
                internal_links,
                external_links,
                sources,
                dt):
    # Assemblage
    nbr_nodes = len(nodes)
    nbr_steps = len( next(iter(sources.values())) )
    node_idx = {node[0]:index
                for index, node in enumerate(nodes)}

    A = np.zeros((nbr_nodes, nbr_nodes))
    S = np.zeros((nbr_nodes, nbr_steps))

    for node_A, node_B, conductance in internal_links:
        i = node_idx[node_A]
        j = node_idx[node_B]
        A[i, i] -= conductance
        A[j, j] -= conductance
        A[i, j] += conductance
        A[j, i] += conductance

    for node, ext, conductance in external_links:
        i = node_idx[node]
        A[i, i] -= conductance
        S[i, :] += conductance*sources[ext]

    # Solver loop
    M = np.diag([n[1] for n in nodes])
    W = np.linalg.inv(M)
    T_zero = np.array( [n[2] for n in nodes] )

    WA = np.matmul(W, A)
    WS = np.matmul(W, S)
    I = np.eye(nbr_nodes)

    theta = .5

    I_minus_A = I - theta*dt*WA
    I_plus_A = I + (1-theta)*dt*WA

    T = np.zeros((nbr_nodes, nbr_steps))
    T[:, 0] = T_zero

    for k in range(1, nbr_steps):
        delta_S = theta*S[:, k] + (1 - theta)*S[:, k-1]
        b = np.matmul(I_plus_A, T[:, k-1]) + delta_S*dt
        T[:, k] = np.linalg.solve(I_minus_A, b)
        
    return T


# +
nodes = [('int', 0.2,   .2), # name, mass, T0
         ('wall', 0.3, 0.8)]

time = np.linspace(0, 100, 132)
sources = {'ext':np.sin(time)}

internal_links = [('int', 'wall', .7), ]
external_links = [('int', 'ext', 0.2), ] # ext. second

dt = .1

T = solve_model(nodes,
                internal_links,
                external_links,
                sources,
                dt)

# +
plt.plot(sources['ext'], label='ext')

for k, (name, _, _) in enumerate(nodes):
    plt.plot(T[k, :], label=name)
    
plt.legend();
# -
# speed-up
#
# use auto-diff to get gradient (fiting optimisation)
#







