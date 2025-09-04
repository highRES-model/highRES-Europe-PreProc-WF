import geopandas as gpd
import time
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.gridspec as gridspec
from scripts.extra_functions import plot_eligible_area, plot_eligible_area_no_table

    
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
    fig_onshore = plt.figure(figsize=(9*len(raster_paths),19))
    fig_offshore = plt.figure(figsize=(9*len(raster_paths),15))
    ## map - map - map / table - table - table
    gs_onshore = gridspec.GridSpec(2, len(raster_paths), figure=fig_onshore, wspace=0.05, hspace=0.03)
    gs_offshore = gridspec.GridSpec(2, len(raster_paths), figure=fig_offshore, wspace=0.05, hspace=0.03)

    col = 0
    for raster_file in raster_paths:
        level = (raster_file.split("_",-1)[-1]).split(".")[0]

        # onshore
        ax1 = fig_onshore.add_subplot(gs_onshore[0,col])
        ax2 = fig_onshore.add_subplot(gs_onshore[1,col])
        plot_eligible_area(ax1, ax2, raster_file, europe_onshore, f"{dimension}: {level}\n", target_crs)
        print(f"{dimension} plot - onshore {level} - {time.time()-t}")

        # offshore
        ax1 = fig_offshore.add_subplot(gs_offshore[0,col])
        ax2 = fig_offshore.add_subplot(gs_offshore[1,col])
        plot_eligible_area(ax1, ax2, raster_file, europe_offshore, f"{dimension}: {level}\n", target_crs)
        print(f"{dimension} plot - offshore {level} - {time.time()-t}")

        col += 1
    fig_onshore.savefig(snakemake.output.plot_path_onshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")
    fig_offshore.savefig(snakemake.output.plot_path_offshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")

    print(f"plotting {time.time()-t}")
else:
    fig_onshore = plt.figure(figsize=(7*len(raster_paths),9))
    fig_offshore = plt.figure(figsize=(7*len(raster_paths),9))
    ## map - map - map
    gs_onshore = gridspec.GridSpec(1, len(raster_paths), figure=fig_onshore, wspace=0.05)
    gs_offshore = gridspec.GridSpec(1, len(raster_paths), figure=fig_offshore, wspace=0.05)
    
    col = 0
    for raster_file in raster_paths:
        level = (raster_file.split("_",-1)[-1]).split(".")[0]

        # onshore
        ax = fig_onshore.add_subplot(gs_onshore[0,col])
        plot_eligible_area_no_table(ax, raster_file, europe_onshore, f"{dimension}: {level}\n", target_crs)
        print(f"{dimension} plot - onshore {level} - {time.time()-t}")
        # offshore
        ax = fig_offshore.add_subplot(gs_offshore[0,col])
        plot_eligible_area_no_table(ax, raster_file, europe_offshore, f"{dimension}: {level}\n", target_crs)
        print(f"{dimension} plot - offshore {level} - {time.time()-t}")

        col += 1

    fig_onshore.savefig(snakemake.output.plot_path_onshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")
    fig_offshore.savefig(snakemake.output.plot_path_offshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")


    
