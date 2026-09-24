from src.geometry.survey import load_survey_csv


file_path = "data/survey/modern_survey_001.csv"

points = load_survey_csv(file_path)

print("Modern survey points:")

for point_id, point in points.items():

    print(
        point_id,
        "→",
        point
    )
