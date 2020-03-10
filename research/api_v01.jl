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

# +
struct Material
    """
    Material
    k      thermal conductivity, W/m2/K
    rho    density, kg/m3
    Cp     specific heat, J/kg
    alpha  Thermal diffusivity, 
    """
    k     ::Float64
    rho   ::Float64
    Cp    ::Float64
    alpha ::Float64
end

Material(k, rho, Cp) = Material(k, rho, Cp, k/(rho*Cp))
# -

mat = Material(0.2, 2000, 300)

# +
struct SimpleThermalMass
   mass_th # rhoCp V 
end

struct Wall
   mat       ::Material
   thickness ::Float64
   surface   ::Float64
end

struct Model
    simple_masses
    walls
    sources
    resistances
end

Model() = Model(Dict(), Dict(), Dict(), [])


function add!(m::Model, simplemass::SimpleThermalMass; id=nothing)
    if id == nothing
        id = "node$(length(m.simple_masses)+1)"
        println("create node $id")
    end
    m.simple_masses[id] = simplemass
    return id
end

function add!(m::Model, wall::Wall; id=nothing)
    if id == nothing
        id = "wall$(length(m.simple_masses)+1)"
        println("create a wall named $id")
    end
    m.walls[id] = wall
    return id
end

# +
m = Model()
air_int = SimpleThermalMass(3.5, "air intérieur")
add!(m, air_int; id="air_int")

air_cave = SimpleThermalMass(1.5, "air de la cave")
add!(m, air_cave; id="air_cave")


mur_ext = Wall(mat, 0.30, 4, "un mur")
add!(m, mur_ext)

# +
dt = 5*60.0
nodes_mass = []
M_i, M_j, M_v = [], [], []
id_to_index = Dict{String, Int}()

for (k, (id, thermalmass)) in enumerate(pairs(m.simple_masses))
    id_to_index[id] = k
    push!(nodes_mass, thermalmass.mass_th)
end
last_idx = length(nodes)

for (id, wall) in pairs(m.walls)
    massth, M = constructmesh(wall, dt)
    
    id_left = "$(id)_left"
    id_right = "$(id)_right"
    id_to_index[id_left] = 1 + last_idx
    id_to_index[id_right] = 1 + last_idx + length(massth)
    
    last_idx = id_to_index[id_right]
    
    append!(nodes_mass, massth)
    #push!(nodes, thermalmass.mass_th)
end

N = length(nodes)
M = zeros(N, N)
# -

id_to_index

function constructmesh(wall::Wall, dt)
    """-- Build the adiabatic wall matrix --"""
    delta_x = sqrt( dt * wall.mat.alpha )
    N = 1 + Int(ceil( wall.thickness/delta_x ))
    dx = wall.thickness / N
    
    M = Tridiagonal(ones(N-1), -2.0 * ones(N), ones(N-1));
    #M[1, 1] += -2.0*h_left*dx/mat.k
    #M[1, 2] = 2.0
    #M[end, end] += -2.0*h_right*dx/mat.k
    #M[end, end-1] = 2.0

    M[1, 1] = -1
    M[end, end] = -1
    #A = mat.alpha / dx^2 * M;
    massth = ones(N) * wall.mat.rho * wall.mat.Cp * dx * wall.surface
    massth[1] *= 0.5
    massth[end] *= 0.5
    return massth, (wall.mat.k / dx) * M
end

# ## v2

using LinearAlgebra

# +
struct Material
    """
    Material
    k      thermal conductivity, W/m2/K
    rho    density, kg/m3
    Cp     specific heat, J/kg
    alpha  Thermal diffusivity, 
    """
    k     ::Float64
    rho   ::Float64
    Cp    ::Float64
    alpha ::Float64
end

Material(k, rho, Cp) = Material(k, rho, Cp, k/(rho*Cp))
# -

mat = Material(0.2, 2000, 300)

# +
#  M dT/dt = K T  +  S
struct Model
    nodes   # actually thermal mass
    id_to_index
    walls
    dt ::Float64
    K_i
    K_j
    K_v
    S#sources
    #resistances
end

Model(dt) = Model([], Dict(), Dict(), dt, [], [], [], [])
# -



# +
function add_simplethermalmass!(model, node_id, th_mass)
    # warning if already exist 
    push!(model.nodes, th_mass)
    model.id_to_index[node_id] = length(model.nodes)
    return node_id
end


function add_wall!(model, wall_id, material, thickness, surface)
    # mesh:
    delta_x = sqrt( model.dt * material.alpha )
    N = 1 + Int(ceil( thickness/delta_x ))
    dx = thickness / N
    
    # thermal mass:
    massth = ones(N) * material.rho * material.Cp * dx * surface
    massth[1] *= 0.5
    massth[end] *= 0.5
    
    # warning if already exist 
    id_left = "$(wall_id)_left"
    id_right = "$(wall_id)_right"
    model.id_to_index[id_left] = length(model.nodes) + 1
    
    append!(model.nodes, massth)
    model.id_to_index[id_right] = length(model.nodes)
    
    # Konduction
    ii = collect(model.id_to_index[id_left]:model.id_to_index[id_right])

    # diagonal
    append!(model.K_i, ii)
    append!(model.K_j, ii)
    append!(model.K_v, 2.0*ones(length(ii)))
    # upper diag
    append!(model.K_i, ii[1:end-1])
    append!(model.K_j, ii[2:end])
    append!(model.K_v, -1.0 *ones(length(ii)-1))
    # lower diag
    append!(model.K_i, ii[2:end])
    append!(model.K_j, ii[1:end-1])
    append!(model.K_v, -1.0 *ones(length(ii)-1))

    return id_left, id_right  # nammed tupled ? 
end
# -

m = Model(5*60)

air_int = add_simplethermalmass!(m, "T_air_int", 24.2)

wall1 = add_wall!(m, "wall_ext_int", mat, .20, 4.)

sol = add_simplethermalmass!(m, "T_sol", 4.2)

function add_resistance!(model, id_nodeA, id_nodeB, R)
    i = model.id_to_index[id_nodeA]
    j = model.id_to_index[id_nodeB]
    push!(model.K_i, i)
    push!(model.K_j, j)
    push!(model.K_v, -R)
    
    push!(model.K_i, j)
    push!(model.K_j, i)
    push!(model.K_v, -R)
end

# +
add_resistance!(m, air_int, wall1[2], R)
add_resistance!(m, air_int, wall1[2], h=1.3, surface=24.)

add_source(m, wall1[1])
# -

m.id_to_index

using SparseArrays

K = sparse(Array{Int}(m.K_i), Array{Int}(m.K_j),
            Array{Float64}(m.K_v), length(m.nodes), length(m.nodes));

factorize(K)

typeof(K)

Array(K)


