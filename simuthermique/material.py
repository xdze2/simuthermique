

from dataclasses import dataclass
import numpy as np

@dataclass
class ThermalMaterial:
    conductivity: float
    heat_capacity: float
    density: float
    # mu


    def diffusion_lenght(self, delta_t):
        return np.sqrt(delta_t*self.conductivity/self.density/self.heat_capacity)
