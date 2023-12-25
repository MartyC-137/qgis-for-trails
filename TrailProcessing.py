from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterVectorDestination,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterProviderConnection,
    QgsProcessingParameterDatabaseSchema,
)
from qgis import processing


class TrailProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This class takes a DEM as an argument, and produces a number of useful
    layers for trailbuilding.
    """

    DATABASE = "DATABASE"
    SCHEMA = "SCHEMA"

    # Input raster specified in the UI
    INPUT_RASTER = "INPUT_RASTER"

    # Output contours
    OUTPUT_10M_CONTOURS = "OUTPUT_10M_CONTOURS"
    OUTPUT_5M_CONTOURS = "OUTPUT_5M_CONTOURS"
    OUTPUT_2M_CONTOURS = "OUTPUT_2M_CONTOURS"

    # Output slope
    OUTPUT_SLOPE = "OUTPUT_SLOPE"

    # Output Hillshade
    OUTPUT_HILLSHADE = "OUTPUT_HILLSHADE"

    # Output Aspect
    OUTPUT_ASPECT = "OUTPUT_ASPECT"

    # Output Relief
    OUTPUT_RELIEF = "OUTPUT_RELIEF"

    # Output Ruggedness
    OUTPUT_RUGGEDNESS = "OUTPUT_RUGGEDNESS"

    # Output Black Diamond Polygons
    OUTPUT_BLACK_DIAMOND = "OUTPUT_BLACK_DIAMOND"

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        # Must return a new copy of your algorithm.
        return TrailProcessingAlgorithm()

    def name(self):
        """
        Returns the unique algorithm name.
        """
        return "traillayers"

    def displayName(self):
        """
        Returns the translated algorithm name.
        """
        return self.tr("Generate Trail Layers")

    def group(self):
        """
        Returns the name of the group this algorithm belongs to.
        """
        return self.tr("Trail Tools")

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs
        to.
        """
        return "trailscripts"

    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return self.tr(
            """This tool takes a DEM as input and 
                       produces the following:
                       - 2m contours
                       - 5m contours
                       - 10m contours
                       - Slope Raster
                       - Hillshade
                       - Relief
                       - Ruggedness
                       - Polygons of Black Diamond Terrain (Slope >= 15 and Slope <= 30)
                       """
        )

    def initAlgorithm(self, config=None):
        """
        Here we define the parameters for the script.
        """

        # Input raster layer
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER, self.tr("Input raster layer")
            )
        )

        # Contour Outputs
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_10M_CONTOURS, self.tr("10m Contour output")
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_5M_CONTOURS, self.tr("5m Contour output")
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_2M_CONTOURS, self.tr("2m Contour output")
            )
        )

        # Slope Output
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_SLOPE, self.tr("Slope output")
            )
        )

        # Hillshade Output
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_HILLSHADE, self.tr("Hillshade output")
            )
        )

        # Aspect Output
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_ASPECT, self.tr("Aspect output")
            )
        )

        # Relief Output
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_RELIEF, self.tr("Relief output")
            )
        )

        # Ruggedness Output
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_RUGGEDNESS, self.tr("Ruggedness output")
            )
        )

        # Black Diamond Polygons output
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_BLACK_DIAMOND, self.tr("Black Diamond (Difficult) Polygons")
            )
        )

        # Available PostGIS databases
        self.addParameter(
            QgsProcessingParameterProviderConnection(
                self.DATABASE,
                self.tr("Database"),
                "postgres",
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterDatabaseSchema(
                self.SCHEMA,
                self.tr("Schema"),
                defaultValue="public",
                connectionParameterName=self.DATABASE,
                optional=True,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        input_raster = self.parameterAsRasterLayer(
            parameters, self.INPUT_RASTER, context
        )

        if not input_raster:
            raise QgsProcessingException(
                "A valid input raster is required for this operation."
            )

        ########## Contours ##########

        # Contour Parameter Dictionaries #
        contour_params_10m = {
            "INPUT": input_raster,
            "OUTPUT": parameters[self.OUTPUT_10M_CONTOURS],
            "BAND": 1,
            "INTERVAL": 10,
            "FIELD_NAME": "ELEV",
        }

        contour_params_5m = {
            "INPUT": input_raster,
            "OUTPUT": parameters[self.OUTPUT_5M_CONTOURS],
            "BAND": 1,
            "INTERVAL": 5,
            "FIELD_NAME": "ELEV",
        }

        contour_params_2m = {
            "INPUT": input_raster,
            "OUTPUT": parameters[self.OUTPUT_2M_CONTOURS],
            "BAND": 1,
            "INTERVAL": 2,
            "FIELD_NAME": "ELEV",
        }

        # Process Contours
        results_10m = processing.run(
            "gdal:contour", contour_params_10m, context=context, feedback=feedback
        )

        results_5m = processing.run(
            "gdal:contour", contour_params_5m, context=context, feedback=feedback
        )

        results_2m = processing.run(
            "gdal:contour", contour_params_2m, context=context, feedback=feedback
        )

        # Upload contours to PostGIS
        if parameters[self.DATABASE]:
            postgis_10m = {
                "INPUT": results_10m["OUTPUT"],
                "DATABASE": parameters[self.DATABASE],
                "SCHEMA": parameters[self.SCHEMA],
                "TABLENAME": "10m_contours",
                "PRIMARY_KEY": "",
                "GEOMETRY_COLUMN": "geom",
                "ENCODING": "UTF-8",
                "OVERWRITE": True,
                "CREATEINDEX": True,
                "LOWERCASE_NAMES": True,
                "DROP_STRING_LENGTH": False,
                "FORCE_SINGLEPART": False,
            }

            postgis_5m = {
                "INPUT": results_5m["OUTPUT"],
                "DATABASE": parameters[self.DATABASE],
                "SCHEMA": parameters[self.SCHEMA],
                "TABLENAME": "5m_contours",
                "PRIMARY_KEY": "",
                "GEOMETRY_COLUMN": "geom",
                "ENCODING": "UTF-8",
                "OVERWRITE": True,
                "CREATEINDEX": True,
                "LOWERCASE_NAMES": True,
                "DROP_STRING_LENGTH": False,
                "FORCE_SINGLEPART": False,
            }

            postgis_2m = {
                "INPUT": results_2m["OUTPUT"],
                "DATABASE": parameters[self.DATABASE],
                "SCHEMA": parameters[self.SCHEMA],
                "TABLENAME": "2m_contours",
                "PRIMARY_KEY": "",
                "GEOMETRY_COLUMN": "geom",
                "ENCODING": "UTF-8",
                "OVERWRITE": True,
                "CREATEINDEX": True,
                "LOWERCASE_NAMES": True,
                "DROP_STRING_LENGTH": False,
                "FORCE_SINGLEPART": False,
            }

            processing.run(
                "native:importintopostgis",
                postgis_10m,
                context=context,
                feedback=feedback,
            )
            processing.run(
                "native:importintopostgis",
                postgis_5m,
                context=context,
                feedback=feedback,
            )
            processing.run(
                "native:importintopostgis",
                postgis_2m,
                context=context,
                feedback=feedback,
            )

        if feedback.isCanceled():
            return {}

        # ---------------------------------------------------------------------

        ########## Hillshade ##########
        hillshade_params = {
            "INPUT": input_raster,
            "BAND": 1,
            "Z_FACTOR": 2,
            "SCALE": 1,
            "AZIMUTH": 315,
            "ALTITUDE": 45,
            "COMPUTE_EDGES": False,
            "ZEVENBERGEN": False,
            "COMBINED": False,
            "MULTIDIRECTIONAL": True,
            "OPTIONS": "",
            "EXTRA": "",
            "OUTPUT": parameters[self.OUTPUT_HILLSHADE],
        }

        results_hillshade = processing.run(
            "gdal:hillshade", hillshade_params, context=context, feedback=feedback
        )

        if feedback.isCanceled():
            return {}

        # ---------------------------------------------------------------------

        ########## Aspect ##########
        aspect_params = {
            "INPUT": input_raster,
            "BAND": 1,
            "TRIG_ANGLE": False,
            "ZERO_FLAT": False,
            "COMPUTE_EDGES": False,
            "ZEVENBERGEN": False,
            "OPTIONS": "",
            "EXTRA": "",
            "OUTPUT": parameters[self.OUTPUT_ASPECT],
        }

        results_aspect = processing.run("gdal:aspect", aspect_params)

        if feedback.isCanceled():
            return {}

        # ---------------------------------------------------------------------

        ########## Relief ##########
        relief_params = {
            "INPUT": input_raster,
            "Z_FACTOR": 2,
            "AUTO_COLORS": True,
            "COLORS": "",
            "OUTPUT": parameters[self.OUTPUT_RELIEF],
        }

        results_relief = processing.run(
            "qgis:relief", relief_params, context=context, feedback=feedback
        )

        if feedback.isCanceled():
            return {}

        # ---------------------------------------------------------------------

        ########## Ruggedness ##########
        ruggedness_params = {
            "INPUT": input_raster,
            "Z_FACTOR": 2,
            "OUTPUT": parameters[self.OUTPUT_RUGGEDNESS],
        }

        results_ruggedness = processing.run(
            "native:ruggednessindex",
            ruggedness_params,
            context=context,
            feedback=feedback,
        )

        if feedback.isCanceled():
            return {}

        # ---------------------------------------------------------------------

        ########## Slope ##########
        slope_params = {
            "INPUT": input_raster,
            "Z_FACTOR": 2,
            "OUTPUT": parameters[self.OUTPUT_SLOPE],
        }

        results_slope = processing.run(
            "native:slope", slope_params, context=context, feedback=feedback
        )

        if feedback.isCanceled():
            return {}

        # ---------------------------------------------------------------------

        ########## Black Diamond Polygons ##########

        slope_black_diamond_params = {
            "INPUT_A": results_slope["OUTPUT"],
            "BAND_A": 1,
            "FORMULA": "A*logical_and(A>=15,A<=30)",
            "OUTPUT": "TEMPORARY_OUTPUT",
        }

        slope_black_diamond = processing.run(
            "gdal:rastercalculator",
            slope_black_diamond_params,
            context=context,
            feedback=feedback,
        )

        polygonize_params_black_diamond = {
            "INPUT": slope_black_diamond["OUTPUT"],
            "BAND": 1,
            "FIELD": "DN",
            "EIGHT_CONNECTEDNESS": False,
            "EXTRA": "",
            "OUTPUT": parameters[self.OUTPUT_BLACK_DIAMOND],
        }

        results_polygonize_black_diamond = processing.run(
            "gdal:polygonize",
            polygonize_params_black_diamond,
            context=context,
            feedback=feedback,
        )

        if parameters[self.DATABASE]:
            postgis_black_diamond_polygons = {
                "INPUT": results_polygonize_black_diamond["OUTPUT"],
                "DATABASE": parameters[self.DATABASE],
                "SCHEMA": parameters[self.SCHEMA],
                "TABLENAME": "Black Diamond Polygons",
                "PRIMARY_KEY": "",
                "GEOMETRY_COLUMN": "geom",
                "ENCODING": "UTF-8",
                "OVERWRITE": True,
                "CREATEINDEX": True,
                "LOWERCASE_NAMES": True,
                "DROP_STRING_LENGTH": False,
                "FORCE_SINGLEPART": False,
            }

            processing.run(
                "native:importintopostgis",
                postgis_black_diamond_polygons,
                context=context,
                feedback=feedback,
            )

        return {
            "HILLSHADE": results_hillshade["OUTPUT"],
            "ASPECT": results_aspect["OUTPUT"],
            "RELIEF": results_relief["OUTPUT"],
            "RUGGEDNESS": results_ruggedness["OUTPUT"],
            "SLOPE": results_slope["OUTPUT"],
        }
