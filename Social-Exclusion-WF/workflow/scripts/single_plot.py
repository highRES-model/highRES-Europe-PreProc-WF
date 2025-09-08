import geopandas as gpd
import time
from atlite.gis import ExclusionContainer, shape_availability
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.gridspec as gridspec


def plot_eligible_area(ax1, ax2, tiff_path, europe, add_title, target_crs):
    excluder_wind = ExclusionContainer()
    excluder_wind.add_raster(tiff_path, crs=target_crs)

    full_europe = (
        europe
        .to_crs(excluder_wind.crs)
    )
    europe = (
        europe
        .to_crs(excluder_wind.crs)
        .dissolve()
        .reset_index()
    )

    mask_out=[]
    for c in full_europe.index:
        # print(c)
        cntr=full_europe.loc[full_europe.index==c,"geometry"]

        masked, transform = shape_availability(cntr, excluder_wind)
        eligible_share = float(masked.sum()) * excluder_wind.res**2 / cntr.geometry.item().area
        mask_out.append([c,(float(masked.sum()) * excluder_wind.res**2)/1E6,eligible_share*100])
    mask_out = pd.DataFrame(mask_out,columns=["Country","area (km$^2$)","share (%)"]).round(1)
    mask_out = mask_out.sort_values(by="Country")

    excluder_wind.plot_shape_availability(
        europe, 
        ax=ax1,
    )
    title = ax1.get_title()
    perc = round(float(title[22:27]),1)
    title = title[:22]+str(perc)+"%"
    new_title = add_title + title
    ax1.set_title(new_title, fontsize=12, weight="bold")

    ax1.set_xticks([])  # Remove x-axis ticks
    ax1.set_yticks([])  # Remove y-axis ticks

    # table
    cell_text = mask_out.values.tolist()
    col_labels = mask_out.columns.tolist()
    row_labels = None

    table = ax2.table(
        cellText=cell_text, 
        colLabels=col_labels,
        rowLabels=row_labels,
        colWidths=[0.3,0.4,0.3],
        loc="center", 
        cellLoc="center",
        )
    for j in range(len(col_labels)):
        cell = table.get_celld()[(0, j)]
        cell.get_text().set_fontweight('bold')
    # table.auto_set_column_width([0,1,2])
    ax2.axis("off")
    table.auto_set_font_size(False)
    #table.scale(1, 1)
    table.set_fontsize(13)






# input data
raster_file = snakemake.input.raster_file

category = snakemake.wildcards.category

# parameters
# aggregated_regions = snakemake.params.aggregated_regions
europe_onshore_shp = snakemake.params.europe_onshore_shapefile
europe_offshore_shp = snakemake.params.europe_offshore_shapefile

# output
output_path = snakemake.output.plot_path


# target EPSG
target_crs = "EPSG:3035"

# load correct shape file
if category in ["coastline"]:
    europe = (
        gpd
        .read_file(europe_offshore_shp)
        .set_index(["index"])
        .loc[:,['geometry']]
    )
else:
    europe = (
        gpd
        .read_file(europe_onshore_shp)
        .set_index(["index"])
        .loc[:,['geometry']]
    )


category = category[0].upper() + category[1:]

fig = plt.figure(figsize=(15,7))
gs = gridspec.GridSpec(1, 2, figure=fig, width_ratios=[1.8, 2], wspace=0.05)
ax1 = fig.add_subplot(gs[0,0])
ax2 = fig.add_subplot(gs[0,1])

plot_eligible_area(ax1, ax2, raster_file, europe, f"{category} exclusion \n", target_crs)
plt.savefig(output_path, dpi=400, format="png", bbox_inches="tight")
