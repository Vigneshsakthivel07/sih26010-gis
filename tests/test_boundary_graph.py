from src.ingestion.map_lines import detect_lines
from src.ingestion.boundary_graph import (
    build_boundary_candidates,
    summarize_graph,
)


IMAGE = "data/fmb/processed/fmb_map.png"


def test_boundary_graph_with_real_fmb():
    # ---------------------------------------------------------
    # STEP 1: Detect existing Hough lines
    # ---------------------------------------------------------
    lines = detect_lines(IMAGE)

    # ---------------------------------------------------------
    # STEP 2: Build boundary graph candidates
    # ---------------------------------------------------------
    graph = build_boundary_candidates(lines)

    summary = summarize_graph(graph)

    # ---------------------------------------------------------
    # STAGE 1 SUMMARY
    # ---------------------------------------------------------
    print()
    print("========== STAGE 1 ==========")

    print("Map lines:", len(lines))
    print("Merged lines:", summary["input_lines"])
    print("Raw intersections:", summary["raw_intersections"])
    print("Clustered vertices:", summary["vertices"])

    # ---------------------------------------------------------
    # STEP 3: Print merged boundary lines
    # ---------------------------------------------------------
    print()
    print("--- MERGED LINES ---")

    for line in graph["lines"]:
        print(
            f"{line.id}: "
            f"({line.x1:.1f}, {line.y1:.1f}) -> "
            f"({line.x2:.1f}, {line.y2:.1f}) "
            f"length={line.length_px:.1f} "
            f"angle={line.angle:.1f}"
        )

    # ---------------------------------------------------------
    # STEP 4: Print raw intersections
    # ---------------------------------------------------------
    print()
    print("--- RAW INTERSECTIONS ---")

    for index, intersection in enumerate(
        graph["intersections"],
        start=1,
    ):
        print(
            f"I{index}: "
            f"({intersection['x']:.1f}, "
            f"{intersection['y']:.1f}) "
            f"between "
            f"{intersection['line_a']} and "
            f"{intersection['line_b']}"
        )

    # ---------------------------------------------------------
    # STEP 5: Print clustered vertices
    # ---------------------------------------------------------
    print()
    print("--- CLUSTERED VERTICES ---")

    for vertex in graph["vertices"]:
       print(
          f"{vertex.id}: "
          f"({vertex.x:.1f}, {vertex.y:.1f}) "
          f"support={vertex.support} "
          f"lines={vertex.connected_lines}"
       )

    # ---------------------------------------------------------
    # STEP 6: Basic validation
    # ---------------------------------------------------------
    assert len(lines) > 0
    assert len(graph["lines"]) > 0
    assert len(graph["intersections"]) > 0
    assert len(graph["vertices"]) > 0

    print()
    print("==============================")
