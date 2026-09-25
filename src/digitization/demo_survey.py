import csv

from src.digitization.pixel_to_local import (
    load_points,
    pixel_to_local
)


def create_demo_survey(
    fmb_csv,
    output_csv,
    shift_x=2.0,
    shift_y=3.0
):
    """
    Create a synthetic modern survey dataset
    from the digitized FMB polygon.

    This is TEST DATA only.
    """

    pixel_points = load_points(fmb_csv)

    local_points = pixel_to_local(
        pixel_points,
        scale_denominator=848,
        dpi=300
    )

    with open(
        output_csv,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "point_id",
                "x",
                "y"
            ]
        )

        for point_id, (x, y) in local_points.items():

            modern_x = x + shift_x
            modern_y = y + shift_y

            writer.writerow(
                [
                    point_id,
                    round(modern_x, 3),
                    round(modern_y, 3)
                ]
            )


if __name__ == "__main__":

    create_demo_survey(
        "data/fmb/fmb_selected_points.csv",
        "data/survey/modern_survey_demo.csv"
    )

    print(
        "Demo modern survey created:"
    )

    print(
        "data/survey/modern_survey_demo.csv"
    )
