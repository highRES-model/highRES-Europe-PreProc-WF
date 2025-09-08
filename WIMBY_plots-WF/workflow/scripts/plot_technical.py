import geopandas as gpd
import time
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import concurrent.futures
from scripts.extra_functions import subplot_parallel


# input data
raster_file = snakemake.input.technical_exclusions
europe_onshore_shp = snakemake.input.europe_onshore_shapefile
europe_offshore_shp = snakemake.input.europe_offshore_shapefile

# params
include_table = snakemake.params.include_table
dpi_fig = snakemake.params.dpi_fig
format_fig = snakemake.params.format_fig

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
    fig_onshore = plt.figure(figsize=(12,9))
    fig_offshore = plt.figure(figsize=(12,9))
    type_plot = "dim_table"
else:
    fig_onshore = plt.figure(figsize=(7,7))
    fig_offshore = plt.figure(figsize=(7,7))
    type_plot = "dim_no_table"


jobs_onshore = []
jobs_offshore = []

job_args = {
    "tiff_paths": raster_file,
    "target_crs": target_crs,
    "add_title": "Technical exclusion\n",
    "technical": 1,
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
print(f"Technical Excl plot - onshore - {time.time()-t}")
print(f"Technical Excl plot - offshore - {time.time()-t}")

gs_onshore = gridspec.GridSpec(1, 1, figure=fig_onshore)
gs_offshore = gridspec.GridSpec(1, 1, figure=fig_offshore)

# onshore
ax_onshore = fig_onshore.add_subplot(gs_onshore[0,0])
result_onshore = results_onshore[0]
ax_onshore.imshow(result_onshore["image"])
ax_onshore.set_xticks([])  # Remove x-axis ticks
ax_onshore.set_yticks([])  # Remove y-axis ticks
ax_onshore.axis("off")

# offshore
ax_offshore = fig_offshore.add_subplot(gs_offshore[0,0])
result_offshore = results_offshore[0]
ax_offshore.imshow(result_offshore["image"])
ax_offshore.set_xticks([])  # Remove x-axis ticks
ax_offshore.set_yticks([])  # Remove y-axis ticks
ax_offshore.axis("off")

fig_onshore.savefig(snakemake.output.plot_path_onshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")
fig_offshore.savefig(snakemake.output.plot_path_offshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")
