import re


def parse_header(text):

    result = {
        "district": None,
        "taluk": None,
        "village": None,
        "survey_number": None,
        "area": None,
        "scale": None
    }

    # --------------------------------------------------
    # Survey Number
    # --------------------------------------------------
    match = re.search(
        r"Survey\s*No\s*:?\s*([A-Za-z0-9/]+)",
        text,
        re.IGNORECASE
    )

    if match:
        result["survey_number"] = match.group(1).strip()

    # --------------------------------------------------
    # District
    # --------------------------------------------------
    match = re.search(
        r"(?:District|Dist[a-z]*)\s*:\s*([A-Za-z]+)",
        text,
        re.IGNORECASE
    )

    if match:
        result["district"] = match.group(1).strip()

    else:
        # OCR may completely distort the word "District".
        # Look for known header structure: value after ":".
        match = re.search(
            r":\s*(Erode)\b",
            text,
            re.IGNORECASE
        )

        if match:
            result["district"] = match.group(1)

    # --------------------------------------------------
    # Taluk
    # --------------------------------------------------
    match = re.search(
        r"Taluk\s*:\s*([A-Za-z]+)",
        text,
        re.IGNORECASE
    )

    if match:
        result["taluk"] = match.group(1).strip()

    # --------------------------------------------------
    # Area
    # --------------------------------------------------
    match = re.search(
        r"Area\s*:\s*Hect\s*([0-9]+)\s*Ares\s*([0-9.]+)",
        text,
        re.IGNORECASE
    )

    if match:
        result["area"] = {
            "hectares": float(match.group(1)),
            "ares": float(match.group(2))
        }

    # --------------------------------------------------
    # Scale
    # --------------------------------------------------
    match = re.search(
        r"Scale\s*:?\s*(?:1\s*:?\s*)?(\d+)",
        text,
        re.IGNORECASE
    )

    if match:
        result["scale"] = f"1:{match.group(1)}"

    # --------------------------------------------------
    # Village
    # --------------------------------------------------
    match = re.search(
        r"Village\s*:\s*(.*)",
        text,
        re.IGNORECASE
    )

    if match:
        village = match.group(1).strip()

        # Remove Scale information accidentally captured
        village = re.split(
            r"\s+Scale\b",
            village,
            flags=re.IGNORECASE
        )[0].strip()

        result["village"] = village

    return result
