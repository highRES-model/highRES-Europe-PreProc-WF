# Existing capacities for Europe

The current workflow updates the techno-economic dataset (used in highRES-Europe) based on data from the Global Energy Monitor platform for nuclear, wind and solar energy sources. Existing capacities are filtered by technology in each relevant NUTS2 region of Europe, taking into account the lifetime of each technology in 2050.
A CSV file is also created containing information on the project name, technology, country, country code, location (latitude and longitude), capacity (in MW), year of commissioning and estimated year of retirement of existing plants. This last column is estimated on the basis of the lifetime for each technology. In particular, for nuclear, the estimated lifetime is calculated using the 75th percentile of nuclear plants to be decommissioned as reported in GEM. For wind and solar, an estimate of 30 years is used.

The techno-economic dataset is updated to include only those plants still in **operation in 2050**, using the column "estimated_retirement_year".

## Getting started

To run the workflow, three main data are needed: the existing power plants, the shape file (geojson) with the considered countries and regions (from the intermediate file), and the techno-economic dataset used in highRES-WF (see below the specific sub-section for each of these datasets).

To create and run the workflow:
1. Clone the repository
2. Install snakemake
    - Download miniforge windows exe <https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe>
    - Install Miniforge
    - Open Miniforge Prompt from the start menu
    - Install the environment from the provided yaml file: `mamba env create -f workflow/envs/highres_existing_capacities.yaml`
3. Activate the snakemake environment `mamba activate highres_existing_capacities`
4. Navigate to the repository in your snakemake conda environment shell
5. Get the required input files (see subsections below)
6. Run `snakemake --configfile config/config.yaml`

The `config.yaml` file in `config/` contains all the options for running the workflow (year of estimation, input and output paths and filenames, etc.).


### Getting existing power plant in Europe

The existing solar, wind and nuclear power plants can be downloaded from the Global Energy Monitor, an open-access platform created to provide essential information on the various existing energy infrastructures and projects (such as wind, solar, hydro, oil and gas, etc.) in the world (more in [Global Energy Monitor] (https://globalenergymonitor.org/)).

To gain access to the files, you will need to complete an online form with your email address, name, organisation and how you intend to use the data. You will receive an email with the requested data shortly after submitting the form. Direct links are provided below:

- [For wind power plants](https://globalenergymonitor.org/projects/global-solar-power-tracker/download-data/)
- [For solar power plants](https://globalenergymonitor.org/projects/global-wind-power-tracker/download-data/)
- [For nuclear power plants](https://globalenergymonitor.org/projects/global-nuclear-power-tracker/download-data/)

You will receive an Excel file (.xlsx) for each energy source. You can provide the path to all these files in the config file (`config/config.yaml`).

### Getting shape files

The shape files needed to run this workflow can be obtained as intermediate data from running the highRES-Europe workflow ([highRES-Europe-WF](https://github.com/highRES-model/highRES-Europe-WF/tree/main)) at NUTS2 level. To run only the input processing step of highRES (without running GAMS), it is necessary to set the target option to `input.finished` in the configuration file (`config/config_ci.yaml`):

```
target: "inputs.finished"
...
spatials: ["nuts2"]
```
The resulting shape files are located in `intermediate_data/nuts2/shapes/` of the highRES-Europe WF.

Once the input processing step is complete, the path to the `europe_onshore.geojson` and `europe_offshore.geojson` files can be defined in the config file (`config/config.yaml`):

```
# Shape files
  onshore_shapefile_path: "resources/europe_onshore.geojson"
  offshore_shapefile_path: "resources/europe_offshore.geojson"
```

### Getting techno-economic dataset

The techno-economic dataset required for this workflow can be downloaded from [here](https://zenodo.org/records/14223618/files/resources.zip?download=1) or using the following command:
```
curl -L -b cookies.txt "https://zenodo.org/records/14223618/files/resources.zip?download=1" --output resources.zip
```

You can provide the path to `highres_technoeconomic_dataset.ods` in config file (`config/config.yaml`).

