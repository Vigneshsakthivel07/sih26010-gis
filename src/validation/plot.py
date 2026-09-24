import matplotlib.pyplot as plt


def plot_parcel_comparison(
    transformed_fmb,
    modern_points,
    deviations,
    output_file="data/results/parcel_comparison.png"
):
    """
    Plot historical FMB and modern survey
    boundaries with deviation lines.
    """

    # ------------------------------------------
    # Historical FMB
    # ------------------------------------------

    fmb_points = list(transformed_fmb.values())

    fmb_x = [p[0] for p in fmb_points]
    fmb_y = [p[1] for p in fmb_points]

    fmb_x.append(fmb_x[0])
    fmb_y.append(fmb_y[0])

    # ------------------------------------------
    # Modern survey
    # ------------------------------------------

    modern_points_list = list(modern_points.values())

    modern_x = [p[0] for p in modern_points_list]
    modern_y = [p[1] for p in modern_points_list]

    modern_x.append(modern_x[0])
    modern_y.append(modern_y[0])

    # ------------------------------------------
    # Create figure
    # ------------------------------------------

    plt.figure(figsize=(10, 8))

    # Historical boundary
    plt.plot(
        fmb_x,
        fmb_y,
        marker="o",
        label="Historical FMB"
    )

    # Modern boundary
    plt.plot(
        modern_x,
        modern_y,
        marker="o",
        label="Modern Survey"
    )

    # ------------------------------------------
    # Label historical points
    # ------------------------------------------

    for point_id, point in transformed_fmb.items():

        plt.annotate(
            point_id,
            (point[0], point[1]),
            xytext=(5, 5),
            textcoords="offset points"
        )

    # ------------------------------------------
    # Draw deviation lines
    # ------------------------------------------

    for point_id, deviation in deviations.items():

        if deviation > 1.0:

            old_point = transformed_fmb[point_id]
            new_point = modern_points[point_id]

            # Draw line between old and new location
            plt.plot(
                [old_point[0], new_point[0]],
                [old_point[1], new_point[1]],
                linestyle="--"
            )

            # Label deviation
            middle_x = (
                old_point[0] + new_point[0]
            ) / 2

            middle_y = (
                old_point[1] + new_point[1]
            ) / 2

            plt.annotate(
                f"{point_id}: {deviation:.2f} m",
                (middle_x, middle_y),
                xytext=(5, 5),
                textcoords="offset points"
            )

    # ------------------------------------------
    # Formatting
    # ------------------------------------------

    plt.xlabel("Projected X (metres)")
    plt.ylabel("Projected Y (metres)")

    plt.title(
        "Historical FMB vs Modern Survey"
    )

    plt.legend()

    plt.axis("equal")

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=200
    )

    plt.close()

    return output_file
