/* QGIS virtual field for calculating total elevation gain of a polyline */
with_variable('elev_gain', 0,
    array_sum(
        array_foreach(
            generate_series(1, num_points($geometry)-1),
            max(0, raster_value('raster_layer', 1, point_n($geometry, @element+1)) - raster_value('raster_layer', 1, point_n($geometry, @element)))
        )
    )
)
