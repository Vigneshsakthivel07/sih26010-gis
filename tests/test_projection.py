from src.transform.projection import gps_to_local


lat = 11.000000
lon = 77.000000

x, y = gps_to_local(lat, lon)

print("X:", x)
print("Y:", y)
