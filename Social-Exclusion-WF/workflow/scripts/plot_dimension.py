import geopandas as gpd
import time
from atlite.gis import ExclusionContainer
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.gridspec as gridspec

def plot_eligible_area(ax, tiff_path, europe, add_title, target_crs):
    excluder_wind = ExclusionContainer()
    excluder_wind.add_raster(tiff_path, crs=target_crs)

    europe_mod = (
        europe
        .to_crs(excluder_wind.crs)
        .dissolve()
        .reset_index()
    )

    excluder_wind.plot_shape_availability(
        europe_mod, 
        ax=ax,
    )

    title = ax.get_title()
    new_title = add_title + title
    ax.set_title(new_title)

    ax.set_xticks([])  # Remove x-axis ticks
    ax.set_yticks([])  # Remove y-axis ticks


# input data
raster_file_low = snakemake.input.input_path_low
raster_file_medium = snakemake.input.input_path_medium
raster_file_high = snakemake.input.input_path_high

# parameters
europe_onshore_shp = snakemake.params.europe_onshore_shapefile
europe_offshore_shp = snakemake.params.europe_offshore_shapefile

# target EPSG
target_crs = "EPSG:3035"


## onshore

t=time.time()


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

print(time.time()-t)


# Open the TIFF file and ensure CRS matches
fig = plt.figure(figsize=(15,7), layout="constrained")
gs = gridspec.GridSpec(1, 3, figure=fig, width_ratios=[1, 1, 1], wspace=0.05)
ax1 = fig.add_subplot(gs[0,0])
ax2 = fig.add_subplot(gs[0,1])
ax3 = fig.add_subplot(gs[0,2])
plot_eligible_area(ax1, raster_file_low, europe_onshore, "Social: low\n", target_crs)
plot_eligible_area(ax2, raster_file_medium, europe_onshore, "Social: medium\n", target_crs)
plot_eligible_area(ax3, raster_file_high, europe_onshore, "Social:high\n", target_crs)
plt.savefig(snakemake.output.plot_path_onshore, dpi=400, format="png", bbox_inches="tight")
print(f"Social excl plot - onshore - {time.time()-t}")

fig = plt.figure(figsize=(15,7), layout="constrained")
gs = gridspec.GridSpec(1, 3, figure=fig, width_ratios=[1, 1, 1], wspace=0.05)
ax1 = fig.add_subplot(gs[0,0])
ax2 = fig.add_subplot(gs[0,1])
ax3 = fig.add_subplot(gs[0,2])
plot_eligible_area(ax1, raster_file_low, europe_offshore, "Social: low\n", target_crs)
plot_eligible_area(ax2, raster_file_medium, europe_offshore, "Social: medium\n", target_crs)
plot_eligible_area(ax3, raster_file_high, europe_offshore, "Social:high\n", target_crs)
plt.savefig(snakemake.output.plot_path_offshore, dpi=400, format="png", bbox_inches="tight")
print(f"Social excl plot - offshore - {time.time()-t}")