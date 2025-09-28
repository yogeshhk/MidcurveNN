# Getting Text format for Midcurve

## Prompt

```
You are an expert in computational geometry and generative AI. Here is a deep research problem of geometric transformation. From 2D profile to its Midcurve.
MidcurveNN is a project aimed at solving the challenging problem of finding the midcurve of a 2D closed shape using neural networks. The primary goal is to transform a closed polygon, represented by a set of points or connected lines, into another set of points or connected lines, allowing for the possibility of open or branched polygons in the output. 

Goal: Given a 2D closed shape (closed polygon), find its midcurve (polyline, closed or open).
Input: Set of points or set of connected lines, non-intersecting, simple, convex, closed polygon.
Output: Another set of points or set of connected lines, open/branched polygons possible.

First task is to propose a text format which can represent 2D geometry well. It should cater to all shapes, geometries, etc. It should cater to open and close curve. It shold cater to loops and inner/outer loops etc.

One sample format is:

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

Column information is as below:

ShapeName (text): name of the shape. Just for visualization/reports.
Profile(text): List of Points coordinates (x,y) representing outer profile shape, typically closed.
Midcurve(text): List of Points coordinates (x,y) representing inner midcurve shape, typically open.
Profile_brep(text): Dictionary in Brep format representing outer profile shape, typically closed.
Midcurve_brep(text): Dictionary in Brep format representing inner midcurve shape, typically open.
Each Segment is a continuous list of lines. In case of, say Midcurve-T, as there is a intersection, we can treat each line in a separate segment. In case of 'Profile O', there will be two segments, one for outer lines and another for inner lines. Each line is list of points, for now, linear. Points is list of coordinates (x,y), later can be (x,y,z).

Once we have this brep representations of both, profile and the corresponding midcurve, in the text form, then we can try various machine translation approaches or LLM based fine tuning or few-shots prompt engineering.

One major advantage of text based method over image based method is that image output still has stray pixels, cleaning which will be a complex task. But text method has exact points. It may just give odd lines, which can be removed easily.

Evaluate this slowly. Step by step. Reason if it is catering to all needs. Propose changes to improve it. Final goal is to convert both profile and its midcurve into the proposed text format, then use LLM based machine translation like application to achieve the geometric transformation.
```
ChatGPT 5 within Deep Research mode asked, and I answered as follows:

```
Geometry Types: for now 2D polygons only, but plan to support splines, curves, or Bezier edges (i.e., non-linear geometries) in the future

Inner Loops: YES, always pre-classify inner vs. outer loops (e.g., for a shape like 'O'), or Yes, the format support explicitly tagged loop types?

Branching Support: For complex midcurves with branches or T-junctions, Yes we allow segments to share points or not edges,NO, segments are not strictly disjoint?

Metadata Needs: Yes,  like to include optional metadata like closed/open flags for loops, NO for directionality (clockwise/counter-clockwise) as it can be inferred from points list, or shape hierarchy, possibly

Dimensionality: No for the format be future-proofed for 3D (i.e., (x, y, z) points), or  2D sufficient for now.
```

## Response

A Structured Text Format for Profiles and Midcurves

To enable LLM-based transformation of a 2D polygon Profile into its Midcurve, we recommend a well-defined JSON-like format that explicitly encodes geometry and topology. The format should list coordinates, edges, and loop structure, and include metadata for loops and future extensions. For example, a simple rectangle “I” shape could be represented as:

{
  "ShapeName": "I",
  "Profile": [[5.0, 5.0], [10.0, 5.0], [10.0, 20.0], [5.0, 20.0]],
  "Midcurve": [[7.5, 5.0], [7.5, 20.0]],
  "Profile_brep": {
    "Points": [[5.0,5.0], [10.0,5.0], [10.0,20.0], [5.0,20.0]],
    "Edges": [[0,1], [1,2], [2,3], [3,0]],
    "Loops": [
      { "edge_indices": [0,1,2,3], "type": "outer", "closed": true }
    ]
  },
  "Midcurve_brep": {
    "Points": [[7.5,5.0], [7.5,20.0]],
    "Edges": [[0,1]],
    "Loops": [
      { "edge_indices": [0], "type": "branch", "closed": false }
    ]
  }
}


This example adds Edge and Loop objects and metadata, improving on the original format. Each Edges entry is a pair of point indices (so line 0 is from point 0 to 1, etc.). Each Loop (formerly “Segment”) lists a continuous set of edge indices, plus attributes like "type" and "closed". For instance, "type": "outer" vs "inner" explicitly tags the loop as an outer boundary or inner hole, following the common GIS convention that polygons have an outer ring and zero or more inner rings. A midcurve branch could be tagged "type": "branch". The "closed" flag indicates whether a loop is closed (e.g. an outer/inner ring is closed) or open (a branch line). This addresses inner/outer loops and open vs closed curves without relying solely on point order or inferring orientation.

- Outer/Inner Loops: We explicitly tag loops as "outer" or "inner". In existing geo-JSON conventions, polygons have one or more clockwise outer rings and zero or more counter-clockwise holes. Here, we encode that by loop metadata instead of point orientation. For example, a donut-shaped profile “O” would have two loop objects: one "type": "outer", one "type": "inner". This makes it clear to an LLM or downstream code which loop is the exterior and which is a hole, without extra inference.
- Branching Midcurves: A midcurve can have branches (like a “T” or “Y” shape). We allow separate loops for each branch or path. If two branches meet at a point, they will share the same point index in Points, but appear in separate loop lists. The shared point naturally indicates a junction. (Alternatively, one could add an explicit "junction": true flag on certain points, but usually sharing the index suffices.) Each branch is an open loop (closed=false). For example, a “T”-shaped midcurve might have two loops: one for the stem, one for the crossbar, sharing the intersection point index. This supports non-disjoint segments as required.

Each Point is a coordinate [x,y] (or [x,y,z] for future 3D support). By listing all points once in Points, edges and loops can reference them by index. This avoids duplicating coordinates and makes the format concise. (Note: we use zero-based indices for readability, but any consistent convention is fine.)

### Geometry and Metadata Fields

The proposed format extends the original by adding structured fields and metadata. Key features include:

- Consistent Naming: Use "Edges" instead of "Lines" to generalize to any edge type. Each edge is a simple polyline between two points. In the future, an edge could include curve data (see below).
- Loop Objects: The "Loops" list contains one object per continuous sub-path. Each loop has:
	- "edge_indices": list of indices into Edges for that loop.
	- "type": a label like "outer", "inner", or "branch" (this is optional but clarifies meaning).
	- "closed": true or false. Outer/inner loops on a profile are closed (start=end), midcurve paths are typically open.
- Orientation Flags (Optional): If desired, one could add a flag or derive orientation from point order. However, since closed vs open is explicit, and outer vs inner is tagged, we need not store clockwise/CCW orientation; an LLM can infer it if needed from points.

Optionally, we can include a top-level "type": "Profile" or "Midcurve" flag, but since we separate them into Profile_brep and Midcurve_brep, this is implicit. The top-level fields "Profile" and "Midcurve" can remain as simple coordinate lists if useful for quick visual checks. (They duplicate Points data but are given in original format for convenience; one could omit them and reconstruct if needed.)

This explicit JSON structure helps an LLM or other parser treat the shape as a graph: points with coordinates, edges between points, and loops (cycles or paths) built from edges. Such graph-based formats are natural for sequences-to-sequence models and have been used successfully. For example, VisionLLM shows that converting image objects into textual polygon representations allows LLMs to process shapes. Likewise, LLaMA-Mesh represents 3D meshes in text (OBJ format) with vertex and face lists, enabling an LLM to generate geometry. Here, we apply a similar idea in 2D: a text graph of points and edges.

### Handling Future Extensions

To accommodate curved edges or splines in future 2D profiles, we suggest allowing edges to carry type and control points. For instance, an edge could be represented not just as [0,1] but as an object like {"points": [0,1], "curve": "bezier", "controls": [c0, c1]} where c0,c1 are control point indices. This would generalize Edges to support non-linear geometry. (Alternatively, one could keep edges linear and represent Beziers as sequences of short edges; but if true curves are needed, a type field is clearer.)

For 3D support, the format is already mostly compatible: simply allow Points to be triples [x,y,z]. The "hasZ": true and "hasM" flags in GIS formats

 could be mimicked if needed, but often the presence of 3 values per point is enough. Including a "dimension": 3 flag or spatial reference (like GeoJSON/WKT do) is optional if the context is known. The important part is that the format is flexible: loops and edges work the same in 3D; they’d just connect 3D coords.

### Advantages of This Format
- Exactness and Clarity: Unlike raster or SVG (XML) formats, this JSON explicitly lists each vertex and connection, so there are no stray pixels or ambiguities. This precision was one motivation for MidcurveNN’s text-based approach (points rather than pixels).
- Machine-Friendliness: Text formats are well-understood by LLMs. Prior works have shown that LLMs can natively generate mesh data in OBJ text form, and that presenting shapes as text polygons (VisionLLM) allows vision tasks via LLMs. Similarly, our JSON is a plain text sequence of numbers and list markers, easily tokenized by an LLM.
- Metadata Inclusion: By adding attributes like "type" and "closed", the format explicitly encodes geometry semantics (outer vs inner, open vs closed). This reduces the chance of LLM confusion or needing to infer from coordinates alone. It also future-proofs for any additional flags (e.g. loop IDs, grouping, or application-specific tags).

### Summary of Proposed Changes
- Use explicit JSON keys: Rename Lines to Edges, Segments to Loops, and include Loops as objects with metadata.
- Tag loops: Add "type" (outer/inner/branch) and "closed" boolean for each loop. This covers polygon holes and branch structure.
- Allow shared points: Permit loops to share point indices if branches meet. (No special format change needed; just ensure a shared index means a junction.)
- Curve support: In future, allow edges to carry curve type (e.g. "bezier") and control points.
- Dimension: Accept (x,y,z) in Points and optional fields like "hasZ": true if beneficial. Otherwise, assume 2D by default.

By incorporating these changes, the text format will be robust for all required cases: convex/simple polygons, shapes with holes, and midcurves with branches. It will support extension to splines or 3D, while remaining structured and LLM-friendly. With both profile and midcurve in this form, one can then frame the midcurve extraction as a sequence-to-sequence or in-context task for an LLM. The model can map the Profile_brep points/edges to Midcurve_brep points/edges in text, similar to how LLMs have learned OBJ mesh formats. This avoids pixel errors (unlike image-based outputs) and provides exact, easily post-processed geometry.