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
```
[Ref](https://medium.com/technology-hits/does-chatgpt-understand-geometry-f92022c40eb9)