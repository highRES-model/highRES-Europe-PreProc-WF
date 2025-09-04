import geopandas as gpd
import time
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.gridspec as gridspec
from scripts.extra_functions import plot_eligible_area_all_dim


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

fig = plt.figure(figsize=(4*len(sc_levels),5*len(en_levels)), layout="constrained")
gs = gridspec.GridSpec(len(en_levels), len(sc_levels), figure=fig, wspace=0.05)

levels = ["low","medium","high"]
i = 0
for level_row in en_levels:
    j = 0
    for level_col in sc_levels:
        ax = fig.add_subplot(gs[i,j])
        environmental_level = f"{inputs_path}/environmental_{level_row}.tif"
        social_level = f"{inputs_path}/social_{level_col}.tif"
        # environmental_level = raster_files["environmental"][level_row]
        # social_level = raster_files["social"][level_col]

        plot_eligible_area_all_dim(ax, [environmental_level,social_level,technical_exclusions], europe_onshore, "", target_crs)
        print(f"Onshore - environmental: {level_row}; social: {level_col} - {time.time()-t}")
        if i==0:
            if j==1:
                title = ax.get_title()
                new_title = "Social\n"+f"{level_col}\n" + title
                ax.set_title(new_title, fontsize=12, weight="bold")
            else:
                title = ax.get_title()
                new_title = f"{level_col}\n" + title
                ax.set_title(new_title, fontsize=12, weight="bold")
        if j==0:
            if i==1:
                ax.set_ylabel(f"Environmental\n{level_row}", fontsize=12, weight="bold")
            else:
                ax.set_ylabel(f"{level_row}", fontsize=12, weight="bold")
        j += 1
    i += 1

plt.savefig(snakemake.output.plot_path_onshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")

fig = plt.figure(figsize=(4*len(sc_levels),5*len(en_levels)), layout="constrained")
gs = gridspec.GridSpec(len(en_levels), len(sc_levels), figure=fig, wspace=0.05)
i = 0
for level_row in levels:
    j = 0
    for level_col in levels:
        ax = fig.add_subplot(gs[i,j])
        environmental_level = f"{inputs_path}/environmental_{level_row}.tif"
        social_level = f"{inputs_path}/social_{level_col}.tif"
        # environmental_level = raster_files["environmental"][level_row]
        # social_level = raster_files["social"][level_col]
        plot_eligible_area_all_dim(ax, [environmental_level,social_level,technical_exclusions], europe_offshore, "", target_crs)
        print(f"Offshore - environmental: {level_row}; social: {level_col} - {time.time()-t}")
        if i==0:
            if j==1:
                title = ax.get_title()
                new_title = "Social\n"+f"{level_col}\n" + title
                ax.set_title(new_title, fontsize=12, weight="bold")
            else:
                title = ax.get_title()
                new_title = f"{level_col}\n" + title
                ax.set_title(new_title, fontsize=12, weight="bold")
        if j==0:
            if i==1:
                ax.set_ylabel(f"Environmental\n{level_row}", fontsize=12, weight="bold")
            else:
                ax.set_ylabel(f"{level_row}", fontsize=12, weight="bold")
        j += 1
    i += 1

plt.savefig(snakemake.output.plot_path_offshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")
