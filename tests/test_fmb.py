from src.geometry.fmb import load_fmb_csv


file_path = "data/fmb/fmb_parcel_001.csv"

points = load_fmb_csv(file_path)

print("FMB points:")

for point_id, point in points.items():
    print(point_id, "→", point)
