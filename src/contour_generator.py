from qgis.core import *

raster = [l for l in QgsProject().instance().mapLayers().values() if isinstance(l, QgsRasterLayer) and 'LochAlvaLidar' in l.name()][0]
result = processing.run("gdal:contour",
    {'INPUT':raster,
    'BAND': 1,
    'INTERVAL':10,
    'FIELD_NAME':'ELEV',
    'OUTPUT':'TEMP_OUTPUT'})

layer = QgsRasterLayer(result['OUTPUT'])
QgsProject.instance().addMapLayer(layer)