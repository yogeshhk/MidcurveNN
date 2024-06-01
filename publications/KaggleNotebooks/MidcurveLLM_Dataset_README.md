## Problem Description
- **Goal**: Given a 2D closed shape (closed polygon) find its midcurve (polyline, closed or open)
- **Input**: set of points or set of connected lines, non-intersecting, simple, convex, closed polygon 
- **Output**: another set of points or set of connected lines, open/branched polygons possible

This dataset leverages Brep (Boundary Representation) like format, which is popular in 3D Solid Modeling application, to the 2D geometry problem of Geometric Dimension reduction. More info [here](https://github.com/yogeshhk/MidcurveNN).

**Sample shape**

```
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
```

Each Segment is a continuous list of lines. In case of, say `Midcurve-T`, as there is a intersection, we can treat each line in a separate segment. In case of 'Profile O', there will be two segments, one for outer lines and another for inner lines. Each line is list of points, for now, linear. Points is list of coordinates (x,y), later can be (x,y,z).

Once we have this brep representations of both, profile and the corresponding midcurve, in the text form, then we can try various machine translation approaches or LLM based fine tuning or few-shots prompt engineering.

One major advantage of text based method over image based method is that image output still has stray pixels, cleaning which will be a complex task. But text method has exact points. It may just give odd lines, which can be removed easily.