from osgeo import gdal
from dem_stitcher.rio_window import read_raster_from_window
from rasterio.warp import transform_bounds
from pathlib import Path
from rasterio.crs import CRS
from shapely.geometry import box
import geopandas as gpd



def build_peckel_vrt(extent: list,
                     out_path: Path):
    df_peckel_data = gpd.read_file('peckel_tiles.geojson')
    bbox = box(*extent)
    ind_inter = df_peckel_data.geometry.intersects(bbox)
    df_subset = df_peckel_data[ind_inter].reset_index(drop=True)
    gdal.BuildVRT(str(out_path), df_subset.source_url.tolist())
    return out_path

def get_peckel_occ_raster(extent:list) -> tuple:
    tmp_vrt = Path('peckel_data_tmp.vrt')
    build_peckel_vrt(extent, tmp_vrt)
    X, p = read_raster_from_window(tmp_vrt,
                                   extent,
                                   CRS.from_epsg(4326))
    tmp_vrt.unlink()
    p['driver'] = 'GTiff'
    return X, p
