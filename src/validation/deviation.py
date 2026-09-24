from .distance import distance


def calculate_point_deviations(
    historical_points,
    modern_points
):

    deviations = {}

    for point_id in historical_points:

        old_point = historical_points[point_id]
        new_point = modern_points[point_id]

        deviations[point_id] = distance(
            old_point,
            new_point
        )

    return deviations


def calculate_statistics(deviations):

    values = list(deviations.values())

    return {
        "minimum": min(values),
        "maximum": max(values),
        "average": sum(values) / len(values)
    }
