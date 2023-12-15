from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingException,
                       QgsProcessingOutputNumber,
                       QgsProcessingParameterDistance,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterRasterDestination,
                       QgsProject,
                       QgsRasterLayer)
from qgis import processing


class TrailProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This class takes a DEM as an argument, and produces a number of useful
    layers for trailbuilding.
    """
    INPUT_RASTER = 'INPUT_RASTER'
    OUTPUT_2M_CONTOURS = 'OUTPUT_2M_CONTOURS'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        # Must return a new copy of your algorithm.
        return TrailProcessingAlgorithm()

    def name(self):
        """
        Returns the unique algorithm name.
        """
        return 'traillayers'

    def displayName(self):
        """
        Returns the translated algorithm name.
        """
        return self.tr('Generate Trail Layers')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to.
        """
        return self.tr('Trail Tools')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs
        to.
        """
        return 'trailscripts'

    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return self.tr("""This tool takes a DEM as input and 
                       produces the following:
                       - 2m contours
                       - 5m contours
                       - 10m contours""")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and outputs of the algorithm.
        """
        # 'INPUT' is the recommended name for the main input
        # parameter.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER,
                self.tr('Input raster layer')
            )
        )
        # 'OUTPUT' is the recommended name for the main output
        # parameter.
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_2M_CONTOURS,
                self.tr('2m Contour output')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        
        input_raster = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER, context)
        
        if not input_raster:
            raise QgsProcessingException('A valid input raster is required for this operation.')
            
        alg_params = {
            'INPUT': input_raster,
            'OUTPUT': parameters[self.output_raster],
            'BAND': 1,
            'INTERVAL': 2,
            'FIELD_NAME': 'ELEV'
        }
        
        processing.run('gdal:contour', alg_params, context = context, feedback = feedback)
        
        return {}