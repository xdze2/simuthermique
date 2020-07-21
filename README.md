# simu thermique

code Python (& Julia) de simulation thermique dynamique (du bâtiment)

[🡺 lien vers la documentation](https://xdze2.github.io/simuthermique/)

## Blocs

- Accès aux données météo (API Weather data)
  - [darksky](weather_api/darksky_weatherdata.ipynb)
  - [donnée climat de la RT2012](weather_api/Fichiers_Meteo_RT2012/viz_yearly_weather_data.ipynb)
- Récupération des mesures de température (data logger)
  - [emonCMS](data_logger/test_readrawdata.ipynb)
- Calcul du flux solaire
  - librairie python `pvlib` 
- Définition et **calcul du modèle thermique**
- Estimation des paramètres du modèle



## Modèle thermique dynamique

Le modèle est l'équivalent d'un circuit électrique de résistances et condensateurs.

Système d'équations différentielles linéaires:

    M dT/dt = K × T(t) + S(t)

avec `T` le vecteur de température des noeuds du réseau, `M` les masses thermiques, `K` la matrice de connections entre les noeuds (conduction & convection) et `S` les termes extérieures (sources).


## Reférences et liens

###  Estimation & problème inverse

* «Solving inverse problems in building physics:  an overview ofguidelines for a careful and optimal use of data» S. Rouchier (2018), [Energy and Buildings, vol.  166, p.  178-195](http://simonrouchier.org/files/2018-enb-review.pdf)

* Simon Rouchier. Solving inverse problems in building physics: An overview of guidelines for a careful and optimal use of data. Energy and Buildings, Elsevier, 2018, 166, pp.178-195. ⟨10.1016/j.enbuild.2018.02.009⟩. ⟨[hal-01739623](https://hal.archives-ouvertes.fr/hal-01739623/document)⟩

*  Chadia Zayane. Identification d'un modèle de comportement thermique de bâtiment à partir de sa courbe de charge. Autre. École Nationale Supérieure des Mines de Paris, 2011. Français. ⟨NNT : 2011ENMP0001⟩. ⟨[pastel-00590810](https://pastel.archives-ouvertes.fr/pastel-00590810/document)⟩

* http://henrikmadsen.org/wp-content/uploads/2014/05/Journal_article_-_1995_-_Estimation_of_continuous-time_models_for_the_heat_dynamics_of_a_building.pdf


### Propriétés thermique des matériaux

- https://www.rt-batiment.fr/documents/rt2012/thbat/2-Fascicule_materiaux.pdf
- https://energieplus-lesite.be/
