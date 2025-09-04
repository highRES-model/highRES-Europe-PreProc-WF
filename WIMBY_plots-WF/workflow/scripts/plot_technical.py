import geopandas as gpd
import time
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scripts.extra_functions import plot_eligible_area, plot_eligible_area_no_table


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
    fig = plt.figure(figsize=(16,7))
    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=-0.08)
    ax1 = fig.add_subplot(gs[0,0])
    ax2 = fig.add_subplot(gs[0,1])

    plot_eligible_area(ax1, ax2, raster_file, europe_onshore, "Technical exclusion \n", target_crs)
    plt.savefig(snakemake.output.plot_path_onshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")
    print(f"Technical Excl plot - onshore - {time.time()-t}")

    fig = plt.figure(figsize=(15,7))
    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=-0.08)
    ax1 = fig.add_subplot(gs[0,0])
    ax2 = fig.add_subplot(gs[0,1])

    plot_eligible_area(ax1, ax2, raster_file, europe_offshore, "Technical exclusion \n", target_crs)

    plt.savefig(snakemake.output.plot_path_offshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")
    print(f"Technical Excl plot - offshore - {time.time()-t}")

else:
    fig = plt.figure(figsize=(7,7))
    gs = gridspec.GridSpec(1, 1, figure=fig)
    ax1 = fig.add_subplot(gs[0,0])

    plot_eligible_area_no_table(ax1, raster_file, europe_onshore, "Technical exclusion \n", target_crs)
    plt.savefig(snakemake.output.plot_path_onshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")
    print(f"Technical Excl plot - onshore - {time.time()-t}")

    fig = plt.figure(figsize=(7,7))
    gs = gridspec.GridSpec(1, 1, figure=fig)
    ax1 = fig.add_subplot(gs[0,0])

    plot_eligible_area_no_table(ax1, raster_file, europe_offshore, "Technical exclusion \n", target_crs)

    plt.savefig(snakemake.output.plot_path_offshore, dpi=dpi_fig, format=format_fig, bbox_inches="tight")
    print(f"Technical Excl plot - offshore - {time.time()-t}")