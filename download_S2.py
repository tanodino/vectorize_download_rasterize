import rasterio as rio
import rasterio.mask
import pystac_client
import planetary_computer
#import rich
import xarray as xr
#import rioxarray as rioxr

# library for turning STAC objects into xarrays
import stackstac
import numpy as np
from script_extractBB import getBBox
import glob
import warnings
import os

warnings.simplefilter(action='ignore', category=FutureWarning)

#TILE = ['31UFP' '31UFQ']

def createGeoTiff(xarray, outputFileName):
    array_npy = xarray.to_numpy()
    #print(array_npy.shape)
    n_bands, height, width = array_npy.shape
    # Define the metadata for the GeoTIFF
    metadata = {
        'driver': 'GTiff',
        'height': height,
        'width': width,
        'count': n_bands,  # Number of bands
        'dtype': 'uint16',  # Data type of the array
        'crs': xarray.attrs['crs'],  # Coordinate Reference System (e.g., WGS84)
        'transform': xarray.attrs['transform'],
    }
    # Create the GeoTIFF file and write the data
    with rasterio.open(outputFileName, 'w', **metadata) as dst:
        dst.write(array_npy)  # Write the data to band 1

def getRasterData(extent, outputFileName):
    catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
    )

    collections = ['sentinel-2-l2a']
    time_range = "2018-10-01/2018-10-31"

    search = catalog.search(
        collections=collections,
        datetime=time_range,
        #query =  {"eo:cloud_cover":{"lt":5}, "s2:mgrs_tile":{"eq":'31UFP'}},
        query =  {"eo:cloud_cover":{"lt":5}},
        bbox=extent
    )

    items = search.get_all_items()
    #print(f"{len(items)} items found with the `bbox` parameter")
    '''
    result_array = []
    for it in items:
        result_array.append( it.properties["s2:mgrs_tile"] )
        print("\t ",it)
    #exit()
    result_array = np.array(result_array)
    result_array = np.unique(result_array)
    return result_array
    '''
    
    bands = ['B02', 'B03', 'B04', 'B8A', 'B05', 'B06', 'B07', 'B08', 'B11', 'B12']
    FILL_VALUE = 2**16-1
    array = stackstac.stack(
                        items[-1],
                        assets = bands,
                        resolution=10,
                        dtype="uint16",
                        fill_value=FILL_VALUE,
                        bounds_latlon=extent,
                        )
    #print(array)

    #print("=====")

    #dd = array.coords['time']
    #print(dd)
    #print(array)
    
    sel_array = array[-1,:,:,:]  
    #array_npy = sel_array.to_numpy()
    #print(array_npy.shape)
    #exit()  
    createGeoTiff(sel_array, outputFileName)
    

outPath = "S2_data"
if not os.path.exists(outPath):
   os.makedirs(outPath)



fileNames = glob.glob("geoJson/*.geojson")
for fName in fileNames:
    print("processing %s"%fName)
    #fName = "geoJson/mask_88.geojson"
    prefix = fName.split("/")[1].split(".")[0].split("_")[1]
    extent = getBBox(fName)    
    print(extent)
    outputFileName = outPath+"/img_"+prefix+".tif"
    getRasterData(extent, outputFileName)
    #exit()
    #print(res)

#extent = [5.078178011635032, 48.728203996144586, 5.083629916803431, 48.73230385892366]
#outputFileName = "output.tif"
#res = getRasterData(extent, outputFileName)
#print(res)