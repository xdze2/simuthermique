# simuthermique
simulation thermique dynamique (du bâtiment)


## Données météorologiques annuels, heure par heure, et locales

- [avec l'API Darksky](./get_weatherdata.py) et la librairie python `pvlib` pour la position du soleil dans le ciel et le flux solaire
- données météorologiques de la [RT 2012](https://www.rt-batiment.fr/batiments-neufs/reglementation-thermique-2012/donnees-meteorologiques.html)

## Propriétés matériaux

- https://www.rt-batiment.fr/documents/rt2012/thbat/2-Fascicule_materiaux.pdf


## Modèle thermique dynamique

Système linéaire:
$$
M \frac{dT}{dt} = K \times T(t) + S(t)
$$

Conduction
$$
\phi_{i \rightarrow j} = UA\,( T_j - T_i )
$$

Convection (considérée linéaire)
$$
\phi_{i \rightarrow j} = hA\,( T_j - T_i )
$$

