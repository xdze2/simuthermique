# simuthermique

code Python & Julia de simulation thermique dynamique (du bâtiment)


## Données météorologiques

- annuels, heure par heure, et locales
 [avec l'API Darksky](./get_weatherdata.py) et la librairie python `pvlib` pour la position du soleil dans le ciel et le flux solaire
- données météorologiques de la [RT 2012](https://www.rt-batiment.fr/batiments-neufs/reglementation-thermique-2012/donnees-meteorologiques.html)


## Propriétés thermique des matériaux

- https://www.rt-batiment.fr/documents/rt2012/thbat/2-Fascicule_materiaux.pdf
- https://energieplus-lesite.be/


## Modèle thermique dynamique

Le modèle est l'équivalent d'un circuit électrique de résistances et condensateurs.

Système d'équation différentielles linéaires:
$$
M \frac{dT}{dt} = K \times T(t) + S(t)
$$

avec $T$ le vecteur de température des noeuds du réseau, $M$ les masses thermiques, $K$ la matrice de connections entre les noeuds (résitances thermiques) et $S$ les termes extérieures (sources).

> _remarque:_ $M$ est un vecteur ou une matrice...


Conduction
$$
\phi_{i \rightarrow j} = UA\,( T_j - T_i )
$$

Convection (considérée linéaire)
$$
\phi_{i \rightarrow j} = hA\,( T_j - T_i )
$$

## Solver

- See part "3 Fully discrete approximation" in [Lecture 3 - Finite Volume Discretization of the Heat Equation](http://www.csc.kth.se/utbildning/kth/kurser/DN2255/ndiff13/Lecture3.pdf)

- Linear system (matrix) formulation:
$$
\frac{\partial T}{\partial t} = A \, T + S(t)
$$

Time discretization using theta-method:
$$
T^{k+1} - T^{k} = \theta\, dt \left[ A \, T^{k+1} + S^{k+1} \right]
+ (1-\theta)\, dt \left[ A \, T^{k} + S^{k} \right]
$$

$$
 \left[ I  - \theta\, dt\, A \right] T^{k+1} =
 \theta\, dt \, S^{k+1}
+ (1-\theta)\, dt \left[ A \, T^{k} + S^{k} \right] + T^k
$$

$$
\left[ I  - \theta\, dt\, A \right] T^{k+1} =
\left[I + (1-\theta)\, dt \,A \right] T^{k}
+ \left( \theta \, S^{k+1} +  (1-\theta)\, S^{k}  \right) dt
$$


$T^{k+1}$ is solved using the backslash operator


- $\theta = 0$ : Forward Euler (explicit, 1st order)
- $\theta = 1/2$ : Crank–Nicolson (implicit, 2nd order)
- $\theta = 1$ : Backward Euler (implicit, 1st order),

> Remark 2: The Crank-Nicolson scheme is second order accurate but gives slowly decaying oscillations for large eigenvalues.  It is unsuitable for parabolic problems with rapidly decayingtransients. The $\theta=1$ scheme damps all components, and should be used in the initial steps.


solver takes: A matrix, T0 values, S time-series (sparse)

## Blocs

- Weather data
- Model topologique (i.e. model definition object)
    - Model parameter setting
- Linear ODE Solver
    - assemblage
    - solve

- fit to measured data


## Reférences et liens

* http://simonrouchier.org/files/2018-enb-review.pdf