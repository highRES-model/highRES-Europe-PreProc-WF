import time,shapely
import numpy as np
import geopandas as gpd
import xarray as xr
import pandas as pd
from shapely.geometry import Polygon
from scipy.ndimage import binary_dilation as dilation
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
import rasterio as rio


def env_constraint_defs(lvl):
    
    env={}
    
    env["low"]={
            "iucn_filter":["Ia","Ib","II","III","IV"],
            "buffer":0,
            "natura":False,
            "birds_bats":False,
            "peat":False
            }
    
    
    env["medium"]={
            "iucn_filter":"../../existing_farms_comparison/windfarm_analysis/protected_areas/cdda/all/CountryStats_cdda_boku_pixels_all_notouched.csv",
            "buffer":0,
            "birds_bats":True,
            "birds_bats_data":"birds_and_bats_vulnerability.tif",
            "birds_bats_filter":"../../existing_farms_comparison/windfarm_analysis/birds_bats/all/percentile_overlap.csv",
            "natura":True,
            "natura_filter":"../../existing_farms_comparison/windfarm_analysis/protected_areas/natura/all/CountryStats_natura_boku_pixels_all_notouched.csv",
            "peat":False,
            "forests":True,
            "forests_filter":"../../existing_farms_comparison/windfarm_analysis/forests/forests_overlap.csv"
            }
    
    
    env["high"]={
            "iucn_filter":["Ia",	
                    "Ib",
                    "II",	
                    "III",	
                    "IV",	
                    "V",	
                    "VI",	
                    "notReported",	
                    "notAssigned",
                    "notApplicable"],
            "buffer":2000,
            "birds_bats":False,
            "natura":True,
            "natura_filter":"all",
            "peat":True,
            "forests":True,
            "forests_filter":"all"
            }
    
    return env[lvl]

def get_europe(wf_path):
    
    aggregated_regions = [
    "AT",
    "BE",
    "BG",
    "CH",
    "CZ",
    "DE",
    "DK",
    "EE",
    "ES",
    "FI",
    "FR",
    "UK",
    "GR",
    "HR",
    "HU",
    "IE",
    "IT",
    "LT",
    "LU",
    "LV",
    "NL",
    "NO",
    "PL",
    "PT",
    "RO",
    "SE",
    "SI",
    "SK",
    ]
    
    europe = (
    gpd
    .read_file(wf_path+'shapes/NUTS_RG_01M_2021_4326.geojson')
    .replace({"EL": "GR"})
    .query("NUTS_ID == @aggregated_regions")
    .set_index(["NUTS_ID"])
    .loc[:,['geometry']]
    )
    
    
    # The square outer boundaries of Europe to consider, because we have downloaded ERA5 for this extent:
    rectx1 = -12
    rectx2 = 44
    recty1 = 33
    recty2 = 72
    
    polygon = Polygon(
    [
        (rectx1, recty1),
        (rectx1, recty2),
        (rectx2, recty2),
        (rectx2, recty1),
        (rectx1, recty1),
    ]
    )
    europe = gpd.clip(europe, polygon)
    
    return europe.to_crs("EPSG:3035")


def get_country_codes():

    country_codes = {
    "Austria" : "AT",
    "Belgium" : "BE",
    "Bulgaria" : "BG", #
    "Switzerland" : "CH", #
    "Czech Republic" : "CZ", #
    "Germany" : "DE",
    "Denmark" : "DK",
    "Estonia" : "EE" ,
    "Spain" : "ES",
    "Finland" : "FI", #
    "France" : "FR",
    "United Kingdom" : "UK",
    "Greece" : "GR",
    "Croatia" : "HR", #
    "Hungary" : "HU", #
    "Ireland" : "IE",
    "Italy" : "IT",
    "Lithuania" : "LT",
    "Luxembourg" : "LU",
    "Latvia" : "LV",
    "Netherlands" : "NL",
    "Norway" : "NO",
    "Poland" : "PL", #
    "Portugal" : "PT",
    "Romania" : "RO", #
    "Sweden" : "SE",
    "Slovenia" : "SI", #
    "Slovakia" : "SK" #
    }
    
    return country_codes

def _as_transform(x, y):
    lx, rx = x[[0, -1]]
    ly, uy = y[[0, -1]]

    dx = float(rx - lx) / float(len(x) - 1)
    dy = float(uy - ly) / float(len(y) - 1)

    return rio.Affine(dx, 0, lx - dx / 2, 0, dy, ly - dy / 2)

def padded_transform_and_shape(bounds, res):
    """
    Get the (transform, shape) tuple of a raster with resolution `res` and
    bounds `bounds`.
    """
    left, bottom = ((b // res) * res for b in bounds[:2])
    right, top = ((b // res + 1) * res for b in bounds[2:])
    shape = int((top - bottom) / res), int((right - left) / res)
    return rio.Affine(res, 0, left, 0, -res, top), shape


def get_bounding():
    
    rectx1 = -12
    rectx2 = 44
    recty1 = 33
    recty2 = 72
    
    polygon = Polygon(
    [
        (rectx1, recty1),
        (rectx1, recty2),
        (rectx2, recty2),
        (rectx2, recty1),
        (rectx1, recty1),
    ]
    )
    

    
    polygon=shapely.segmentize(polygon, max_segment_length=0.5)
    
    b=gpd.GeoDataFrame(geometry=[polygon],crs="EPSG:4326")
 
    
    return b.to_crs("EPSG:3035")


def build_cdda(iucn):

    d=(gpd.read_file("./cdda_natura/cdda_BOKU_iucnCats.gpkg")
       .query("iucnCategory in @iucn")
       .loc[:,["geomType","geometry"]])
    
    # buffer points by 100m
    
    d.loc[d["geomType"]=="point","geometry"]=d.loc[d["geomType"]=="point",:].buffer(100)
    
    return d

def build_cdda_by_country(by_country,thresh=15.0,min_wf=5):
    
    country_codes=get_country_codes()
    
    by_country=(pd.read_csv(by_country,skiprows=1)
                .loc[:,["country",
                        "Ia (% pixels)",	
                         "Ib (% pixels)",
                         "II (% pixels)",	
                         "III (% pixels)",	
                         "IV (% pixels)",	
                         "V (% pixels)",	
                         "VI (% pixels)",	
                         "notReported (% pixels)",	
                         "notAssigned (% pixels)",
                         "notApplicable (% pixels)",
                         "total_windfarms"]]
                )
    
    
    by_country.country=by_country.country.replace(country_codes)
    
    shp=(gpd.read_file("./cdda_natura/cdda_BOKU_iucnCats.gpkg")
         .replace({"EL": "GR"}))
    
    
    cats=shp.iucnCategory.unique()
    
    cdda_out=[]
    for _,row in by_country.iterrows():
        cnt=row.country
        for cat in cats: 
            if row[f"{cat} (% pixels)"] < thresh and row["total_windfarms"] > min_wf:
                cdda_out.append(
                    shp.query("cddaRegionCode == @cnt and iucnCategory == @cat").loc[:,["cddaRegionCode","iucnCategory","geomType","geometry"]])
            
            # if a country only has a small number of wfs then assume all cats are excluded
            elif row["total_windfarms"] < min_wf:
                cdda_out.append(
                    shp.query("cddaRegionCode == @cnt and iucnCategory == @cat").loc[:,["cddaRegionCode","iucnCategory","geomType","geometry"]])
            else:
                print(f"No exclusion for: {cat} in {cnt}")
            
    cdda_out=pd.concat(cdda_out)
            
    cdda_out.loc[cdda_out["geomType"]=="point","geometry"]=cdda_out.loc[cdda_out["geomType"]=="point",:].buffer(100)
    
    return cdda_out

def build_filter(by_country,cols,thresh=15.0,min_wf=5):
    
    country_codes=get_country_codes()
    
    by_country=(pd.read_csv(by_country,skiprows=1)
                .loc[:,cols])
    
    by_country.country=by_country.country.replace(country_codes)
    
    sel=(by_country.iloc[:,1] > min_wf) & (by_country.iloc[:,2] < thresh)
            
    return by_country.country[sel]

def build_filter_bb(by_country,thresh=15.0,min_wf=10):
    
    country_codes=get_country_codes()
    
    by_country=pd.read_csv(by_country,skiprows=1)
    
    by_country.country=by_country.country.replace(country_codes)
    by_country=by_country.set_index("country",drop=True)
    
    sel_wf=(by_country["Num_windFarms"] > min_wf)
    
    sel=(by_country.loc[sel_wf,"60":"90"] < thresh)
            
    return sel.loc[sel.any(axis=1),:]

def build_natura(natura_by_country,thresh=15.0,min_wf=5):
    
    shp=gpd.read_file("./cdda_natura/natura.2000_BOKU.gpkg")
    
    country_codes=get_country_codes()
    
    by_country=(pd.read_csv(natura_by_country,skiprows=1)
                .loc[:,["country","ABC (% pixels)","total_windfarms"]])
    
    by_country.country=by_country.country.replace(country_codes)
    
    nat_out=[]
    for _,(cnt,pct,tot_area) in by_country.iterrows():
        if pct < thresh and tot_area > min_wf:
            nat_out.append(shp.query("MS == @cnt").loc[:,["MS","geometry"]])
        elif tot_area < min_wf:
            nat_out.append(shp.query("MS == @cnt").loc[:,["MS","geometry"]])
        else:
            print(f"No exclusion for: natura2k in {cnt}")
            
    return pd.concat(nat_out)


# def build_raster_by_country(ds):
    
#     europe=get_europe()
    
#     ds=
    

def env_build_by_country():
    
    wf_path="D:/science/models/highRES/model_versions/highRES-Europe-WF/shared_input/geodata/onshore/"
    
    lvls=["medium"]
    
    thresh=15.
    
    for lvl in lvls:
    
        c=env_constraint_defs(lvl)
    
        dst_transform, shape=padded_transform_and_shape(rio.features.bounds(get_bounding()), 100)
        
        out=np.zeros(shape, np.uint8) 
        
        to_raster=[]
        
        if type(c["iucn_filter"])==list:
            print("Exclude CDDA based on list")
            
            to_raster.append(build_cdda(c["iucn_filter"]))
        else:
            print("Exclude country specific CDDA")
            
            to_raster.append(build_cdda_by_country(c["iucn_filter"],thresh=thresh))
            
        if c["natura"]:
            
            if c["natura_filter"]=="all":
                print("Exclude all natura2k")
                shp=gpd.read_file("./cdda_natura/natura.2000_BOKU.gpkg")
                to_raster.append(shp)
            else:
                print("Exclude country specific natura2k")
                to_raster.append(build_natura(c["natura_filter"],thresh=thresh))
                
        for shp in to_raster:
            shp["area"]=1
            shp["area"]=shp["area"].astype("uint8")
        
            out=out+rio.features.rasterize(zip(shp.geometry,shp["area"].values),
                               out_shape=shape,
                               transform=dst_transform,
                               fill=0,
                               all_touched=True)
            
        # if requested add buffer for cdda and natura
            
        if c["buffer"] !=0:
            iterations = int(c["buffer"] / 100) + 1
            out = dilation(out, iterations=iterations).astype("uint8")
        
        if c["birds_bats"]:
            
            print("Adding birds and bats exclusion")
            
            if c["birds_bats_filter"]=="all":
                
                print("All countries at same quantile")
                
                europe=get_europe(wf_path)
                
                src=rio.open("./birds_bats/"+c["birds_bats_data"])
                
                src_data = src.read(1)
                src_transform = src.transform
                
                temp=np.zeros(src_data.shape, dtype=np.uint8)
                
                for cnt,geom in europe.iterrows():
      
                    in_cnt=~geometry_mask(geom,
                                   src_data.shape,
                                   src_transform,
                                   all_touched=False)
                    
                    cnt_data=src_data.copy()
                    
                    cnt_data[~in_cnt]=np.nan
                    
                    quant=np.nanpercentile(cnt_data,c["birds_bats_quantile"])

                    temp[in_cnt & (src_data > quant)]=1
                    
                destination = np.zeros(shape, np.uint8)
                
                rio.warp.reproject(temp,
                                     destination,
                                     src_transform=src_transform,
                                     src_crs=src.crs,
                                     dst_transform=dst_transform,
                                     dst_crs=src.crs,
                                     resampling=Resampling.nearest,
                                     num_threads=2)
        
                out=out+destination
                
            else:    
            
                print("Excluding country specific BB")
                
                cnt_sel=build_filter_bb(c["birds_bats_filter"],thresh=thresh)
                
                europe=get_europe(wf_path).query("NUTS_ID in @cnt_sel.index")
            
                src=rio.open("./birds_bats/"+c["birds_bats_data"])
                
                src_data = src.read(1)
                src_transform = src.transform
                
                temp=np.zeros(src_data.shape, dtype=np.uint8)
                
                for cnt,geom in europe.iterrows():
                    
                    quantile=cnt_sel.columns[cnt_sel.loc[cnt_sel.index==cnt,:].values[0]][0]
   
                    in_cnt=~geometry_mask(geom,
                                   src_data.shape,
                                   src_transform,
                                   all_touched=False)
                    
                    cnt_data=src_data.copy()
                    
                    cnt_data[~in_cnt]=np.nan
                    
                    quant=np.nanpercentile(cnt_data,float(quantile))

                    temp[in_cnt & (src_data > quant)]=1
                    
                destination = np.zeros(shape, np.uint8)
                
                rio.warp.reproject(temp,
                                     destination,
                                     src_transform=src_transform,
                                     src_crs=src.crs,
                                     dst_transform=dst_transform,
                                     dst_crs=src.crs,
                                     resampling=Resampling.nearest,
                                     num_threads=2)
        
                out=out+destination
                
        if c["peat"]:
            
            print("Excluding peat")
 
            src=rio.open("./corine/corine.tif")
            
            src_data=src.read(1)
            src_transform = src.transform
            
            sel=(src_data==36)
            
            src_data=np.where(sel,1,0)
     
            peat = np.zeros(shape, np.uint8)
        
            rio.warp.reproject(src_data,
                             peat,
                             src_transform=src_transform,
                             src_crs=src.crs,
                             dst_transform=dst_transform,
                             dst_crs=src.crs,
                             resampling=Resampling.nearest,
                             num_threads=2)
            
            out=out+peat
            
        if c["forests"]:
            
            if c["forests_filter"]=="all":
            
                print("Excluding all forests")
     
                src=rio.open("./corine/corine.tif")
                
                src_data=src.read(1)
                src_transform = src.transform
                
                # removed agro forests
                
                sel=((src_data==22) | (src_data==23) | (src_data==24) | (src_data==25))
                
                src_data=np.where(sel,1,0)
     
                forests = np.zeros(shape, np.uint8)
            
                rio.warp.reproject(src_data,
                                 forests,
                                 src_transform=src_transform,
                                 src_crs=src.crs,
                                 dst_transform=dst_transform,
                                 dst_crs=src.crs,
                                 resampling=Resampling.nearest,
                                 num_threads=2)
                
                out=out+forests
                
            else:
                
                print("Excluding country specific Forests")
                
                cnt_sel=build_filter(c["forests_filter"],["country","Num of WF","Total"],thresh=thresh)

                europe=get_europe(wf_path).query("NUTS_ID in @cnt_sel")
                
                src=rio.open("./corine/corine.tif")
                
                src_data = src.read(1)
                src_transform = src.transform
                
                temp=np.zeros(src_data.shape, dtype=np.uint8)
                
                sel=((src_data==22) | (src_data==23) | (src_data==24) | (src_data==25))
                
                for cnt,geom in europe.iterrows():
                    
                    in_cnt=~geometry_mask(geom,
                                   src_data.shape,
                                   src_transform,
                                   all_touched=False)
                    
                    temp[in_cnt & sel]=1
                    
                forests = np.zeros(shape, np.uint8)
                
                rio.warp.reproject(temp,
                                     forests,
                                     src_transform=src_transform,
                                     src_crs=src.crs,
                                     dst_transform=dst_transform,
                                     dst_crs=src.crs,
                                     resampling=Resampling.nearest,
                                     num_threads=2)
        
                out=out+forests
        
                
        out[out>=1]=1
            
        with rio.open(
            f"environmental_{lvl}_forests_test.tif",
            mode="w",
            driver="GTiff",
            height=out.shape[0],
            width=out.shape[1],
            count=1,
            dtype=out.dtype,
            #dtype=np.uint8,
            #crs=pc.rio.crs,
            crs="EPSG:3035",
            transform=dst_transform,
            compress='lzw',
            ) as new_dataset:
                new_dataset.write(out, 1)
            

    
    
env_build_by_country()

