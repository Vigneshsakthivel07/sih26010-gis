from src.geometry.polygon import create_polygon


points = [
    (0, 0),
    (100, 0),
    (100, 80),
    (0, 80)
]

polygon = create_polygon(points)

print("Area:", polygon.area)
print("Perimeter:", polygon.length)
