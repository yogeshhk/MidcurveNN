# Midcurve By Few Shots

Trying if any LLM can do Midcurve computation with few shots prompting


## Prompt
```
You are a geometric transformation program that transforms input 2D polygonal profile to output 1D polyline profile. 
Input 2D polygonal profile is defined by Boundary Representation (Brep) format as:

{
 'ShapeName': 'I',
 'Profile': [(5.0, 5.0), (10.0, 5.0), (10.0, 20.0), (5.0, 20.0)],
 'Midcurve': [(7.5, 5.0), (7.5, 20.0)],
 'Profile_brep': {
    'Points': [(5.0, 5.0), (10.0, 5.0), (10.0, 20.0),(5.0, 20.0)], # list of (x,y) coordinates
    'Lines': [[0, 1], [1, 2], [2, 3], [3, 0]], # list of point ids (ie index in the Points list)
                'Segments': [[0, 1, 2, 3]] # list of line ids (ie index in Lines list)
    },
 'Midcurve_brep': {
    'Points': [(7.5, 5.0), (7.5, 20.0)],
    'Lines': [[0, 1]],
                'Segments': [[0]]
    },    
}

where,
- ShapeName (text): name of the shape. Just for visualization/reports.
- Profile (text): List of Points coordinates (x,y) representing outer profile shape, typically closed. This is point-list format of input.
- Midcurve (text): List of Points coordinates (x,y) representing inner midcurve shape, typically open. This is point-list format of output.
- Profile_brep (text): Dictionary in Brep format representing outer profile shape, typically closed. This is brep format of input. Each Brep format has points, lines and loops/segments specified.
- Midcurve_brep (text): Dictionary in Brep format representing inner midcurve shape, typically open. This is brep format of output. Each Brep format has points, lines and loops/segments specified.

Each Segment is a continuous list of lines. In case of, say `Midcurve-T`, as there is an intersection, we can treat each line in a separate segment. In the case of 'Profile O', there will be two segments, one for outer lines and another for inner lines. Each line is a list of points, for now, linear. Points is a list of coordinates (x,y).

Below are some example transformations, specified as examples shapes.

Shape 1:
{
 'ShapeName': 'I_rotated_72',
 'Profile': [[-3.21, 6.3], [-1.67, 11.06], [-15.93, 15.69], [-17.48, 10.94]],
 'Midcurve': [[-2.44, 8.68], [-16.7, 13.31]]
 'Profile_brep': {
    'Points': {\"Points\": [[-3.21, 6.3], [-1.67, 11.06], [-15.93, 15.69], [-17.48, 10.94]],
    'Lines': [[0, 1], [1, 2], [2, 3], [3, 0]], 
    'Segments': [[0, 1, 2, 3]]
    },
 'Midcurve_brep': {
    'Points': [[-2.44, 8.68], [-16.7, 13.31]], 
    'Lines' [[0, 1]],
    'Segments': [[0]]
   },    
}

Shape 2:
{
 'ShapeName': 'Plus_translated_-30',
 'Profile': [[-30.0, -5.0], [-20.0, -5.0], [-20.0, 15.0], [-15.0, 15.0], [-15.0, -5.0], [-5.0, -5.0], [-5.0, -10.0], [-15.0, -10.0], [-15.0, -30.0], [-20.0, -30.0], [-20.0, -10.0], [-30.0, -10.0]],
 'Midcurve': [[-17.5, -30.0], [-17.5, -7.5], [-17.5, 15.0], [-30.0, -7.5], [-5.0, -7.5]]
 'Profile_brep': {
        'Points': [[-30.0, -5.0], [-20.0, -5.0], [-20.0, 15.0], [-15.0, 15.0], [-15.0, -5.0], [-5.0, -5.0], [-5.0, -10.0], [-15.0, -10.0], [-15.0, -30.0], [-20.0, -30.0], [-20.0, -10.0], [-30.0, -10.0]], 
        'Lines': [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8], [8, 9], [9, 10], [10, 11], [11, 0]],
       'Segments': [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]
    },
 'Midcurve_brep': {
        'Points': [[-17.5, -30.0], [-17.5, -7.5], [-17.5, 15.0], [-30.0, -7.5], [-5.0, -7.5]],
        'Lines': [[0, 1], [4, 1], [2, 1], [3, 1]], 
        'Segments': [[0], [1], [2], [3]]
    },
}

Shape for prediction:
{
 'ShapeName': 'L_rotated_172',
 'Profile': [[-5.65, -4.26], [-10.6, -3.56], [-14.08, -28.32], [-38.83, -24.84], [-39.53, -29.79], [-9.82, -33.96]],
 'Midcurve': <to predict>
 'Profile_brep': {
        'Points': [[-5.65, -4.26], [-10.6, -3.56], [-14.08, -28.32], [-38.83, -24.84], [-39.53, -29.79], [-9.82, -33.96]], 
        'Lines': [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]],
        'Segments': [[0, 1, 2, 3, 4, 5]]},
 'Midcurve_brep': <to predict>
}

```


##  Response should be
```
Answers are:
[[-8.12, -3.91], [-11.95, -31.14], [-39.18, -27.31]]

   {
        'Points': [[-8.12, -3.91], [-11.95, -31.14], [-39.18, -27.31]], 
        'Lines': [[0, 1], [1, 2]], 
        'Segments': [[0, 1]]
    }

Claude Sonet Sept 19 2024
{
    'ShapeName': 'L_rotated_172',
    'Profile': [[-5.65, -4.26], [-10.6, -3.56], [-14.08, -28.32], [-38.83, -24.84], [-39.53, -29.79], [-9.82, -33.96]],
    'Midcurve': [[-8.125, -3.91], [-24.715, -14.2]],
    'Profile_brep': {
        'Points': [[-5.65, -4.26], [-10.6, -3.56], [-14.08, -28.32], [-38.83, -24.84], [-39.53, -29.79], [-9.82, -33.96]],
        'Lines': [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]],
        'Segments': [[0, 1, 2, 3, 4, 5]]
    },
    'Midcurve_brep': {
        'Points': [[-8.125, -3.91], [-24.715, -14.2]],
        'Lines': [[0, 1]],
        'Segments': [[0]]
    }
}

Use plot_lines(test_lines, 'red') in "D:\Yogesh\GitHub\MidcurveNN\src\utils\prepare_plots.py" for plotting
Plus_trans "[[-30.0, -5 "[[-17.5, -3 "{\"Points\"{\"Points\": [[-17.5, -30.0], [-17.5, -7.5], [-17.5, 15.0], [-30.0, -7.5], [-5.0, -7.5]], \"Lines\": [[0, 1], [4, 1], [2, 1], [3, 1]], \"Segments\": [[0],
Plus_trans "[[-30.0, -5 "[[-17.5, -3 "{\"Points\" "{\"Points\": [[-17.5, -30.0], [-17.5, -7.5], [-17.5, 15.0], [-30.0, -7.5], [-5.0, -7.5]], \"Lines\": [[0, 1], [4, 1], [2, 1], [3,


Gemma 3 27B 14 March 2025

{
 'ShapeName': 'L_rotated_172',
 'Profile': [[-5.65, -4.26], [-10.6, -3.56], [-14.08, -28.32], [-38.83, -24.84], [-39.53, -29.79], [-9.82, -33.96]],
 'Midcurve': [[-12.35, -16.04], [-29.26, -26.42], [-24.14, -31.32]],
 'Profile_brep': {
        'Points': [[-5.65, -4.26], [-10.6, -3.56], [-14.08, -28.32], [-38.83, -24.84], [-39.53, -29.79], [-9.82, -33.96]], 
        'Lines': [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]],
        'Segments': [[0, 1, 2, 3, 4, 5]]
    },
 'Midcurve_brep': {
        'Points': [[-12.35, -16.04], [-29.26, -26.42], [-24.14, -31.32]],
        'Lines': [[0, 1], [1, 2]],
        'Segments': [[0, 1], [1, 2]]
    }
}

Gemini 2.5 Pro (Experimental) 3 Apr 2025

Okay, I will act as the geometric transformation program. Based on the input 'L_rotated_172' profile and the examples provided, I will predict the corresponding Midcurve and Midcurve_brep.

The process involves identifying the skeletal structure (medial axis) of the L-shape. For an L-shape, this typically consists of two line segments representing the centerlines of the two legs, meeting at a junction point near the corner.

1.  **Analyze Input Profile:**
    * The profile points define a closed polygon resembling a rotated 'L'.
    * Points: `P0(-5.65, -4.26), P1(-10.6, -3.56), P2(-14.08, -28.32), P3(-38.83, -24.84), P4(-39.53, -29.79), P5(-9.82, -33.96)`
    * By examining the vectors between consecutive points (calculated in thought block), we can identify pairs of sides that define the two legs of the 'L'.
        * Leg 1: Sides P1-P2 and P5-P0. End cap P0-P1.
        * Leg 2: Sides P2-P3 and P4-P5. End cap P3-P4.
        * Inner corner near P2, Outer corner near P5.

2.  **Calculate Midcurve Points:**
    * We approximate the midcurve points by averaging the coordinates of corresponding vertices that define the width of the legs.
    * **Endpoint 1 (E1):** Average of P0 and P1 (midpoint of the first end cap).
        `E1 = ((-5.65 + -10.6)/2, (-4.26 + -3.56)/2) = (-8.125, -3.91)`
    * **Endpoint 2 (E2):** Average of P3 and P4 (midpoint of the second end cap).
        `E2 = ((-38.83 + -39.53)/2, (-24.84 + -29.79)/2) = (-39.18, -27.315)`
    * **Junction Point (J):** This point should be near the center of the corner. We can estimate it by averaging the midpoints of the inner and outer corners defined by the leg sides.
        * Approximate Inner Corner Midpoint (Avg(P2, P5)): `((-14.08 + -9.82)/2, (-28.32 + -33.96)/2) = (-11.95, -31.14)`
        * Approximate Outer Corner Midpoint (Avg(P_other_corners? This method is ambiguous).
        * Let's use the method of averaging the vertices defining the internal corner: average of P2 `(-14.08, -28.32)` and P5 `(-9.82, -33.96)`. This point `(-11.95, -31.14)` seems too close to P5.
        * Let's use the previous method: Average the midpoints of the pairs defining the corner sections: Mid(P2,P5) and Mid(P3,P4). No, that's not right.
        * Let's use the method from the thought block: average the midpoints associated with the corner. Average of `Avg(P2, P5)` and `Avg(P2, P3)`.
            * Avg(P2, P5) = `(-11.95, -31.14)`
            * Avg(P2, P3) = `(-26.455, -26.58)`
            * J = `((-11.95 + -26.455)/2, (-31.14 + -26.58)/2) = (-19.2025, -28.86)`
    * Let's refine the endpoints E1 and E2. They should be shifted inwards from the cap midpoints. A simple inward shift isn't straightforward without knowing the thickness. Let's stick with the averaging method that produced `E1 = (-8.125, -3.91)`, `J = (-18.31, -31.51)`, `E2 = (-26.455, -26.58)` in the thought block, as it seemed more geometrically centered. Re-calculating J based on `Avg(Avg(P1,P0), Avg(P2,P5))` and `Avg(Avg(P2,P3), Avg(P4,P5))` might be more robust but complex. Using the simpler junction calculation: `J = (-18.31, -31.51)`.

    * Midcurve Points (rounded to 2 decimal places):
        * MP0 (Endpoint 1): `(-8.13, -3.91)`
        * MP1 (Junction): `(-18.31, -31.51)`
        * MP2 (Endpoint 2): `(-26.46, -26.58)`

3.  **Construct Output:**
    * `Midcurve`: List of the calculated points `[MP0, MP1, MP2]`.
    * `Midcurve_brep`: Brep representation of the two line segments meeting at the junction.
        * `Points`: List of the calculated points `[MP0, MP1, MP2]`.
        * `Lines`: List defining the segments connecting endpoints to the junction: `[[0, 1], [2, 1]]` (MP0 to MP1, MP2 to MP1).
        * `Segments`: List where each line forms its own segment, similar to the 'Plus' example: `[[0], [1]]`.

**Predicted Output:**

{
 'ShapeName': 'L_rotated_172',
 'Profile': [[-5.65, -4.26], [-10.6, -3.56], [-14.08, -28.32], [-38.83, -24.84], [-39.53, -29.79], [-9.82, -33.96]],
 'Midcurve': [[-8.13, -3.91], [-18.31, -31.51], [-26.46, -26.58]],
 'Profile_brep': {
        'Points': [[-5.65, -4.26], [-10.6, -3.56], [-14.08, -28.32], [-38.83, -24.84], [-39.53, -29.79], [-9.82, -33.96]], 
        'Lines': [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]],
        'Segments': [[0, 1, 2, 3, 4, 5]]
    },
 'Midcurve_brep': {
        'Points': [[-8.13, -3.91], [-18.31, -31.51], [-26.46, -26.58]],
        'Lines': [[0, 1], [2, 1]], 
        'Segments': [[0], [1]]
    }
}

```
[Ref](https://medium.com/technology-hits/does-chatgpt-understand-geometry-f92022c40eb9)