from src.geometry.survey import load_survey_csv


file_path = "data/survey/modern_survey_001.csv"

df = load_survey_csv(file_path)

print(df)
