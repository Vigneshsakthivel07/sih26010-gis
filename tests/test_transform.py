from src.transform.affine import (
    calculate_affine_transform,
    transform_point
)


source = [
    (0, 0),
    (100, 0),
    (100, 80),
    (0, 80)
]

target = [
    (500000, 1200000),
    (500100, 1200000),
    (500100, 1200080),
    (500000, 1200080)
]


params = calculate_affine_transform(
    source,
    target
)


print("Transformation parameters:")
print(params)


for point in source:

    transformed = transform_point(
        point,
        params
    )

    print(
        point,
        "→",
        transformed
    )
