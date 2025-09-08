import geopandas as gpd
from shapely.geometry import Polygon
import shapely

from atlite.gis import ExclusionContainer

def get_bounding( target_crs, rectx1, rectx2, recty1, recty2):
    
    polygon = Polygon(
    [
        (rectx1, recty1),
        (rectx1, recty2),
        (rectx2, recty2),
        (rectx2, recty1),
        (rectx1, recty1),
    ]
    )
    polygon = shapely.segmentize(polygon, max_segment_length=0.5)
 
    return (
        gpd.GeoDataFrame(geometry=[polygon],crs="EPSG:4326")
        .to_crs(target_crs)
    )

def plot_eligible_area(ax, tiff_path, europe, add_title, target_crs):
    excluder_wind = ExclusionContainer(crs=target_crs)
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