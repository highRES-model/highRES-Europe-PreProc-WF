# Environmental exclusions for Europe

This sub-repository generates the environmental exclusion used in highRES-Europe. The particular application presented here is based on the work in the Horizon 2020 project [WIMBY](https://wimby.eu/) and is to be included in a forthcoming publication. 

The Snakemake based workflow process highly detailed geospatial data, applies buffer distances to different type of environmental categories and produce raster files with the combined environmental exclusions. The raster files are later used in the [highRES-Europe Workflow](https://github.com/highRES-model/highRES-Europe-WF/) to determine the wind energy potential across different regions in Europe. 

The workflow is customisable and can be modified to include additional/alternative data sources as well as different buffer distances. 

Datasets:
* [Eurostat shapefiles](https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics), used as the base layer for specifying the spatial extent. 
* [Nationally designated areas (CDDA)](https://doi.org/10.2909/81f265d0-0734-4315-af0f-63721e937f57), used to exclude different IUCN categories.
* [CORINE land Cover](https://land.copernicus.eu/en/products/corine-land-cover?tab=datasets), used to exclude forests and peat bogs. 
* [Natura2000](https://www.eea.europa.eu/en/datahub/datahubitem-view/6fc8ad2d-195d-40f4-bdec-576e7d1268e4), used to exclude Natura2000 areas.
* [Bird and bat vulnerability ](https://www.biorxiv.org/content/10.1101/2025.11.24.685024v1), used to exclude areas with high bird and bat vulnerability. The dataset is currently undergoing peer review and will soon be made publicly available. 

## Installation and usage

The workflow is built using the Python based workflow manager [Snakemake](https://snakemake.github.io/). 

1. Clone the repository:
```sh
git clone git@github.com:highRES-model/highRES-Europe-PreProc-WF.git
```

2. Install Snakemake and the associated conda environment. The recommended way is using [mamba](https://mamba.readthedocs.io/en/latest/installation.html) to install snakemake into its own conda environment from the environment file:
```sh
mamba env create -f workflow/envs/environmental_exclusions.yaml`
```

3. Acquire the data (see links in the description above) and setup the paths and potential modifications to the buffer distances in the config file.

4. Activate the environment `conda activate environmental_exclusions` and run the workflow: `snakemake -c 1 --configfile config/config.yaml`.

## Computational requirements

Due to the high resolution GIS data and relatively large extent, the code in this repository requires considerable computational resources. Running the workflow requires about 32GB of RAM. It is possible to parallelize the workflow and run all scenario levels simultaneously. This will however put a higher strain on the peak RAM required and may be more suitable for High Performing Computing (HPC) clusters. 

The code has been tested for the following system:

    Linux : Ubuntu 24.04
