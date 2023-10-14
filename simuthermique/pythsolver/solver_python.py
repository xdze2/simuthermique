from dataclasses import dataclass
from typing import Callable, List

import numpy as np
from scipy.integrate import odeint


@dataclass
class ThermalMassNode:
    name: str
    mass: float
    T_zero: float


@dataclass
class ExternalNode:
    name: str
    get_temp: Callable


@dataclass
class DirectSource:
    node_name: str
    get_flux: Callable


@dataclass
class ConductionLink:
    node_name_a: str
    node_name_b: str
    conductance: float


class SimpleThermalModel:
    def __init__(
        self,
        internal_nodes: List[ThermalMassNode] = None,
        external_nodes: List[ExternalNode] = None,
        direct_sources: List[DirectSource] = None,
        links: List[ConductionLink] = None,
    ) -> None:
        self.internal_nodes = internal_nodes if internal_nodes is not None else list()
        self.external_nodes = external_nodes if external_nodes is not None else list()
        self.direct_sources = direct_sources if direct_sources is not None else list()
        self.links = links if links is not None else list()

        self._node_name_to_idx = {
            node.name: idx for idx, node in enumerate(self.internal_nodes)
        }
        self._external_to_node = {
            node.name: node for idx, node in enumerate(self.external_nodes)
        }
        self.internal_links: List[ConductionLink] = []
        self.external_links: List[ConductionLink] = []
        for link in self.links:
            node_a, node_b = link.node_name_a, link.node_name_b
            if node_a in self._node_name_to_idx and node_b in self._node_name_to_idx:
                self.internal_links.append(link)
            elif node_a in self._node_name_to_idx and node_b in self._external_to_node:
                self.external_links.append(link)
            elif node_a in self._external_to_node and node_b in self._node_name_to_idx:
                link.node_name_a = node_b
                link.node_name_b = node_a
                self.external_links.append(link)
            else:
                raise ValueError(f"link {link} nodes error")

    def assemble_K(self):
        self.K = np.zeros((len(self.internal_nodes), len(self.internal_nodes)))

        for link in self.internal_links:
            i = self._node_name_to_idx[link.node_name_a]
            j = self._node_name_to_idx[link.node_name_b]
            self.K[i, i] -= link.conductance
            self.K[j, j] -= link.conductance
            self.K[i, j] += link.conductance
            self.K[j, i] += link.conductance

        return self.K

    def assemble_H(self) -> np.ndarray:
        self.H = np.zeros(len(self.internal_nodes))
        for link in self.external_links:
            internal_node_idx = self._node_name_to_idx[link.node_name_a]
            self.H[internal_node_idx] += link.conductance

        return self.H

    def assemble_M(self) -> np.ndarray:
        self.M = [node.mass for node in self.internal_nodes]
        return np.array(self.M)

    def assemble_S(self, t: float) -> np.ndarray:
        """Assemble equivalent sources: S = phi + H*T_ext."""
        self.S = np.zeros(len(self.internal_nodes))
        for source in self.direct_sources:
            node_idx = self._node_name_to_idx[source.node_name]
            self.S[node_idx] += source.get_flux(t)

        for ext_link in self.external_links:
            node_idx = self._node_name_to_idx[ext_link.node_name_a]
            ext_node = self._external_to_node[ext_link.node_name_b]
            self.S[node_idx] += ext_link.conductance * ext_node.get_temp(t)

        return self.S

    def solve(self, delta_t: float, nbr_steps: int, theta: float = 0.5) -> np.ndarray:
        """Time integration."""
        Keq = self.assemble_K() + np.diag(self.assemble_H())
        Mm = np.diag(self.assemble_M()) / delta_t
        a = Mm + theta * Keq

        T = np.zeros((len(self.internal_nodes), nbr_steps))
        T[:, 0] = np.array([n.T_zero for n in self.internal_nodes])
        S_k = self.assemble_S(0)
        for k in range(1, nbr_steps):
            Tk = T[:, k - 1]
            S_k_plus_1 = self.assemble_S((k + 1) * delta_t)
            Mk = Mm - (1 - theta) * Keq
            b = np.matmul(Mk, Tk) + theta * S_k_plus_1 + (1 - theta) * S_k
            T[:, k] = np.linalg.solve(a, b)
            S_k = S_k_plus_1
        return T

    def get_fTt(self):
        """Return f(t, T) = dT/dt model function."""
        invM = np.diag(1 / self.assemble_M())
        Keq = self.assemble_K() + np.diag(self.assemble_H())
        invMKeq = np.matmul(invM, Keq)

        def fTr(t, T):
            return -np.matmul(invMKeq, T) + np.matmul(invM, self.assemble_S(t))

        return fTr

    def solve_odeint(self, timeindex_sec: np.ndarray) -> np.ndarray:
        """Use scipy odeint solver."""
        Tzero = [n.T_zero for n in self.internal_nodes]
        model_function = self.get_fTt()
        sol = odeint(model_function, Tzero, timeindex_sec, tfirst=True)
        return sol

    def draw_graph(self):
        from graphviz import Graph

        graph = Graph(comment="thermal model")

        for node in self.internal_nodes:
            label = f"{node.name} [{node.mass}]"
            graph.node(node.name, label, shape="rectangle")

        for node in self.external_nodes:
            label = f"{node.name} [K]"
            graph.node(node.name, label, shape="ellipse")

        for src in self.direct_sources:
            graph.node(src.node_name, f"{src.node_name}", shape="triangle")

        for link in self.internal_links + self.external_links:
            label = f"{link.conductance} W/K"
            graph.edge(link.node_name_a, link.node_name_b, label, fontsize="9")

        graph.view()
        return graph
