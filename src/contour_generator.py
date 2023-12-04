import rasterio
from rasterio import features
import geopandas as gpd
import matplotlib.pyplot as plt

def generate_contour_lines(input_raster_path, output_plot=True):
    """
    Generate contour lines from a raster file and optionally plot them.

    Parameters:
    - input_raster_path (str): Path to the input raster file.
    - output_plot (bool): Whether to plot the generated contour lines (default is True).

    Returns:
    - gdf (GeoDataFrame): GeoDataFrame containing contour lines.
    """

    # Open the raster file
    with rasterio.open(input_raster_path) as src:
        # Read the raster data
        raster_data = src.read(1)

        # Generate contours
        contours = features.shapes(raster_data, transform=src.transform)

        # Convert contours to GeoDataFrame
        gdf = gpd.GeoDataFrame(geometry=[shape for shape, value in contours],
                               data={'value': [value for shape, value in contours]})

    # Plot the contours if specified
    if output_plot:
        gdf.plot(column='value', cmap='viridis', legend=True)
        plt.show()

    return gdf

# Example usage:
input_raster_path = input('Please enter the path for your raster file:')
contour_lines_gdf = generate_contour_lines(input_raster_path, False)
