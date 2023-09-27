
from typing import List
from dataclasses import dataclass


@dataclass
class InertialNode:
    name: str
    mass: float
    T0: float


@dataclass
class LinearLink:
    source_name: str
    target_nane: str
    conductance: float

@dataclass
class SourceNode:
    name: str
    timeserie: List[float]

