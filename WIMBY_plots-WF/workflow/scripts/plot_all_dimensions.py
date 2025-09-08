import geopandas as gpd
import time
import matplotlib.pyplot as plt
import concurrent.futures
import matplotlib.gridspec as gridspec
from scripts.extra_functions import subplot_parallel


europe_onshore_shp = snakemake.input.europe_onshore_shapefile
europe_offshore_shp = snakemake.input.europe_offshore_shapefile
technical_exclusions = snakemake.input.technical_exclusions


# parameters
dimensions_scenarios = snakemake.params.dimensions_scenarios
dpi_fig = snakemake.params.dpi_fig
format_fig = snakemake.params.format_fig
inputs_path = snakemake.params.inputs_path


# target EPSG
target_crs = "EPSG:3035"

## onshore
europe_onshore = (
    gpd
    .read_file(europe_onshore_shp)
    .set_index(["index"])
    .loc[:,['geometry']]
)

## offshore
europe_offshore = (
    gpd
    .read_file(europe_offshore_shp)
    .set_index(["index"])
    .loc[:,['geometry']]
)


t=time.time()

sc_levels = dimensions_scenarios["social"]
en_levels = dimensions_scenarios["environmental"]

jobs_onshore = []
jobs_offshore = []
for i,level_row in enumerate(en_levels):
    for j, level_col in enumerate(sc_levels):
        environmental_level = f"{inputs_path}/environmental_{level_row}.tif"
        social_level = f"{inputs_path}/social_{level_col}.tif"
        
        add_title = f"Soc: {level_col} - env: {level_row}\n"
        job_args = {
            "tiff_paths": [environmental_level,social_level,technical_exclusions],
            "target_crs": target_crs,
            "add_title": add_title,
            "dpi_fig": dpi_fig,
            "format_fig": format_fig,
            "type_plot":"all_dim",
        }

        job_args["europe"] = europe_onshore
        jobs_onshore.append(job_args)

        job_args["europe"] = europe_offshore
        jobs_offshore.append(job_args)

with concurrent.futures.ProcessPoolExecutor() as executor:
    results_onshore = list(executor.map(subplot_parallel, jobs_onshore))
print(f"Onshore - environmental: {level_row}; social: {level_col} - {time.time()-t}")

with concurrent.futures.ProcessPoolExecutor() as executor:
    results_offshore = list(executor.map(subplot_parallel, jobs_offshore))
print(f"Offshore - environmental: {level_row}; social: {level_col} - {time.time()-t}")

fig_onshore = plt.figure(figsize=(4*len(sc_levels),5*len(en_levels)), layout="constrained")
fig_offshore = plt.figure(figsize=(4*len(sc_levels),5*len(en_levels)), layout="constrained")
gs_onshore = gridspec.GridSpec(len(en_levels), len(sc_levels), figure=fig_onshore, wspace=0.05)
gs_offshore = gridspec.GridSpec(len(en_levels), len(sc_levels), figure=fig_offshore, wspace=0.05)

result_index = 0
for i,level_row in enumerate(en_levels):
    for j, level_col in enumerate(sc_levels):
        # onshore
        ax = fig_onshore.add_subplot(gs_onshore[i,j])
        result = results_onshore[result_index]
        ax.imshow(result["image"])
        ax.set_xticks([])  # Remove x-axis ticks
        ax.set_yticks([])  # Remove y-axis ticks
        ax.axis("off")

        # offshore
        ax = fig_offshore.add_subplot(gs_offshore[i,j])
        result = results_offshore[result_index]
        ax.imshow(result["image"])
        ax.set_xticks([])  # Remove x-axis ticks
        ax.set_yticks([])  # Remove y-axis ticks
        ax.axis("off")

        result_index += 1

        
fig_onshore.savefig(snakemake.output.plot_path_onshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")
fig_offshore.savefig(snakemake.output.plot_path_offshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")
