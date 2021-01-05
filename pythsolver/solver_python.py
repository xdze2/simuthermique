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

import numba as nb
import numpy as np
from scipy.linalg import lu_factor, lu_solve


# +
# to check:

# len(mass) == len(nodes)
# no same id node & source
# no link with unknown node id
# no external link with no node_id
# no internal link with source_id
# all sources have same length
# -

def assemble(nodes,
              internal_links,
              external_links,
              sources):
    """
    Assembles the model matrices
    
    dT/dt = WA x T + WS
     
    return WA and WS matrices
    """
    
    # Assemblage
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
        
    M = np.diag([n[1] for n in nodes])
    W = np.linalg.inv(M)
    
    WA = np.matmul(W, A)
    WS = np.matmul(W, S)
    
    return WA, WS


def solve_model_noOptim(nodes,
                internal_links,
                external_links,
                sources,
                dt):
    nbr_nodes = len(nodes)
    nbr_steps = len( next(iter(sources.values())) )
    
    WA, WS = assemble(nodes, internal_links, external_links, sources)
    
    theta = .5
    I = np.eye(nbr_nodes)
    I_minus_A = I - theta*dt*WA
    I_plus_A = I + (1-theta)*dt*WA
    delta_S = theta*WS[:, :-1] + (1 - theta)*WS[:, 1:]
       
    # Solver loop

    T = np.zeros((nbr_nodes, nbr_steps))
    T[:, 0] = np.array( [n[2] for n in nodes] )   
    for k in range(1, nbr_steps):
        b = np.matmul(I_plus_A, T[:, k-1]) + delta_S[:, k-1]*dt
        T[:, k] = np.linalg.solve(I_minus_A, b)

    return T


def solve_model(nodes,
                internal_links,
                external_links,
                sources,
                dt):
        
    nbr_nodes = len(nodes)
    nbr_steps = len( next(iter(sources.values())) )
    
    WA, WS = assemble(nodes, internal_links, external_links, sources)
    
    h = dt/2
    I = np.eye(nbr_nodes)

    I_minus_A = I - h*WA
    I_plus_A  = I + h*WA
    delta_S   = (WS[:, :-1] + WS[:, 1:])*h
    
    II  = np.linalg.inv(I_minus_A)
    III = np.matmul(II, I_plus_A)
    dd  = np.matmul(II, delta_S)
    
    # Solver loop
    T = np.zeros((nbr_nodes, nbr_steps))
    T[:, 0] = np.array( [n[2] for n in nodes] )
    
    return full_loop2(T, III, dd)


@nb.jit(nopython=True)
def full_loop2(T, III, dd):
    for k in range(1, dd.shape[1]+1):
        T[:, k] = np.dot(III, T[..., k-1]) + dd[..., k-1]
    return T

# +
#@nb.jit(nopython=True)
#def prod_sum(III, Tkm1, dd):
#    return np.dot(III, Tkm1) + dd
#
#@nb.jit(nopython=True)
#def full_loop(T, III, dd, nbr_steps):
#    for k in range(1, nbr_steps):
#        T[:, k] = prod_sum(III, T[..., k-1], dd[..., k-1])
#    return T

# +
## benchmark
# with time = np.linspace(0, 100, 456)
# 5.96 ms ± 54.1 µs pe   start
# 5.12 ms with S_avg
# 5.25 ms with LU solve
# 2.05 ms  with inverse first
# 1.37 ms ± 7.13 µs per loop  with inverse, and develloment
# 909 µs  with numba inside the loop with @, same with dot()
# 232 µs ± 601 ns per loop   full loop with numba (with inner loop numba too)
# 216 µs ± 1.47 µs    full loop with numba (one function only)
# ---
# 43.5 µs  without the loop

    #for k in range(1, nbr_steps):
    #    #b = np.matmul(I_plus_A, T[:, k-1]) + delta_S[:, k-1]*dt
    #    #T[:, k] = np.linalg.solve(I_minus_A, b)
    #    #T[:, k] = np.matmul(II, b)
    #    #T[:, k] = lu_solve((lu, piv), b)
    #    ##T[:, k] = np.matmul(III, T[:, k-1]) + dd[:, k-1]
    #    T[:, k] = prod_sum(III, T[..., k-1], dd[..., k-1])
# -






