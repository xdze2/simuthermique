# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,jl:light
#     text_representation:
#       extension: .jl
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.4
#   kernelspec:
#     display_name: Julia 1.3.0
#     language: julia
#     name: julia-1.3
# ---

using LinearAlgebra
using SparseArrays

# +
"""
Thermal Properties of material

        k      thermal conductivity, W/m2/K  
        rho    density, kg/m3  
        Cp     specific heat, J/kg  
        alpha  thermal diffusivity, m2/s
"""
struct Material
    k     ::Float64
    rho   ::Float64
    Cp    ::Float64
    alpha ::Float64
end

Material(k, rho, Cp) = Material(k, rho, Cp, k/(rho*Cp));
# -

clay = Material(1.28, 880.0, 1450.0) # Clay

# ## v2

# +
""" 
    equation
        M dT/dt = K T  +  S(t)
"""
struct Model
    dt          ::Float64            # time step, seconds
    id_to_index ::Dict{String, Int64}
    M           ::Array{Float64,1}   # thermal mass of each nodes
    K_ijv  ::Array{NamedTuple{(:i,:j,:v),Tuple{Int64,Int64,Float64}}, 1}# Array of named tuple (i, j, value)
    S_iv  #sources -- array of [(idx, function(t)), ()...]
end

Model(dt) = Model(dt,
                  Dict{String,Int64}(),
                  Array{Float64,1}(),
                  [],
                  []);
# -
function add_simplethermalmass!(model, node_id, th_mass)
    if haskey(model.id_to_index, node_id)
        error("""Can't add simple mass: "$node_id", the id already exists""")
    end
    push!(model.M, th_mass)
    model.id_to_index[node_id] = length(model.M)
    return node_id
end

# test
m = Model(5*60)
add_simplethermalmass!(m, "1", 0.1)
add_simplethermalmass!(m, "2", 0.2)



function add_wall!(model, wall_id, material, thickness, surface)
    # Mesh
    delta_x = sqrt( model.dt * material.alpha )
    N = 1 + Int(ceil( thickness/delta_x ))
    dx = thickness / N
    
    # Register surfaces node index
    i_ext = length(model.M) + 1
    i_int = length(model.M) + N
    
    id_ext = "$(wall_id)_ext"
    id_int = "$(wall_id)_int"
    if haskey(model.id_to_index, id_ext) || haskey(model.id_to_index, id_int)
        error("""Can't add wall: "$wall_id", the id already exists""")
    end
    model.id_to_index[id_ext] = i_ext
    model.id_to_index[id_int] = i_int
    
    is_boundary(i) = (i == i_ext || i == i_int)
    
    # Thermal mass
    massth = (material.rho * material.Cp * dx * surface * (is_boundary(i) ? 0.5 : 1.0)
              for i in i_ext:i_int)
    append!(model.M, massth)

    # Konduction
    k_dx = material.k / dx
    diagonal   = ( (i=i,   j=i,   v=(is_boundary(i) ? -1.0 : -2.0)*k_dx)
                  for i in i_ext:i_int )
    upper_diag = ( (i=i,   j=i+1, v=+k_dx) for i in i_ext:i_int-1 )
    lower_diag = ( (i=i+1, j=i,   v=+k_dx) for i in i_ext:i_int-1 )
    cells = Iterators.flatten((diagonal, upper_diag, lower_diag))
    append!(model.K_ijv, cells) 

    return (ext=id_ext, int=id_int)
end

function get_sparse_K(model::Model)
    I = map(x->x.i, m.K_ijv)
    J = map(x->x.j, m.K_ijv)
    V = map(x->x.v, m.K_ijv)
    n = length(m.M)
    K = sparse(I, J, V, n, n)
    return K
end

# +
m = Model(5*60)

air_int = add_simplethermalmass!(m, "T_air_int", 24.2)

wall1 = add_wall!(m, "wall1", clay, .20, 4.)

sol = add_simplethermalmass!(m, "T_sol", 4.2)

wall1 = add_wall!(m, "wall2", clay, .10, 4.)
# -

typeof(m.K_ijv)

function add_conductance!(model, id_nodeA, id_nodeB, UA)
    i = model.id_to_index[id_nodeA]
    j = model.id_to_index[id_nodeB]
    
    cells = [(i=i, j=i, v=-UA),
             (i=j, j=j, v=-UA),
             (i=i, j=j, v=+UA),
             (i=j, j=i, v=+UA)] 
    append!(model.K_ijv, cells);
    return nothing
end

add_conductance!(m, "ez", wall1[2], 0.1)

add_conductance!(m, air_int, wall1.ext, 0.1)

function add_convectivesource(model, node_id, Tsource, hS)
    i = model.id_to_index[node_id]
    push!(model.K_ijv, (i=i, j=i, v=-hS));
    push!(model.S_iv,  (i=i, v=t -> hS*Tsource(t)))  # more generic args?
    return nothing
end

T_ext(t) = cos(t)
add_convectivesource(m, wall1.int, T_ext, 1.5)

m.S_iv

mutable struct State
    update_S!   ::Function
    T           ::Array{Float64,1}
    dt          ::Float64
    t           ::Float64
    theta       ::Float64
    I_minus_dtA #::LDLt{Float64,Tridiagonal{Float64,Array{Float64,1}}}
    I_plus_dtA  #::Tridiagonal{Float64,Array{Float64,1}}
    St          ::Array{Float64,1}
end

function init_solver(model; T0=nothing, theta=0.5, t=0.0)
    M = Diagonal(model.M);
    K = get_sparse_K(model);

    A = M\K;
    dt = model.dt
    I_minus_dtA = factorize(I - theta*dt*A)
    I_plus_dtA = I + (1 - theta)*dt*A;

    function update_S!(S, t)
        fill!(S, 0.0)
        foreach(cell->S[cell.i] += cell.v(t), m.S_iv)
        S[:] = M \ S
    end    
    St = zeros(length(model.M));
    update_S!(St, t)
    
    if isnothing(T0)
        T0 = zeros(length(model.M))
    end
    
    return State(
        update_S!,
        T0,
        model.dt,
        t,
        theta,
        I_minus_dtA,
        I_plus_dtA,
        St
    )
end

function iter!(state)
    theta = state.theta
    dt = state.dt
    
    state.t += dt
    old_S = state.St
    state.update_S!(state.St, state.t)
    S_theta = theta*state.St + (1 - theta)*old_S

    state.T = state.I_minus_dtA \ ( state.I_plus_dtA*state.T + dt*S_theta )
    
    return state.t, state.T
end

# ## Test with soil model

using Plots

min = 60.0
hour = 60min
day = 34hour

# +
clay = Material(1.28, 880.0, 1450.0) # Clay
m = Model(2hour)

soil = add_wall!(m, "soil", clay, 6.0, 1.)

T_ext(t) = sin(2pi/(7day)*t)
add_convectivesource(m, soil.ext, T_ext, 1.0)
add_convectivesource(m, soil.int, t->0.0, 2.0)
# -

state = init_solver(m);

save = [1, 4, 8];
n_iter = 300;

sol = zeros(n_iter, length(save))
for k in 1:n_iter
    iter!(state)
    sol[k, :] = state.T[save]
end
plot(sol)
