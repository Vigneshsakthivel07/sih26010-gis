from dataclasses import dataclass, field
from typing import Optional
import math


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class BoundaryLine:
    """
    Normalized representation of one detected cadastral line.
    """

    id: str
    x1: float
    y1: float
    x2: float
    y2: float
    source: str = "hough"

    @property
    def length_px(self):
        return math.hypot(
            self.x2 - self.x1,
            self.y2 - self.y1
        )

    @property
    def angle(self):
        return (
            math.degrees(
                math.atan2(
                    self.y2 - self.y1,
                    self.x2 - self.x1
                )
            )
            % 180
        )

    @property
    def midpoint(self):
        return (
            (self.x1 + self.x2) / 2,
            (self.y1 + self.y2) / 2
        )


@dataclass
class BoundaryVertex:
    id: str
    x: float
    y: float
    connected_edges: list = field(default_factory=list)
    connected_lines: list = field(default_factory=list)
    support: int = 0


@dataclass
class BoundaryEdge:
    """
    Edge between two boundary vertices.

    line_ids keeps the merged boundary line that supports
    this edge.
    """

    id: str
    start_vertex: Optional[str]
    end_vertex: Optional[str]
    line_ids: list = field(default_factory=list)

    length_px: float = 0.0
    angle: float = 0.0

    measurement_candidates: list = field(default_factory=list)

    selected_measurement: Optional[str] = None

    status: str = "CANDIDATE"


@dataclass
class MeasurementCandidate:
    """
    OCR measurement candidate.

    This is deliberately NOT treated as a final measurement.
    """

    id: str
    value: float
    x: float
    y: float
    confidence: float
    orientation: str

    candidate_edges: list = field(default_factory=list)

    selected_edge: Optional[str] = None

    status: str = "CANDIDATE"


# ============================================================
# GEOMETRY HELPERS
# ============================================================

def angle_difference(a, b):
    """
    Difference between two unoriented line angles.

    Example:
        5° and 175° are considered almost parallel.
    """

    diff = abs(a - b) % 180

    return min(
        diff,
        180 - diff
    )


def point_segment_distance(px, py, line):
    """
    Distance from a point to a finite line segment.
    """

    x1 = line.x1
    y1 = line.y1
    x2 = line.x2
    y2 = line.y2

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        return math.hypot(
            px - x1,
            py - y1
        )

    t = (
        (px - x1) * dx
        + (py - y1) * dy
    ) / (
        dx * dx
        + dy * dy
    )

    t = max(
        0.0,
        min(1.0, t)
    )

    qx = x1 + t * dx
    qy = y1 + t * dy

    return math.hypot(
        px - qx,
        py - qy
    )

def line_intersection(a, b):
    """
    Intersection of two infinite lines.

    Returns:
        (x, y)

    or:
        None for parallel lines.
    """

    x1, y1 = a.x1, a.y1
    x2, y2 = a.x2, a.y2

    x3, y3 = b.x1, b.y1
    x4, y4 = b.x2, b.y2

    denominator = (
        (x1 - x2) * (y3 - y4)
        - (y1 - y2) * (x3 - x4)
    )

    if abs(denominator) < 1e-9:
        return None

    px = (
        (x1 * y2 - y1 * x2) * (x3 - x4)
        - (x1 - x2) * (x3 * y4 - y3 * x4)
    ) / denominator

    py = (
        (x1 * y2 - y1 * x2) * (y3 - y4)
        - (y1 - y2) * (x3 * y4 - y3 * x4)
    ) / denominator

    return px, py

# ============================================================
# INPUT NORMALIZATION
# ============================================================

def normalize_lines(lines):
    """
    Convert the existing map_lines.py dictionaries into
    BoundaryLine objects.

    Existing input format:

        {
            "x1": ...,
            "y1": ...,
            "x2": ...,
            "y2": ...,
            "length": ...,
            "angle": ...
        }

    We intentionally preserve compatibility with it.
    """

    normalized = []

    for index, line in enumerate(lines):

        if isinstance(line, BoundaryLine):
            normalized.append(line)
            continue

        required = (
            "x1",
            "y1",
            "x2",
            "y2"
        )

        if not all(
            key in line
            for key in required
        ):
            continue

        normalized.append(
            BoundaryLine(
                id=f"L{index + 1}",
                x1=float(line["x1"]),
                y1=float(line["y1"]),
                x2=float(line["x2"]),
                y2=float(line["y2"]),
                source="hough"
            )
        )

    return normalized


# ============================================================
# LINE MERGING
# ============================================================

def _point_to_infinite_line_distance(px, py, line):
    """
    Perpendicular distance from point to infinite line.
    """

    dx = line.x2 - line.x1
    dy = line.y2 - line.y1

    length = math.hypot(dx, dy)

    if length == 0:
        return float("inf")

    return abs(
        dy * px
        - dx * py
        + line.x2 * line.y1
        - line.y2 * line.x1
    ) / length


def _project_interval(line, axis_x, axis_y):
    """
    Project line endpoints onto a unit axis.
    """

    p1 = (
        line.x1 * axis_x
        + line.y1 * axis_y
    )

    p2 = (
        line.x2 * axis_x
        + line.y2 * axis_y
    )

    return (
        min(p1, p2),
        max(p1, p2)
    )


def _interval_overlap(a, b):
    return max(
        0.0,
        min(a[1], b[1])
        - max(a[0], b[0])
    )


def are_mergeable(
    a,
    b,
    angle_tolerance=5.0,
    distance_tolerance=12.0,
    gap_tolerance=40.0
):
    """
    Decide whether two Hough fragments probably belong
    to the same cadastral boundary.

    This is intentionally conservative.
    """

    if angle_difference(
        a.angle,
        b.angle
    ) > angle_tolerance:
        return False

    length = a.length_px

    if length == 0:
        return False

    axis_x = (
        a.x2 - a.x1
    ) / length

    axis_y = (
        a.y2 - a.y1
    ) / length

    distance_b1 = _point_to_infinite_line_distance(
        b.x1,
        b.y1,
        a
    )

    distance_b2 = _point_to_infinite_line_distance(
        b.x2,
        b.y2,
        a
    )

    if max(
        distance_b1,
        distance_b2
    ) > distance_tolerance:
        return False

    interval_a = _project_interval(
        a,
        axis_x,
        axis_y
    )

    interval_b = _project_interval(
        b,
        axis_x,
        axis_y
    )

    overlap = _interval_overlap(
        interval_a,
        interval_b
    )

    if overlap > 0:
        return True

    gap = max(
        interval_a[0],
        interval_b[0]
    ) - min(
        interval_a[1],
        interval_b[1]
    )

    return gap <= gap_tolerance


def merge_lines(
    lines,
    angle_tolerance=5.0,
    distance_tolerance=12.0,
    gap_tolerance=40.0,
):
    """
    Merge collinear/near-collinear Hough fragments into longer
    continuous boundary segments.

    Unlike the previous implementation, this does not simply
    keep the longest fragment. It combines the projected extent
    of all compatible fragments.
    """

    lines = normalize_lines(lines)

    if not lines:
        return []

    groups = []

    for line in lines:

        assigned_group = None

        for group in groups:

            representative = group[0]

            if are_mergeable(
                representative,
                line,
                angle_tolerance,
                distance_tolerance,
                gap_tolerance,
            ):
                assigned_group = group
                break

        if assigned_group is not None:
            assigned_group.append(line)

        else:
            groups.append([line])

    merged = []

    for index, group in enumerate(groups):

        reference = max(
            group,
            key=lambda item: item.length_px
        )

        length = reference.length_px

        if length == 0:
            continue

        ux = (
            reference.x2 - reference.x1
        ) / length

        uy = (
            reference.y2 - reference.y1
        ) / length

        projected_points = []

        for line in group:

            for x, y in [
                (line.x1, line.y1),
                (line.x2, line.y2),
            ]:

                projection = (
                    (x - reference.x1) * ux
                    + (y - reference.y1) * uy
                )

                projected_points.append(
                    projection
                )

        min_projection = min(
            projected_points
        )

        max_projection = max(
            projected_points
        )

        x1 = (
            reference.x1
            + min_projection * ux
        )

        y1 = (
            reference.y1
            + min_projection * uy
        )

        x2 = (
            reference.x1
            + max_projection * ux
        )

        y2 = (
            reference.y1
            + max_projection * uy
        )

        merged.append(
            BoundaryLine(
                id=f"M{index + 1}",
                x1=round(x1, 2),
                y1=round(y1, 2),
                x2=round(x2, 2),
                y2=round(y2, 2),
                source="merged",
            )
        )

    return merged


# ============================================================
# INTERSECTION DETECTION
# ============================================================

def find_intersections(
    lines,
    angle_threshold=12.0,
    max_extension=80.0
):
    """
    Find candidate vertices from line intersections.

    Compared with the old extractor, max_extension is larger
    because Hough fragments can stop before the actual corner.

    We still keep this bounded to avoid arbitrary intersections.
    """

    lines = normalize_lines(lines)

    candidates = []

    for i in range(len(lines)):

        for j in range(
            i + 1,
            len(lines)
        ):

            a = lines[i]
            b = lines[j]

            if angle_difference(
                a.angle,
                b.angle
            ) < angle_threshold:
                continue

            point = line_intersection(
                a,
                b
            )

            if point is None:
                continue

            px, py = point

            da = point_segment_distance(
                px,
                py,
                a
            )

            db = point_segment_distance(
                px,
                py,
                b
            )

            if (
                da > max_extension
                or db > max_extension
            ):
                continue

            candidates.append(
                {
                    "x": px,
                    "y": py,
                    "line_a": a.id,
                    "line_b": b.id
                }
            )

    return candidates


# ============================================================
# POINT CLUSTERING
# ============================================================

def cluster_intersections(
    intersections,
    radius=18.0
):
    """
    Merge multiple nearly identical intersections into
    one graph vertex.
    """

    clusters = []

    for item in intersections:

        x = item["x"]
        y = item["y"]

        assigned = False

        for cluster in clusters:

            distance = math.hypot(
                x - cluster["x"],
                y - cluster["y"]
            )

            if distance <= radius:

                cluster["points"].append(item)

                count = len(
                    cluster["points"]
                )

                cluster["x"] = sum(
                    p["x"]
                    for p in cluster["points"]
                ) / count

                cluster["y"] = sum(
                    p["y"]
                    for p in cluster["points"]
                ) / count

                cluster["support"] = count

                assigned = True
                break

        if not assigned:

            clusters.append(
                {
                    "x": x,
                    "y": y,
                    "support": 1,
                    "points": [item]
                }
            )

    vertices = []

    for index, cluster in enumerate(
        clusters
    ):

        vertices.append(
            BoundaryVertex(
                id=f"V{index + 1}",
                x=round(cluster["x"], 2),
                y=round(cluster["y"], 2)
            )
        )

    return vertices


# ============================================================
# BOUNDARY EDGE CONSTRUCTION
# ============================================================

def build_boundary_edges(lines, vertices):
    """
    Connect clustered vertices that lie on the same
    merged boundary line.

    Each edge represents one continuous boundary segment
    between two detected vertices.
    """

    edges = []

    for line in lines:

        line_vertices = []

        for vertex in vertices:

            distance = point_segment_distance(
                vertex.x,
                vertex.y,
                line
            )

            if distance <= 20.0:
                line_vertices.append(vertex)

        if len(line_vertices) < 2:
            continue

        length = line.length_px

        if length == 0:
            continue

        ux = (
            line.x2 - line.x1
        ) / length

        uy = (
            line.y2 - line.y1
        ) / length

        projected_vertices = []

        for vertex in line_vertices:

            projection = (
                (vertex.x - line.x1) * ux
                + (vertex.y - line.y1) * uy
            )

            projected_vertices.append(
                (projection, vertex)
            )

        projected_vertices.sort(
            key=lambda item: item[0]
        )

        for index in range(
            len(projected_vertices) - 1
        ):

            start_vertex = (
                projected_vertices[index][1]
            )

            end_vertex = (
                projected_vertices[index + 1][1]
            )

            if start_vertex.id == end_vertex.id:
                continue

            edge_length = math.hypot(
                end_vertex.x - start_vertex.x,
                end_vertex.y - start_vertex.y
            )

            edge = BoundaryEdge(
                id=f"E{len(edges) + 1}",
                start_vertex=start_vertex.id,
                end_vertex=end_vertex.id,
                line_ids=[line.id],
                length_px=edge_length,
                angle=line.angle,
            )

            edges.append(edge)

            start_vertex.connected_edges.append(
                edge.id
            )

            end_vertex.connected_edges.append(
                edge.id
            )

    return edges


# ============================================================
# PUBLIC PIPELINE
# ============================================================

def build_boundary_candidates(lines, merge=True):

    normalized = normalize_lines(lines)

    if merge:
        boundary_lines = merge_lines(
            normalized
        )

    else:
        boundary_lines = normalized

    intersections = find_intersections(
        boundary_lines
    )

    vertices = cluster_intersections(
        intersections
    )

    # ---------------------------------------------------------
    # Connect each intersection to its two participating lines
    # ---------------------------------------------------------

    vertex_line_map = {}

    for intersection in intersections:

        point = (
            intersection["x"],
            intersection["y"],
        )

        line_ids = [
            intersection["line_a"],
            intersection["line_b"],
        ]

        nearest_vertex = None
        nearest_distance = float("inf")

        for vertex in vertices:

            distance = math.hypot(
                point[0] - vertex.x,
                point[1] - vertex.y,
            )

            if distance < nearest_distance:

                nearest_distance = distance
                nearest_vertex = vertex

        if nearest_vertex is None:
            continue

        if nearest_vertex.id not in vertex_line_map:

            vertex_line_map[
                nearest_vertex.id
            ] = set()

        vertex_line_map[
            nearest_vertex.id
        ].update(line_ids)

    # ---------------------------------------------------------
    # Store line connectivity inside each vertex
    # ---------------------------------------------------------

    for vertex in vertices:

        connected = sorted(
            vertex_line_map.get(
                vertex.id,
                set()
            )
        )

        vertex.connected_lines = connected

        vertex.support = len(
            connected
        )

    # ---------------------------------------------------------
    # Build edges from vertices and merged lines
    # ---------------------------------------------------------

    edges = build_boundary_edges(
        boundary_lines,
        vertices
    )

    return {
        "lines": boundary_lines,
        "intersections": intersections,
        "vertices": vertices,
        "edges": edges,
    }


# ============================================================
# SIMPLE DEBUG OUTPUT
# ============================================================

def summarize_graph(graph):
    """
    Human-readable diagnostic summary.
    """

    return {
        "input_lines": len(
            graph.get("lines", [])
        ),

        "raw_intersections": len(
            graph.get("intersections", [])
        ),

        "vertices": len(
            graph.get("vertices", [])
        ),

        "edges": len(
            graph.get("edges", [])
        ),
    }
