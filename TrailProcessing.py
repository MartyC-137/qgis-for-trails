from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessingAlgorithm,
                       QgsProcessingException,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterRasterDestination)
from qgis import processing

class TrailProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This class takes a DEM as an argument, and produces a number of useful
    layers for trailbuilding.
    """

    # Input raster specified in the UI
    INPUT_RASTER = 'INPUT_RASTER'

    # Output contours
    OUTPUT_10M_CONTOURS = 'OUTPUT_10M_CONTOURS'
    OUTPUT_5M_CONTOURS = 'OUTPUT_5M_CONTOURS'
    OUTPUT_2M_CONTOURS = 'OUTPUT_2M_CONTOURS'

    # Output slope
    OUTPUT_SLOPE = 'OUTPUT_SLOPE'

    # Output Hillshade
    OUTPUT_HILLSHADE = 'OUTPUT_HILLSHADE'

    # Output Aspect
    OUTPUT_ASPECT = 'OUTPUT_ASPECT'

    # Output Relief
    OUTPUT_RELIEF = 'OUTPUT_RELIEF'

    # Output Ruggedness
    OUTPUT_RUGGEDNESS = 'OUTPUT_RUGGEDNESS'


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
                       - 10m contours
                       - Slope Raster
                       - Hillshade
                       - Relief
                       - Ruggedness
                       """)

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and outputs of the algorithm.
        """

        # Input raster layer
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER,
                self.tr('Input raster layer')
            )
        )
        
        # Contour outputs
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_10M_CONTOURS,
                self.tr('10m Contour output')
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_5M_CONTOURS,
                self.tr('5m Contour output')
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_2M_CONTOURS,
                self.tr('2m Contour output')
            )
        )

        # Slope output
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_SLOPE,
                self.tr('Slope output')
            )
        )

        # Hillshade output
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_HILLSHADE,
                self.tr('Hillshade output')
            )
        )

        # Aspect output
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_ASPECT,
                self.tr('Aspect output')
            )
        )

        # Relief output
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_RELIEF,
                self.tr('Relief output')
            )
        )

        # Ruggedness output
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_RUGGEDNESS,
                self.tr('Ruggedness output')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        input_raster = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER, context)
        
        if not input_raster:
            raise QgsProcessingException('A valid input raster is required for this operation.')
            
        contour_params_10m = {
            'INPUT': input_raster,
            'OUTPUT': parameters[self.OUTPUT_10M_CONTOURS],
            'BAND': 1,
            'INTERVAL': 10,
            'FIELD_NAME': 'ELEV'
        }
        
        contour_params_5m = {
            'INPUT': input_raster,
            'OUTPUT': parameters[self.OUTPUT_5M_CONTOURS],
            'BAND': 1,
            'INTERVAL': 5,
            'FIELD_NAME': 'ELEV'
        }

        contour_params_2m = {
            'INPUT': input_raster,
            'OUTPUT': parameters[self.OUTPUT_2M_CONTOURS],
            'BAND': 1,
            'INTERVAL': 2,
            'FIELD_NAME': 'ELEV'
        }

        slope_params = {
            'INPUT': input_raster,
            'Z_FACTOR':2,
            'OUTPUT': parameters[self.OUTPUT_SLOPE]
        }

        hillshade_params =  {
            'INPUT': input_raster,
            'BAND': 1,
            'Z_FACTOR': 2,
            'SCALE': 1,
            'AZIMUTH': 315,
            'ALTITUDE': 45,
            'COMPUTE_EDGES': False,
            'ZEVENBERGEN': False,
            'COMBINED': False,
            'MULTIDIRECTIONAL': True,
            'OPTIONS': '',
            'EXTRA': '',
            'OUTPUT': parameters[self.OUTPUT_HILLSHADE]
        }

        aspect_params = {
            'INPUT': input_raster,
            'BAND': 1,
            'TRIG_ANGLE': False,
            'ZERO_FLAT': False,
            'COMPUTE_EDGES': False,
            'ZEVENBERGEN': False,
            'OPTIONS': '',
            'EXTRA': '',
            'OUTPUT': parameters[self.OUTPUT_ASPECT]
        }

        relief_params = {
            'INPUT': input_raster,
            'Z_FACTOR': 2,
            'AUTO_COLORS': True,
            'COLORS': '',
            'OUTPUT': parameters[self.OUTPUT_RELIEF]
        }

        ruggedness_params = {
            'INPUT': input_raster,
            'Z_FACTOR':2,
            'OUTPUT':parameters[self.OUTPUT_RUGGEDNESS]
        }

        # Contours
        processing.run('gdal:contour', contour_params_10m, context = context, feedback = feedback)
        processing.run('gdal:contour', contour_params_5m, context = context, feedback = feedback)
        processing.run('gdal:contour', contour_params_2m, context = context, feedback = feedback)

        # # Slope
        processing.run("native:slope", slope_params, context = context, feedback = feedback)

        # Hillshade
        processing.run("gdal:hillshade", hillshade_params, context = context, feedback = feedback)

        # Aspect
        processing.run("gdal:aspect", aspect_params, context = context, feedback = feedback)

        # Relief
        processing.run("qgis:relief", relief_params, context = context, feedback = feedback)

        # Ruggedness
        processing.run("native:ruggednessindex", ruggedness_params, context = context, feedback = feedback)

        return {}
