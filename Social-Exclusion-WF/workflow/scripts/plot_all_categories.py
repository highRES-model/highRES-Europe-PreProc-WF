import geopandas as gpd
import time
from atlite.gis import ExclusionContainer
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.gridspec as gridspec

from workflow.scripts.extra_functions import plot_eligible_area


# input data
europe_onshore_shp = snakemake.input.europe_onshore_shapefile
europe_offshore_shp = snakemake.input.europe_offshore_shapefile

# parameters
input_scenarios = pd.DataFrame(snakemake.params.input_scenarios)
workpath = snakemake.params.workpath

# output
output_path = snakemake.output.plot_path



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



t=time.time()

columns = list(input_scenarios.index)
rows = list(input_scenarios.columns)

fig = plt.figure(figsize=(len(columns)*4,len(columns)*3), layout="constrained")
gs = gridspec.GridSpec(len(rows), len(columns), figure=fig, wspace=0.05)

i = 0
for row in rows:
    j = 0
    for col in columns:
        file_path = workpath / "rasters" / f"{row}_{col}.tif"
        ax = fig.add_subplot(gs[i,j])
        if row=="Coastline":
            plot_eligible_area(ax, file_path, europe_offshore, f"{row} - {input_scenarios.loc[col,row]}nms\n", target_crs)
            print(f"{row} - {input_scenarios.loc[col,row]}nms - {time.time()-t}")
        elif row=="LandscapeVisualImpact":
            plot_eligible_area(ax, file_path, europe_onshore, f"{row} - {col}\n", target_crs)
            print(f"{row} - {input_scenarios.loc[col,row]} - {time.time()-t}")
        else:
            plot_eligible_area(ax, file_path, europe_onshore, f"{row} - {input_scenarios.loc[col,row]}m\n", target_crs)
            print(f"{row} - {input_scenarios.loc[col,row]}m - {time.time()-t}")

        j += 1

    i += 1
plt.savefig(output_path)