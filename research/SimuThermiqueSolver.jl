module SimuThermiqueSolver

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

Model(;dt) = Model(dt,
                   Dict{String,Int64}(),
                   Array{Float64,1}(),
                   [],
                   []);
# -

function get_sparse_K(model::Model)
    I = map(x->x.i, model.K_ijv)
    J = map(x->x.j, model.K_ijv)
    V = map(x->x.v, model.K_ijv)
    n = length(model.M)
    K = sparse(I, J, V, n, n)
    return K
end


function add_simplethermalmass!(model, node_id; thermal_mass)
    if haskey(model.id_to_index, node_id)
        error("""Can't add simple mass: "$node_id", the id already exists""")
    end
    push!(model.M, thermal_mass)
    model.id_to_index[node_id] = length(model.M)
    return node_id
end


function add_wall!(model, wall_id; material, thickness, area)
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
    massth = (material.rho * material.Cp * dx * area * (is_boundary(i) ? 0.5 : 1.0)
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


function add_conductance!(model, id_nodeA, id_nodeB; UA)
    i = model.id_to_index[id_nodeA]
    j = model.id_to_index[id_nodeB]
    
    cells = [(i=i, j=i, v=-UA),
             (i=j, j=j, v=-UA),
             (i=i, j=j, v=+UA),
             (i=j, j=i, v=+UA)] 
    append!(model.K_ijv, cells);
    return nothing
end


function add_convectivesource!(model, node_id; Tsource, hS)
    i = model.id_to_index[node_id]
    push!(model.K_ijv, (i=i, j=i, v=-hS));
    push!(model.S_iv,  (i=i, v=t -> hS*Tsource(t)))  # more generic args?
    return nothing
end


function add_directsource!(model, node_id; flux)
    i = model.id_to_index[node_id]
    push!(model.S_iv, (i=i, v=flux));
    return nothing
end

export Model, Material, add_directsource!, add_convectivesource!, add_conductance!, add_wall!, add_simplethermalmass!


# -- solver --

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
    dt = abs(model.dt)
    I_minus_dtA = factorize(I - theta*dt*A)
    I_plus_dtA = I + (1 - theta)*dt*A;

    function update_S!(S, t)
        fill!(S, 0.0)
        foreach(cell->S[cell.i] += cell.v(t), model.S_iv)
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

    state.T = state.I_minus_dtA \ ( state.I_plus_dtA*state.T + abs(dt)*S_theta )
    
    return state.t, state.T
end

export init_solver, iter!

end  # module