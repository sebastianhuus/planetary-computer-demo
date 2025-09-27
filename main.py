import numpy as np
import xarray as xr
import rasterio.features
import stackstac
import pystac_client
import planetary_computer
import odc.stac
import matplotlib.pyplot as plt

def main():
    print("Starting Planetary Computer example...")

    # Define area of interest (Seattle area)
    area_of_interest = {
        "type": "Polygon",
        "coordinates": [
            [
                [-122.27508544921875, 47.54687159892238],
                [-121.96128845214844, 47.54687159892238],
                [-121.96128845214844, 47.745787772920934],
                [-122.27508544921875, 47.745787772920934],
                [-122.27508544921875, 47.54687159892238]
            ]
        ]
    }
    bbox = rasterio.features.bounds(area_of_interest)
    print(f"Bounding box: {bbox}")

    # Search for Sentinel-2 images
    stac = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )

    search = stac.search(
        bbox=bbox,
        datetime="2016-01-01/2020-12-31",
        collections=["sentinel-2-l2a"],
        query={"eo:cloud_cover": {"lt": 25}}
    )

    items = search.item_collection()
    print(f"Found {len(items)} Sentinel-2 images")

    # Inspect first item to understand the data structure
    print("Inspecting first STAC item...")
    first_item = items[0]
    print(f"First item ID: {first_item.id}")
    print(f"First item bbox: {first_item.bbox}")
    print(f"First item geometry: {first_item.geometry}")

    # Try odc.stac.load instead of stackstac (more reliable for Planetary Computer)
    print("Loading data with odc.stac.load (recommended for Planetary Computer)...")
    limited_items = items[:5]  # Use 5 items for testing

    mosaic = odc.stac.load(
        limited_items,
        bands=["red", "green", "blue"],
        bbox=bbox,  # Use the bbox we calculated earlier
        resolution=60,  # 60 meter resolution
        crs="EPSG:32610"  # UTM Zone 10N
    )
    print(f"Mosaic type: {type(mosaic)}")
    print(f"Mosaic dims: {mosaic.dims}")
    print(f"Mosaic data variables: {list(mosaic.data_vars)}")
    print(f"Mosaic coordinates: {list(mosaic.coords)}")

    # Compute cloudless mosaic by taking median
    print("Computing cloudless mosaic (median)...")
    cloudless_mosaic = mosaic.median(dim="time")
    print(f"Cloudless mosaic type: {type(cloudless_mosaic)}")
    print(f"Cloudless mosaic data variables: {list(cloudless_mosaic.data_vars)}")

    # Display basic info about each band
    for band in cloudless_mosaic.data_vars:
        data_array = cloudless_mosaic[band]
        print(f"Band '{band}': shape={data_array.shape}, dtype={data_array.dtype}")

    print("Cloudless mosaic computation completed!")

    # Create and display RGB image
    print("Creating RGB composite image...")

    # Extract the bands and convert to numpy arrays
    red = cloudless_mosaic['red'].values
    green = cloudless_mosaic['green'].values
    blue = cloudless_mosaic['blue'].values

    # Stack bands into RGB array (height, width, 3)
    rgb = np.stack([red, green, blue], axis=-1)

    # Normalize values to 0-1 range for display
    # Sentinel-2 values are typically 0-10000, so we'll scale accordingly
    rgb_normalized = np.clip(rgb / 3000, 0, 1)  # Adjust divisor for brightness

    # Create the plot
    plt.figure(figsize=(12, 8))
    plt.imshow(rgb_normalized)
    plt.title('Cloudless Satellite Mosaic - Seattle Area\n(Sentinel-2 RGB Composite)', fontsize=14)
    plt.axis('off')  # Remove axes for cleaner image

    # Add some info text
    plt.figtext(0.02, 0.02, f'Data: {len(limited_items)} Sentinel-2 images, 60m resolution\nSource: Microsoft Planetary Computer',
                fontsize=10, style='italic')

    plt.tight_layout()
    plt.show()

    print("Image displayed! Close the window to continue.")

if __name__ == "__main__":
    main()