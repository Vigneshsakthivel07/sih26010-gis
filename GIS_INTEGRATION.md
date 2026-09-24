# GIS Validation Integration

## Purpose

The GIS module compares historical FMB parcel geometry with modern
survey coordinates and determines whether the parcel is spatially
consistent.

## Main Function

```python
from src.validation.validator import validate_parcel_from_files

result = validate_parcel_from_files(
    fmb_file,
    survey_file,
    control_ids=["A", "C", "G"],
    tolerance=1.0,
    minimum_overlap=90.0
)

Input
FMB file

CSV format:

point_id,x,y
A,0,0
B,50,0
C,100,0
D,100,40
Modern survey file

CSV format:

point_id,latitude,longitude
A,11.000000,77.000000
B,11.000000,77.000450
C,11.000000,77.000900
D,10.999640,77.000900
Output

The function returns a dictionary containing:

status
maximum_deviation
average_deviation
overlap_percentage
points_outside
deviations
point_results
transformed_fmb
modern_points
Status
VERIFIED

The parcel satisfies the configured spatial validation checks.

MISMATCH

One or more validation checks failed.

A mismatch should be flagged for surveyor/domain review or resurvey.
It does not by itself establish a legal ownership decision.

Important

The tolerance and overlap thresholds are configurable prototype
parameters and are not universal legal survey standards.