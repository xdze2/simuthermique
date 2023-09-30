from pint import UnitRegistry
ureg = UnitRegistry()
print(ureg.meter)

print(30.0 * ureg.meter)


print(ureg.get_compatible_units('[mass]'))


from simuthermique.material import ThermalMaterial


brique = ThermalMaterial(
    conductivity=0.64,
    heat_capacity=1000,
    density=1700
)

print(brique.diffusion_lenght(24*60*60))

print(brique.diffusion_lenght(24*60*60*7))

print(brique.diffusion_lenght(24*60*60*365))