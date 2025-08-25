# Technical Exclusions for Europe

This sub-repository generates the technical exclusion used in highRES-Europe. 

Datasets:
* [Eurostat shapefiles](https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics), used as the base layer for specifying the spatial extent. 
* [EU-Hydro River Network Database 2006-2012 (vector), Europe](https://land.copernicus.eu/en/products/eu-hydro/eu-hydro-river-network-database), used to exclude hydrological features.
* [Copernicus DEM – GLO-90](https://doi.org/10.5270/ESA-c5d3d65), used to generate the maximum slope restrictions. 
* [EMODnet Human Activities, Vessel Density Map](https://emodnet.ec.europa.eu/en/human-activities), used to exclude shipping lanes.

## Computational requirements

The code in this repository requires considerable computational resources. 

The code has been tested for the following system:

    Linux : Ubuntu 24.04
