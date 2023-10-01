from typing import Dict, List
from dataclasses import dataclass

from itertools import chain

import numpy as np


@dataclass
class ThermalCapacityLink:
    node_a: str
    node_b: str
    mass: float


@dataclass
class BatteryLink:
    node_a: str
    node_b: str
    Tk: List[float]


@dataclass
class ConductionLink:
    node_a: str
    node_b: str
    conductance: float


@dataclass
class HeatSource:
    name: str
    Phik: List[float]


@dataclass
class ModelGraph:
    links: List
    sources: List[HeatSource]

    def _assemble(self, time):
        node_names = set()
        for link in self.links:
            node_names.add(link.node_a)
            node_names.add(link.node_b)

        for node in self.sources:
            node_names.add(node.name)

        node_name_to_idx = {name: idx for idx, name in enumerate(node_names)}
        link_name_to_idx = {
            (link.node_a, link.node_b): idx
            for idx, link in enumerate(self.links)
        }

        # Assemble
        nbr_nodes = len(node_name_to_idx)
        nbr_links = len(link_name_to_idx)
        print(f"{nbr_nodes:=}")
        print(f"{nbr_links:=}")

        A = np.zeros((nbr_links, nbr_nodes))
        diag_C = np.zeros(nbr_links)
        b = np.zeros(nbr_links)
        m = np.zeros(nbr_links)
        for link in self.links:
            k = link_name_to_idx[(link.node_a, link.node_b)]
            i, j = node_name_to_idx[link.node_a], node_name_to_idx[link.node_b]
            A[k, i] += 1
            A[k, j] -= 1

            if isinstance(link, ConductionLink):
                diag_C[k] = link.conductance
            elif isinstance(link, ThermalCapacityLink):
                m[k] = link.mass
            elif isinstance(link, BatteryLink):
                b[k] = link.Tk


        C = np.diag(diag_C)

        f = np.zeros(nbr_nodes)
        for node in self.sources:
            k = node_name_to_idx[node.name]
            f[k] = node.Phik

        return A, C, b, f, m
    

links = [
    ConductionLink("zero", "A", 1),
    ConductionLink("A", "SRC", 0.1),
    BatteryLink("zero", "SRC", 10)
]

sources = [
]


model = ModelGraph(
    links=links,
    sources=sources
)

A, C, b, f, m = model._assemble(1)


AtC = np.matmul(A.transpose(),  C)
AtCA = np.matmul(AtC, A)
AtCb = np.matmul(AtC, b)

print("AtCA=", AtCA)

print("AtCb=", AtCb)

print("f=", f)