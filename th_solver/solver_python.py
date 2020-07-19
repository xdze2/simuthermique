import numpy as np

# +
# model validity check:
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
        if conductance:
            A[i, i] -= conductance
            S[i, :] += conductance*sources[ext]
        else:
            S[i, :] += sources[ext]

    M = np.diag([n[1] for n in nodes])
    W = np.linalg.inv(M)

    WA = np.matmul(W, A)
    WS = np.matmul(W, S)
    I = np.eye(nbr_nodes)

    theta = .5
    I_minus_A = I - theta*dt*WA
    I_plus_A = I + (1-theta)*dt*WA
    delta_S = theta*S[:, :-1] + (1 - theta)*WS[:, 1:]

    # Solver loop
    T = np.zeros((nbr_nodes, nbr_steps))
    T[:, 0] = np.array( [n[2] for n in nodes] )
    for k in range(1, nbr_steps):
        b = np.matmul(I_plus_A, T[:, k-1]) + delta_S[:, k-1]*dt
        T[:, k] = np.linalg.solve(I_minus_A, b)

    return T