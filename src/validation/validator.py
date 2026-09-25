from src.geometry.fmb import load_fmb_csv, load_digitized_fmb_csv
from src.geometry.survey import load_survey_csv
from src.geometry.polygon import polygon_from_point_dict, create_point

from src.transform.affine import calculate_affine_transform
from src.transform.transform_points import transform_points

from src.validation.parcel_compare import compare_parcel
from src.validation.point_check import check_points_inside
from src.validation.overlap import calculate_overlap
from src.validation.engine import validate_parcel


def validate_parcel_from_files(
    fmb_file,
    survey_file,
    control_ids,
    tolerance=1.0,
    minimum_overlap=90.0,
    digitized_fmb=False
):


    """
    Complete GIS validation pipeline.

    Parameters
    ----------
    fmb_file : str
        Path to historical FMB CSV.

    survey_file : str
        Path to modern survey CSV.

    control_ids : list
        Point IDs used as stable control points.

    tolerance : float
        Maximum allowed boundary deviation in metres.

    minimum_overlap : float
        Minimum acceptable polygon overlap percentage.

    Returns
    -------
    dict
        Complete parcel validation result.
    """

    # ------------------------------------------
    # 1. Load historical FMB
    # ------------------------------------------
    if digitized_fmb:
         fmb_points = load_digitized_fmb_csv(fmb_file)
    else:
   	 fmb_points = load_fmb_csv(fmb_file)

    # ------------------------------------------
    # 2. Load modern survey
    # ------------------------------------------

    modern_points = load_survey_csv(survey_file)

    # ------------------------------------------
    # 3. Get transformation control points
    # ------------------------------------------

    source_control_points = [
        fmb_points[point_id]
        for point_id in control_ids
    ]

    target_control_points = [
        modern_points[point_id]
        for point_id in control_ids
    ]

    # ------------------------------------------
    # 4. Calculate affine transformation
    # ------------------------------------------

    transform_params = calculate_affine_transform(
        source_control_points,
        target_control_points
    )

    # ------------------------------------------
    # 5. Transform historical FMB
    # ------------------------------------------

    transformed_fmb = transform_points(
        fmb_points,
        transform_params
    )

    # ------------------------------------------
    # 6. Calculate boundary deviations
    # ------------------------------------------

    deviations = compare_parcel(
        fmb_points,
        modern_points,
        transform_params
    )

    # ------------------------------------------
    # 7. Create transformed FMB polygon
    # ------------------------------------------

    fmb_polygon = polygon_from_point_dict(
        transformed_fmb
    )

    # ------------------------------------------
    # 8. Create modern survey polygon
    # ------------------------------------------

    modern_polygon = polygon_from_point_dict(
        modern_points
    )

    # ------------------------------------------
    # 9. Convert modern points to Shapely points
    # ------------------------------------------

    modern_shapely_points = {}

    for point_id, coordinates in modern_points.items():

        modern_shapely_points[point_id] = create_point(
            coordinates[0],
            coordinates[1]
        )

    # ------------------------------------------
    # 10. Point-in-polygon validation
    # ------------------------------------------

    point_results = check_points_inside(
        fmb_polygon,
        modern_shapely_points
    )

    points_outside = sum(
        1
        for inside in point_results.values()
        if not inside
    )

    # ------------------------------------------
    # 11. Polygon overlap
    # ------------------------------------------

    overlap_percentage = calculate_overlap(
        fmb_polygon,
        modern_polygon
    )

    # ------------------------------------------
    # 12. Final validation
    # ------------------------------------------

    validation_result = validate_parcel(
        deviations=deviations,
        overlap_percentage=overlap_percentage,
        points_outside=points_outside,
        tolerance=tolerance,
        minimum_overlap=minimum_overlap
    )

    # ------------------------------------------
    # 13. Return complete result
    # ------------------------------------------

    return {
        "status": validation_result["status"],
        "deviations": deviations,
        "point_results": point_results,
        "points_outside": points_outside,
        "overlap_percentage": overlap_percentage,
        "maximum_deviation": validation_result[
            "maximum_deviation"
        ],
        "average_deviation": validation_result[
            "average_deviation"
        ],
        "deviation_ok": validation_result[
            "deviation_ok"
        ],
        "overlap_ok": validation_result[
            "overlap_ok"
        ],
        "points_ok": validation_result[
            "points_ok"
        ],
        "transformed_fmb": transformed_fmb,
        "modern_points": modern_points,
    }
