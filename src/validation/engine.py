def validate_parcel(
    max_deviation,
    overlap_percentage,
    points_outside,
    tolerance,
    minimum_overlap
):

    deviation_ok = max_deviation <= tolerance

    overlap_ok = (
        overlap_percentage >= minimum_overlap
    )

    points_ok = points_outside == 0

    if deviation_ok and overlap_ok and points_ok:

        status = "VERIFIED"

    else:

        status = "MISMATCH"

    return {
        "status": status,
        "deviation_ok": deviation_ok,
        "overlap_ok": overlap_ok,
        "points_ok": points_ok
    }
