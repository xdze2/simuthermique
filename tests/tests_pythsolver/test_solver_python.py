import numpy as np
from simuthermique.pythsolver.solver_python import (
    ThermalMassNode,
    ConductionLink,
    ExternalNode,
    SimpleThermalModel,
    DirectSource,
)


def test_SimpleThermalModel():
    model = SimpleThermalModel(
        internal_nodes=[ThermalMassNode("one", 1, 10), ThermalMassNode("two", 1.6, 10)],
        links=[ConductionLink("one", "two", 1), ConductionLink("two", "ext", 0.5)],
        external_nodes=[ExternalNode("ext", lambda t: 20)],
    )

    K = model.assemble_K()
    assert K.shape == (2, 2)
    np.testing.assert_array_almost_equal(K, [[-1, 1], [1, -1]])

    S = model.assemble_S(1)
    print(S)
    np.testing.assert_array_almost_equal(S, [0, 10])

    # model.draw_graph()


def test_SimpleThermalModel_cosinus():
    mass = 25
    phi0 = 2
    omega = 0.5

    Tzero = 0.5
    T_amp = phi0 / (mass * omega)

    print(f"T_amp=", T_amp)

    model = SimpleThermalModel(
        internal_nodes=[ThermalMassNode("one", mass, Tzero)],
        direct_sources=[DirectSource("one", lambda t: phi0 * np.cos(omega * t))],
    )

    period = 2 * np.pi / omega
    dt = period / 1000
    nbr_step = 3000
    T = model.solve(dt, nbr_step, 0)

    t = np.linspace(0, dt * nbr_step, nbr_step)
    T_theo = T_amp * np.sin(omega * t) + Tzero

    np.testing.assert_almost_equal(T_theo, T[0, :], decimal=2)


def test_SimpleThermalModel_mixed():
    mass = 15
    phi0 = 2
    omega = 0.5
    h = 0.5
    Tzero = -0.5
    T_ext = 10

    model = SimpleThermalModel(
        internal_nodes=[ThermalMassNode("one", mass, Tzero)],
        external_nodes=[ExternalNode("ext", lambda t: T_ext)],
        links=[ConductionLink("ext", "one", h)],
        direct_sources=[DirectSource("one", lambda t: phi0 * np.cos(omega * t))],
    )

    period = 2 * np.pi / omega
    dt = period / 500
    nbr_step = 50
    T = model.solve(dt, nbr_step, 1)

    t = np.linspace(0, dt * nbr_step, nbr_step)
    a = phi0 / mass
    b = h / mass
    c = T_ext * h / mass
    bbw = b**3 + b * omega**2
    k1 = Tzero - (a * b**2 + c * omega**2 + b**2 * c) / bbw
    T_theo = (
        a * b * omega * np.sin(omega * t)
        + a * b**2 * np.cos(omega * t)
        + c * omega**2
        + b**2 * c
    ) / bbw + k1 * np.exp(-b * t)

    # plt.figure(figsize=(12, 3))
    # for k, node in enumerate(model.internal_nodes):
    #     plt.plot(T[k, :], label=node.name)

    # plt.plot(T_theo, label="theo", color='r')
    # plt.legend()
    # plt.xlabel("time")
    # plt.show()

    np.testing.assert_almost_equal(T_theo, T[0, :], decimal=1)  # <-- warning


# TODO add test for mass...
