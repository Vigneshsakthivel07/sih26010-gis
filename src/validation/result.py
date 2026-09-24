import json


def save_validation_result(result, output_file="data/results/validation_result.json"):
    """
    Save important parcel validation results as JSON.
    """

    output = {
        "status": result["status"],
        "maximum_deviation": round(result["maximum_deviation"], 3),
        "average_deviation": round(result["average_deviation"], 3),
        "overlap_percentage": round(result["overlap_percentage"], 2),
        "points_outside": result["points_outside"],

        "deviation_ok": result["deviation_ok"],
        "overlap_ok": result["overlap_ok"],
        "points_ok": result["points_ok"],

        "deviations": {
            point_id: round(value, 3)
            for point_id, value in result["deviations"].items()
        },

        "point_results": result["point_results"]
    }

    with open(output_file, "w") as file:
        json.dump(output, file, indent=4)

    return output_file