import rasterio
from rasterio.features import geometry_mask
import geopandas as gpd
import os
import glob

def rasterize(template_geotiff, geojson_file, output_raster_file):
    # Open the template GeoTIFF to obtain its geospatial information
    with rasterio.open(template_geotiff) as src:
        width = src.width
        height = src.height
        transform = src.transform
        crs = src.crs

    # Create a new raster image using the template's geospatial information
    with rasterio.open(
        output_raster_file,
        'w',
        driver='GTiff',
        width=width,
        height=height,
        count=1,  # Number of bands
        dtype=rasterio.uint8,  # Data type for the raster
        crs=crs,  # Coordinate Reference System
        transform=transform
    ) as dst:
        # Read the GeoJSON file
        gdf = gpd.read_file(geojson_file)
        gdf.to_crs(crs=crs, inplace=True)
        out_shape = (height, width)  # Define the output shape
        # Rasterize the GeoJSON features onto the raster image
        mask = geometry_mask(gdf['geometry'], transform=dst.transform, out_shape=out_shape, invert=False)
        dst.write(mask, 1)  # Write the mask to band 1

    print(f"Rasterized image saved to '{output_raster_file}'.")    


outPath = "new_masks"
if not os.path.exists(outPath):
   os.makedirs(outPath)


S2_data = "S2_data"

fileNames = glob.glob("geoJson/*.geojson")
for geojson_file in fileNames:
    print("process file %s"%geojson_file)
    id_ = geojson_file.split("/")[1].split(".")[0].split("_")[1]
    template_geotiff = S2_data+"/"+"img_"+id_+".tif"
    output_raster_file = outPath+"/new_mask_"+id_+".tif"
    rasterize(template_geotiff, geojson_file, output_raster_file)