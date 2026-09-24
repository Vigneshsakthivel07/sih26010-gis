from src.validation.deviation import (
    calculate_point_deviations,
    calculate_statistics
)


# Historical FMB points
historical_points = {
    "A": (0, 0),
    "B": (100, 0),
    "C": (100, 80),
    "D": (0, 80)
}


# Modern survey points
# Slightly shifted from the historical points
modern_points = {
    "A": (0.3, 0.2),
    "B": (100.8, 0.4),
    "C": (100.5, 79.7),
    "D": (0.2, 80.1)
}


# Calculate deviation for each point
deviations = calculate_point_deviations(
    historical_points,
    modern_points
)


print("Point deviations:")

for point_id, value in deviations.items():
    print(
        point_id,
        "→",
        round(value, 3),
        "metres"
    )


# Calculate statistics
statistics = calculate_statistics(deviations)


print("\nStatistics:")

print(
    "Minimum:",
    round(statistics["minimum"], 3),
    "metres"
)

print(
    "Maximum:",
    round(statistics["maximum"], 3),
    "metres"
)

print(
    "Average:",
    round(statistics["average"], 3),
    "metres"
)
