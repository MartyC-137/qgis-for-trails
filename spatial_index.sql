/* Spatial Index for Contours */
-- 10m
CREATE INDEX ten_m_contours_sml_index
ON seven_mile_lake."10m_contour_gaussian_seven_mile_lake"
USING gist (geom);

VACUUM ANALYZE seven_mile_lake."10m_contour_gaussian_seven_mile_lake";

-- 5m
CREATE INDEX five_m_contours_sml_index
ON seven_mile_lake."5m_contour_gaussian_seven_mile_lake"
USING gist (geom);

VACUUM ANALYZE seven_mile_lake."5m_contour_gaussian_seven_mile_lake";

-- 2m
CREATE INDEX two_m_contours_sml_index
ON seven_mile_lake."2m_contour_gaussian_seven_mile_lake"
USING gist (geom);

VACUUM ANALYZE seven_mile_lake."2m_contour_gaussian_seven_mile_lake";