from src.validation.validator import validate_parcel_from_files


def validate_land_parcel(
    fmb_file,
    survey_file,
    control_ids=None,
    tolerance=1.0,
    minimum_overlap=90.0,
    digitized_fmb=False
):

    """
    Public interface for the GIS validation module.

    The application only needs to call this function.
    """

    if control_ids is None:
        control_ids = ["A", "C", "G"]

    result = validate_parcel_from_files(
        fmb_file=fmb_file,
        survey_file=survey_file,
        control_ids=control_ids,
        tolerance=tolerance,
        minimum_overlap=minimum_overlap,
        digitized_fmb=digitized_fmb
    )

    return {
        "status": result["status"],
        "maximum_deviation": result["maximum_deviation"],
        "average_deviation": result["average_deviation"],
        "overlap_percentage": result["overlap_percentage"],
        "points_outside": result["points_outside"],
        "deviations": result["deviations"],
        "point_results": result["point_results"],
        "transformed_fmb": result["transformed_fmb"],
        "modern_points": result["modern_points"]
    }
