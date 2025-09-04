from atlite.gis import ExclusionContainer, shape_availability
import pandas as pd
import geopandas as gpd
from matplotlib.colors import ListedColormap, BoundaryNorm

cmap = ListedColormap(['white', 'green'])
# normalize the color map. 
# Values between -0.5 and 0.5 -> White
# Values between 0.5 and 1.5 -> green
norm = BoundaryNorm([-0.5, 0.5, 1.5], cmap.N)

def plot_eligible_area(ax1, ax2, tiff_path, europe, add_title, target_crs):

    # get the dissolved polygon
    europe_contour = (
        europe
        .to_crs(target_crs)
        .dissolve()
        .reset_index()
    )
    
    excluder_wind = ExclusionContainer(crs=target_crs)
    excluder_wind.add_raster(tiff_path, crs=target_crs)


    europe_countries = (
        europe
        .to_crs(target_crs)
    )

    mask_out=[]
    for country in europe_countries.index:
        # print(c)
        country_geom = europe_countries.loc[europe_countries.index==country,"geometry"]

        masked, _ = shape_availability(country_geom, excluder_wind)
        eligible_area = float(masked.sum()) * excluder_wind.res**2 # m2
        eligible_share = eligible_area / country_geom.geometry.item().area # %
        mask_out.append([country, eligible_area/1E6, eligible_share*100])

    mask_out = pd.DataFrame(mask_out,columns=["Country","area (km$^2$)","share (%)"]).round(1)
    mask_out = mask_out.sort_values(by="Country")

    excluder_wind.plot_shape_availability(
        europe_contour, 
        ax=ax1,
        show_kwargs={"cmap":cmap,"norm":norm},
    )

    title = ax1.get_title()

    # title = "{text1} perc% {text2}"
    text_title = title.split("%",1)
    text1_perc = text_title[0]
    text2 = text_title[1]

    perc_index = text1_perc.rfind(" ") #before the value, there is a space
    text1 = text1_perc[:perc_index+1]
    perc = round(float(text1_perc[perc_index+1:]),1)
    title = text1+str(perc)+"%"+text2

    new_title = add_title + title
    ax1.set_title(new_title, fontsize=14, weight="bold")

    ax1.set_xticks([])  # Remove x-axis ticks
    ax1.set_yticks([])  # Remove y-axis ticks
    # ax1.axis("off")

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
    table.auto_set_column_width([0])
    for j in range(len(col_labels)):
        cell = table.get_celld()[(0, j)]
        cell.get_text().set_fontweight('bold')
    
    ax2.axis("off")
    table.auto_set_font_size(False)
    table.set_fontsize(16)
    table.scale(1.1, 1.5)
    

def plot_eligible_area_no_table(ax, tiff_path, europe, add_title, target_crs):

    # get the dissolved polygon
    europe_contour = (
        europe
        .to_crs(target_crs)
        .dissolve()
        .reset_index()
    )


    excluder_wind = ExclusionContainer(crs=target_crs)
    excluder_wind.add_raster(tiff_path, crs=target_crs)
    excluder_wind.plot_shape_availability(
        europe_contour, 
        ax=ax,
        show_kwargs={"cmap":cmap,"norm":norm},
    )

    # round the %
    title = ax.get_title()
    # title = "{text1} perc% {text2}"
    text_title = title.split("%",1)
    text1_perc = text_title[0]
    text2 = text_title[1]
    perc_index = text1_perc.rfind(" ") #before the value, there is a space
    text1 = text1_perc[:perc_index+1]
    perc = round(float(text1_perc[perc_index+1:]),1)
    title = text1+str(perc)+"%"+text2

    new_title = add_title + title
    ax.set_title(new_title, fontsize=14, weight="bold")

    ax.set_xticks([])  # Remove x-axis ticks
    ax.set_yticks([])  # Remove y-axis ticks
    # ax.axis("off")


def plot_eligible_area_all_dim(ax, tiff_paths, europe, add_title, target_crs):
    excluder_wind = ExclusionContainer(crs=target_crs)
    for tiff_path in tiff_paths:
        excluder_wind.add_raster(tiff_path, crs=target_crs)

    # get the dissolved polygon
    europe_contour = (
        europe
        .to_crs(target_crs)
        .dissolve()
        .reset_index()
    )

    excluder_wind.plot_shape_availability(
        europe_contour,
        ax=ax,
        show_kwargs={"cmap":cmap,"norm":norm},
    )

    # round the %
    title = ax.get_title()
    # title = "{text1} perc% {text2}"
    text_title = title.split("%",1)
    text1_perc = text_title[0]
    text2 = text_title[1]
    perc_index = text1_perc.rfind(" ") #before the value, there is a space
    text1 = text1_perc[:perc_index+1]
    perc = round(float(text1_perc[perc_index+1:]),1)
    title = text1+str(perc)+"%"+text2

    new_title = add_title + title
    ax.set_title(new_title, fontsize=14, weight="bold")

    ax.set_xticks([])  # Remove x-axis ticks
    ax.set_yticks([])  # Remove y-axis ticks
    # ax.axis("off")