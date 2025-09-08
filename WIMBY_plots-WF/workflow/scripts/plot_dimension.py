import geopandas as gpd
import time
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.gridspec as gridspec
import concurrent.futures
from scripts.extra_functions import subplot_parallel

    
# input data
input_paths = snakemake.input

europe_onshore_shp = snakemake.input.europe_onshore_shapefile
europe_offshore_shp = snakemake.input.europe_offshore_shapefile

# only raster files
raster_paths = list(input_paths)
raster_paths.remove(europe_onshore_shp)
raster_paths.remove(europe_offshore_shp)


# parameters
include_table = snakemake.params.include_table
dpi_fig = snakemake.params.dpi_fig
format_fig = snakemake.params.format_fig

# dimension
dimension = snakemake.wildcards.dimension
dimension = dimension[0].upper() + dimension[1:]


# target EPSG
target_crs = "EPSG:3035"
# target_crs = "EPSG:4326"

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

if include_table:
    fig_onshore = plt.figure(figsize=(6*len(raster_paths),18))
    fig_offshore = plt.figure(figsize=(6*len(raster_paths),18))
    type_plot = "dim_table"
else:
    fig_onshore = plt.figure(figsize=(7*len(raster_paths),9))
    fig_offshore = plt.figure(figsize=(7*len(raster_paths),9))
    type_plot = "dim_no_table"


jobs_onshore = []
jobs_offshore = []
for raster_file in raster_paths:
    level = (raster_file.split("_",-1)[-1]).split(".")[0]
    job_args = {
        "tiff_paths": raster_file,
        "target_crs": target_crs,
        "technical": 0,
        "add_title": f"{dimension}: {level}\n",
        "dpi_fig": dpi_fig,
        "format_fig": format_fig,
        "type_plot":type_plot,
    }

    job_args_onshore = job_args.copy()
    job_args_onshore["europe"] = europe_onshore
    job_args_onshore["onshore"] = True
    jobs_onshore.append(job_args_onshore)

    job_args_offshore = job_args.copy()
    job_args_offshore["europe"] = europe_offshore
    job_args_offshore["onshore"] = False
    jobs_offshore.append(job_args_offshore)

with concurrent.futures.ProcessPoolExecutor() as executor:
    results_onshore = list(executor.map(subplot_parallel, jobs_onshore))
    results_offshore = list(executor.map(subplot_parallel, jobs_offshore))
print(f"{dimension} plot - onshore - {time.time()-t}")
print(f"{dimension} plot - offshore - {time.time()-t}")

gs_onshore = gridspec.GridSpec(1, len(raster_paths), figure=fig_onshore, wspace=0.05)
gs_offshore = gridspec.GridSpec(1, len(raster_paths), figure=fig_offshore, wspace=0.05)
for result_index, raster_file in enumerate(raster_paths):
    # onshore
    ax_onshore = fig_onshore.add_subplot(gs_onshore[0,result_index])
    result_onshore = results_onshore[result_index]
    ax_onshore.imshow(result_onshore["image"])
    ax_onshore.set_xticks([])  # Remove x-axis ticks
    ax_onshore.set_yticks([])  # Remove y-axis ticks
    ax_onshore.axis("off")

    # offshore
    ax_offshore = fig_offshore.add_subplot(gs_offshore[0,result_index])
    result_offshore = results_offshore[result_index]
    ax_offshore.imshow(result_offshore["image"])
    ax_offshore.set_xticks([])  # Remove x-axis ticks
    ax_offshore.set_yticks([])  # Remove y-axis ticks
    ax_offshore.axis("off")

fig_onshore.savefig(snakemake.output.plot_path_onshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")
fig_offshore.savefig(snakemake.output.plot_path_offshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")

