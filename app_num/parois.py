class ThermalConductivity:
    """W/m/K"""

    BriqueTerreCuite = 0.84
    Bois = 0.14
    LaineVerre = 0.045


def resistance_thermiqe(ep, kth):
    """K/W"""
    return ep / kth


delta_T = 20

surface_m2 = 5 * 2.5

thickness_m = 0.4
lambda_brique_terre_cuite = 0.84  # W/m/K


k_mat = lambda_brique_terre_cuite

R_thermique_brique = resistance_thermiqe(0.40, ThermalConductivity.BriqueTerreCuite)
print(f"{R_thermique_brique=:.1f}")

R_thermique_isolant = resistance_thermiqe(0.10, ThermalConductivity.LaineVerre)
print(f"{R_thermique_isolant=:.1f}")


Ri = 0.13
Re = 0.04
# page 37

R_surfacique = Ri + Re + R_thermique_isolant + R_thermique_brique
flux_W = delta_T * surface_m2 / R_surfacique

print(f"{flux_W=:.1f} W")


lambda_bois = 0.14  # W/m/K
epaisseur = 2e-2
R = epaisseur / lambda_bois

R_surfacique = Ri + Re + R
surface_m2 = 0.1 * (2 + 2 + 1 + 1 + 2)
flux_W = delta_T * surface_m2 / R_surfacique
print(f"{flux_W:.1f} W")


# simple vitrage

U = 5  # W/m2/C

surface_vitre = 1.9 * 0.9
flux = U * surface_vitre * delta_T
print(f"{flux_W:.1f} W")
