
from typing import Dict, List
from dataclasses import dataclass


class Node:
    name: str

class Link:
    node_a: str
    node_b: str


@dataclass
class ThermalMass(Node):
    # Actually it is a link (capacitor) but with ground
    name: str
    mass: float
    T0: float


@dataclass
class FixedTemperature(Node):
    name: str
    Tk: List[float]

@dataclass
class FixedTemperature(Node):
    name: str
    Tk: List[float]

@dataclass
class HeatSource(Node):
    name: str
    Phik: List[float]

@dataclass
class ConductionLink(Link):
    node_a: str
    node_b: str
    conductance: float



# Nodes: list of tuples [(name, mass, T0) , ...]
# Sources: Dict {name: array (nbr time step), ...}
# Internal links: list ot tuples [(node A, node B, conductance value), ...]
# External links (i.e. with a source):
# list ot tuples [(internal node, source name, conductance value), ...]
# use conductance=None if it is a direct heat source

import numpy as np

@dataclass
class ModelGraph:
    nodes: List[Node]
    links: List[Link]

    def _assemble(self):

        node_name_to_idx = {node.name: k for k, node in enumerate(self.nodes)}

        A = np.zeros(len(self.links), len(self.nodes))
        C = np.zeros(len(self.links), 1)
        for k, link in enumerate(self.links):
            i, j = node_name_to_idx[link.node_a], node_name_to_idx[link.node_b]
            A[k, i] += 1
            A[k, j] -= 1

            C[k] = link.conductance

        C = np.diag(C)

        b = np.zeros(len(self.nodes), 1)
        f = np.zeros(len(self.nodes), 1)
        m = np.zeros(len(self.nodes), 1)
        for k, node in enumerate(self.nodes):
            if isinstance(ThermalMass, node):
                m[k] = node.mass
            elif isinstance(FixedTemperature, node):
                b[k] = node.Tk
            elif isinstance(HeatSource, node):
                b[k] = node.Phik
            