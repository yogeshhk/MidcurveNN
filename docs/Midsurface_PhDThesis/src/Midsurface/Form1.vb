Imports System
Imports System.Type
Imports System.Activator
Imports System.Runtime.InteropServices
Imports Inventor
Imports BeyazitTest
Imports BeyazitTest.Vertices
Imports System.Windows.Vector
Imports System.IO
Imports FbMidsurfUtilities.Yogesh

Public Class Form1

    ' App variables.
    Dim _invApp As Inventor.Application
    Dim _started As Boolean = False
    Dim _initialized As Boolean = False

    Public Sub New()

        ' This call is required by the designer.
        InitializeComponent()

        ' Add any initialization after the InitializeComponent() call.

        Try
            _invApp = Marshal.GetActiveObject("Inventor.Application")

        Catch ex As Exception
            Try
                Dim invAppType As Type = _
                    GetTypeFromProgID("Inventor.Application")

                _invApp = CreateInstance(invAppType)
                _invApp.Visible = True

                _started = True

            Catch ex2 As Exception
                MsgBox(ex2.ToString())
                MsgBox("Unable to start Inventor")
            End Try
        End Try

    End Sub

    Private Function Init() As Boolean
        ' Make sure a part is active.
        If _invApp.ActiveDocumentType <> DocumentTypeEnum.kPartDocumentObject Then
            MsgBox("A part document must be active.")
            Init = False
            Exit Function
        End If

        Init = True
    End Function

    Private Sub Form1_FormClosed(sender As Object, e As System.Windows.Forms.FormClosedEventArgs) Handles Me.FormClosed

        If _started Then
            _invApp.Quit()
        End If

        _invApp = Nothing
    End Sub

    Private Sub Form1_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load

        Me.ResizeRedraw = True

    End Sub

    ' Callbacks
    Private Sub GenMidsurf_Click(sender As System.Object, e As System.EventArgs) Handles GenMidsurf.Click

        ' set active part
        If _initialized = False Then
            _initialized = Init()
        End If

        If _initialized = False Then
            Exit Sub
        End If



        Dim genMids As Yogesh.MidsurfaceGenerator = New Yogesh.MidsurfaceGenerator(_invApp)
        genMids.GenerateMidsurface()
        'genMids.TestFindDistance()

        Me.Invalidate()

    End Sub

End Class

Namespace Yogesh

    Public Class MidsurfaceGenerator

        Private m_partDoc As PartDocument
        Dim _invApp As Inventor.Application
        Dim m_ClientGraphics As ClientGraphics
        Dim m_DataSets As GraphicsDataSets

        Private m_Utilities As FbMidsurfUtilities.Yogesh.FbMidsurfUtilities

        Public Sub New(ByRef app As Inventor.Application)
            _invApp = app
            m_partDoc = _invApp.ActiveDocument()
            'm_ClientGraphics = m_partDoc.ComponentDefinition().ClientGraphicsCollection.Add("Debugging")
            'm_DataSets = m_partDoc.GraphicsDataSetsCollection.Item("Debugging")
            'If Err.Number = 0 Then
            '    ' An existing client graphics object was successfully obtained so clean up.
            '    m_DataSets.Delete()
            '    m_partDoc.ComponentDefinition().ClientGraphicsCollection.Item("Debugging").Delete()
            '    ' update the display to see the results.
            '    _invApp.ActiveView.Update()
            'Else
            '    m_DataSets = m_partDoc.GraphicsDataSetsCollection.Add("Debugging")
            'End If

            m_Utilities = New FbMidsurfUtilities.Yogesh.FbMidsurfUtilities(_invApp)

        End Sub

        Private Sub DebugDrawLine(ByRef oLine As Inventor.Line)
            Dim oLineNode As GraphicsNode = m_ClientGraphics.AddNode(1)
            Dim oLineSet As LineGraphics = oLineNode.AddLineGraphics

            Dim oPointCoords(5) As Double

            oPointCoords(0) = oLine.RootPoint.X
            oPointCoords(1) = oLine.RootPoint.Y
            oPointCoords(2) = oLine.RootPoint.Z

            oPointCoords(3) = oLine.RootPoint.X
            oPointCoords(4) = oLine.RootPoint.Y + 2
            oPointCoords(5) = oLine.RootPoint.Z

            Dim oCoordSet As GraphicsCoordinateSet = m_DataSets.CreateCoordinateSet(1)
            oCoordSet.PutCoordinates(oPointCoords)

            oLineSet.CoordinateSet = oCoordSet
            oLineNode.RenderStyle = m_partDoc.RenderStyles.Item("Purple")
            _invApp.ActiveView.Update()
        End Sub

        Private Sub DebugDrawPoint(ByRef oPoint As Inventor.Point)
            Dim oPointNode As GraphicsNode = m_ClientGraphics.AddNode(1)
            Dim oPointSet As LineGraphics = oPointNode.AddLineGraphics

            Dim oPointCoords(2) As Double

            oPointCoords(0) = oPoint.X
            oPointCoords(1) = oPoint.Y
            oPointCoords(2) = oPoint.Z

            Dim oCoordSet As GraphicsCoordinateSet = m_DataSets.CreateCoordinateSet(1)
            oCoordSet.PutCoordinates(oPointCoords)

            oPointSet.CoordinateSet = oCoordSet
            oPointNode.RenderStyle = m_partDoc.RenderStyles.Item("Purple")
            _invApp.ActiveView.Update()
        End Sub

        Private Sub DebugPrintPoint(p As Point)
            Debug.Print(Str(p.X) + "; " + Str(p.Y) + "; " + Str(p.Z))
        End Sub

        Private Sub DebugPrintPathInfo(p As Inventor.Path)
            Dim pe As PathEntity
            For Each pe In p
                DebugPrintPoint(pe.Curve.StartPoint)
                DebugPrintPoint(pe.Curve.EndPoint)
            Next
        End Sub

        Private Sub DeleteInvalidSketchEntities(p As Inventor.Path)
            Dim pe As PathEntity
            For Each pe In p
                DebugPrintPoint(pe.Curve.StartPoint)
                DebugPrintPoint(pe.Curve.EndPoint)

                'Dim MinParam As Double
                'Dim MaxParam As Double
                'Dim length As Double

                'pe.Curve.Evaluator.GetParamExtents(MinParam, MaxParam)
                'pe.Curve.Evaluator.GetLengthAtParam(MinParam, MaxParam, length)
                Dim length As Double
                length = _invApp.MeasureTools.GetMinimumDistance(pe.Curve.StartPoint, pe.Curve.EndPoint)

                If length < 0.00001 Then
                    pe.SketchEntity.Delete()
                End If

            Next
        End Sub
        Private Function RemoveRedundantEntities(oPath As Inventor.Path, oSkPath As PlanarSketch, oCompDef As ComponentDefinition) As Inventor.Path
            ' Remove unnecessary lines from it
            Dim oTO As TransientObjects
            oTO = _invApp.TransientObjects

            Dim oColl As ObjectCollection
            oColl = oTO.CreateObjectCollection

            Dim oPathEntity As PathEntity
            For Each oPathEntity In oPath
                Dim oSkEntity As SketchEntity
                oSkEntity = oPathEntity.SketchEntity

                If oSkEntity.Parent Is oSkPath Then
                    Call oColl.Add(oSkEntity)
                End If
            Next

            Dim oPathNew As Inventor.Path
            oPathNew = oCompDef.Features.CreateSpecifiedPath(oColl)
            RemoveRedundantEntities = oPathNew
        End Function

        Private Function FindOrCreateSketchPoint(ByRef oSketch As PlanarSketch, ByVal x As Double, ByVal y As Double) As SketchPoint
            FindOrCreateSketchPoint = Nothing
            Dim found As Boolean = False
            Dim oTransGeom As TransientGeometry
            oTransGeom = _invApp.TransientGeometry
            Dim tolerance As Double = 0.001

            For Each skpt As SketchPoint In oSketch.SketchPoints
                Dim skptx As Double = skpt.Geometry.X
                Dim skpty As Double = skpt.Geometry.Y
                Dim diffx As Double = Math.Abs(skptx - x)
                Dim diffy As Double = Math.Abs(skpty - y)
                If (diffx < tolerance) And (diffy < tolerance) Then
                    found = True
                    FindOrCreateSketchPoint = skpt
                    Exit Function
                End If
            Next
            If Not found Then
                FindOrCreateSketchPoint = oSketch.SketchPoints.Add(oTransGeom.CreatePoint2d(x, y))
            End If
        End Function

        Private Function GenerateSingleEntityVertices(ByRef profile_entity As Inventor.ProfileEntity) As BeyazitTest.Vertices

            Dim entity As SketchEntity = profile_entity.SketchEntity
            Dim perimeter As Double = profile_entity.Parent.Parent.RegionProperties.Perimeter ' Perimeter of full profile. Use this to decide segmentation, as we dont want to small segments
            Dim toleranceLength As Double = 0.05 * perimeter

            Dim singleEntityVertices As BeyazitTest.Vertices = New BeyazitTest.Vertices ' these are just for this individual curves

            If TypeOf entity Is SketchCircle Then  '' TEMP NEED TO REFACTOR LATER
                Dim curveEval As Curve2dEvaluator = entity.Geometry.Evaluator
                Dim minU As Double
                Dim maxU As Double
                curveEval.GetParamExtents(minU, maxU)

                ' Get the curve length. 
                Dim length As Double
                curveEval.GetLengthAtParam(minU, maxU, length)

                ' Determine the length between segments. 
                Dim segmentCount As Integer = 12 ' Adjust to resolution needed

                Dim offset As Double
                offset = length / segmentCount
                ' NOT FOR FULL CIRCLE
                'If offset < toleranceLength Then
                '    segmentCount = 1
                '    offset = length
                'End If
                Dim currentLength As Double = 0

                For i As Integer = 0 To segmentCount

                    Dim currentParam As Double
                    curveEval.GetParamAtLength(minU, currentLength, _
                                               currentParam)
                    currentLength = currentLength + offset

                    Dim params(0) As Double
                    params(0) = currentParam
                    Dim coords() As Double = {}
                    curveEval.GetPointAtParam(params, coords)

                    singleEntityVertices.Add(New System.Windows.Vector(coords(0), coords(1)))

                Next
                GenerateSingleEntityVertices = singleEntityVertices
                Exit Function
            End If

            ' Every sketch entity has start and end, so caching them before, needed for 'reverse' logic later
            Dim startpt As Inventor.Point2d = entity.StartSketchPoint.Geometry
            Dim endpt As Inventor.Point2d = entity.EndSketchPoint.Geometry
            Dim v1 As System.Windows.Vector = New System.Windows.Vector(startpt.X, startpt.Y)
            Dim v2 As System.Windows.Vector = New System.Windows.Vector(endpt.X, endpt.Y)


            If TypeOf entity Is SketchPoint Then
                ' do nothing
            ElseIf TypeOf entity Is SketchLine Then
                ' Add already cached start and end point, nothing else is needed
                If (singleEntityVertices.Index(v1) = -1) Then
                    singleEntityVertices.Add(v1)
                End If
                If (singleEntityVertices.Index(v2) = -1) Then
                    singleEntityVertices.Add(v2)
                End If

            Else ' curved entities, generically get sample points

                ' Get the evaluator from the associate geometry. 
                Dim curveEval As Curve2dEvaluator = entity.Geometry.Evaluator
                Dim minU As Double
                Dim maxU As Double
                curveEval.GetParamExtents(minU, maxU)

                ' Get the curve length. 
                Dim length As Double
                curveEval.GetLengthAtParam(minU, maxU, length)

                ' Determine the length between segments. 
                Dim segmentCount As Integer = 6 ' Adjust to resolution needed

                Dim offset As Double
                offset = length / segmentCount
                If offset < toleranceLength Then
                    segmentCount = 1
                    offset = length
                End If
                Dim currentLength As Double = 0

                For i As Integer = 0 To segmentCount

                    Dim currentParam As Double
                    curveEval.GetParamAtLength(minU, currentLength, _
                                               currentParam)
                    currentLength = currentLength + offset

                    Dim params(0) As Double
                    params(0) = currentParam
                    Dim coords() As Double = {}
                    curveEval.GetPointAtParam(params, coords)

                    singleEntityVertices.Add(New System.Windows.Vector(coords(0), coords(1)))

                Next

            End If
            For Each vtt As System.Windows.Vector In singleEntityVertices
                Debug.Print("[" & vtt.X & "," & vtt.Y & "], ")
            Next
            Debug.Print("------------------")

            GenerateSingleEntityVertices = singleEntityVertices

        End Function

        Private Sub GeneratePathVertices(ByRef path As Inventor.ProfilePath, ByRef pathindex As Integer, ByVal hasHoles As Boolean, ByRef allProfileVertices As BeyazitTest.Vertices)

            'YOGESH: path.Count is 0 for profile created by TEXT command. Not yet implemeneted by Inventor APIs (wishlist)
            If Not path Is Nothing And path.Count > 0 Then

                Dim pathVertices As BeyazitTest.Vertices = New BeyazitTest.Vertices ' these are for this individual profile-path, outer or inner
                Dim entityCounter As Integer = 0
                'YOGESH: Its assumed that curves in the path are connected end-to-end, if not following logic wont work
                For Each profile_entity As Inventor.ProfileEntity In path
                    entityCounter += 1

                    Dim singleEntityVertices As BeyazitTest.Vertices = New BeyazitTest.Vertices ' these are just for this individual curves

                    singleEntityVertices = GenerateSingleEntityVertices(profile_entity)

                    Dim lastSingleEntityVertex As System.Windows.Vector = singleEntityVertices(singleEntityVertices.Count - 1)
                    Dim firstSingleEntityVertex As System.Windows.Vector = singleEntityVertices(0)
                    Dim lastIndexOfPathVerticesSoFar As Integer = pathVertices.Count - 1

                    ' Individual entities may be connected in 'reverse' directions, correct it. Except the CLosing segment
                    If Not entityCounter = path.Count And pathVertices.Index(lastSingleEntityVertex) = 0 Then
                        pathVertices.Reverse()
                        singleEntityVertices.Reverse()
                    ElseIf pathVertices.Count > 1 Then
                        If pathVertices.Index(lastSingleEntityVertex) = lastIndexOfPathVerticesSoFar Then
                            singleEntityVertices.Reverse()
                        ElseIf pathVertices.Index(firstSingleEntityVertex) = 0 Then
                            pathVertices.Reverse()
                        End If
                    End If

                    ' Add sample points from this singleEntity to path vertices
                    For j As Integer = 0 To singleEntityVertices.Count - 1
                        Dim v As System.Windows.Vector = singleEntityVertices(j)
                        If (pathVertices.Index(v) = -1) Then
                            pathVertices.Add(v)
                        End If
                    Next
                Next

                'if there are holes, meaning more than one path, then add first vertex again to close it
                If hasHoles Then
                    If pathindex = 0 Then ' first profile should be CCW
                        pathVertices.Add(pathVertices.Vertex(0))
                        pathVertices.ForceCounterClockWise()
                    Else
                        If Not pathVertices.IsCounterClockWise() Then
                            allProfileVertices.Add(pathVertices.Vertex(pathVertices.Count - 1))
                        Else
                            pathVertices.Add(pathVertices.Vertex(0))
                            pathVertices.ForceClockWise() ' make it clockwise!!!!!!!!!!!!!
                        End If
                    End If
                    For Each vp As System.Windows.Vector In pathVertices
                        allProfileVertices.Add(vp)
                    Next
                Else ' Single path, no holes
                    pathVertices.ForceCounterClockWise()
                    For Each vp As System.Windows.Vector In pathVertices
                        allProfileVertices.Add(vp)
                    Next
                End If

            End If
        End Sub

        Private Function GenerateMidcurveFromProfile(ByRef profile As Inventor.Profile) As List(Of BeyazitTest.Vertices)

            Dim allProfileVertices As BeyazitTest.Vertices = New BeyazitTest.Vertices

            If Not profile Is Nothing Then
                Dim hasHoles As Boolean = profile.Count > 1
                Dim pathIndex As Integer = 0
                For Each path As Inventor.ProfilePath In profile
                    GeneratePathVertices(path, pathIndex, hasHoles, allProfileVertices)
                    pathIndex = pathIndex + 1
                Next
            End If

            BeyazitTest.Vertices.DumpProfileToFile(allProfileVertices, "Profile.dat")

            Dim resultsWithTriangulation As List(Of BeyazitTest.Vertices)
            resultsWithTriangulation = YogeshBayazitDecomposer.ConvexPartition(allProfileVertices)

            YogeshBayazitDecomposer.DumpPartitionsToFile(resultsWithTriangulation, "Partitions.dat")

            'Dim polygonList As List(Of BeyazitTest.Vertices)
            'polygonList = Triangulator.TriagnulateQuadPlusPolygons(resultsWithTriangulation)
            Dim midcurves As List(Of BeyazitTest.Vertices) = MidcurveGenerator.GenerateMidcurves(resultsWithTriangulation)
            MidcurveGenerator.DumpMidcurvesToFile(allProfileVertices, midcurves, "Midcurves.dat")

            GenerateMidcurveFromProfile = midcurves

        End Function

        Private Function GenerateNewProfilesFromMidcurves(oSketch As PlanarSketch, midcurves As List(Of BeyazitTest.Vertices)) As ObjectCollection

            ' SketchLines made up of Midcurves are added to the shared oSketch
            Dim oTransGeom As TransientGeometry
            oTransGeom = _invApp.TransientGeometry

            Dim profileCollection As ObjectCollection
            profileCollection = _invApp.TransientObjects.CreateObjectCollection

            Dim oLine As SketchLine = Nothing

            For ii As Integer = 0 To midcurves.Count - 1
                Dim vertices As BeyazitTest.Vertices = midcurves(ii)

                Dim startOfCurrentCurve As SketchPoint = Nothing
                For jj As Integer = 0 To vertices.Count - 1 'Step steploop
                    Dim vt As System.Windows.Vector = vertices.Vertex(jj)
                    If startOfCurrentCurve Is Nothing Then
                        'startOfCurrentCurve = oSketch.SketchPoints.Add(oTransGeom.CreatePoint2d(vt.X, vt.Y)) 'oSketch.SketchPoints.Add
                        startOfCurrentCurve = FindOrCreateSketchPoint(oSketch, vt.X, vt.Y)
                    Else
                        'Dim currentPoint As SketchPoint = oSketch.SketchPoints.Add(oTransGeom.CreatePoint2d(vt.X, vt.Y))
                        Dim currentPoint As SketchPoint = FindOrCreateSketchPoint(oSketch, vt.X, vt.Y)
                        oLine = oSketch.SketchLines.AddByTwoPoints(startOfCurrentCurve, currentPoint)
                        '' ToDo: currently, for each line, a new profile is made, need to see if paths can be sent
                        'Dim oProfile As Profile = oSketch.Profiles.AddForSurface(oLine)
                        'profileCollection.Add(oProfile)
                    End If
                Next
            Next
            ' ToDo: currently, for each line, a new profile is made, need to see if paths can be sent
            Dim oProfile As Profile = oSketch.Profiles.AddForSurface(oLine)
            profileCollection.Add(oProfile)
            GenerateNewProfilesFromMidcurves = profileCollection

        End Function

        Private Function GetPathFromExtrude(ByRef extrude As ExtrudeFeature, ByRef dir As PartFeatureExtentDirectionEnum) As Double
            Dim length As Double = 0.0

            Dim extrudeDef As ExtrudeDefinition
            extrudeDef = extrude.Definition

            ' Get centroid of the profile
            ' Get the centroid of the sweep profile in sketch space
            Dim oProfileOrigin As Point2d = extrude.Profile.RegionProperties.Centroid

            ' Transform the centroid from sketch space to model space
            Dim centroid As Point = extrude.Profile.Parent.SketchToModelSpace(oProfileOrigin)

            ' Display information in the definition object.
            Select Case extrudeDef.ExtentType
                Case PartFeatureExtentEnum.kDistanceExtent
                    Dim distance As DistanceExtent
                    distance = extrudeDef.Extent
                    length = distance.Distance.Value
                    dir = distance.Direction

                Case PartFeatureExtentEnum.kFromToExtent
                    Dim fromTo As FromToExtent
                    fromTo = extrudeDef.Extent

                    Debug.Print("FromTo extent between to faces and/or work features.")
                Case PartFeatureExtentEnum.kThroughAllExtent
                    Dim throughAll As ThroughAllExtent
                    throughAll = extrudeDef.Extent

                    Debug.Print("Through all extent.")
                Case PartFeatureExtentEnum.kToExtent
                    Dim toExt As ToExtent
                    toExt = extrudeDef.Extent
                    If TypeOf toExt.ToEntity() Is Inventor.Faces Then
                        Dim faces As Inventor.Faces = toExt.ToEntity()
                        Dim testFace As Inventor.Face = faces.Item(1)
                        length = _invApp.MeasureTools.GetMinimumDistance(centroid, testFace)
                        If testFace.SurfaceType <> SurfaceTypeEnum.kPlaneSurface Then
                            length = 1.01 * length
                        End If
                    ElseIf TypeOf toExt.ToEntity() Is Inventor.WorkPlane Then
                        Dim wp As WorkPlane = toExt.ToEntity()
                        length = _invApp.MeasureTools.GetMinimumDistance(centroid, wp)
                    End If
                    dir = toExt.Direction

                Case PartFeatureExtentEnum.kToNextExtent
                    Dim toNext As ToNextExtent
                    toNext = extrudeDef.Extent

                    Debug.Print("To next extent.")
                Case Else
                    Debug.Print("Unhandled case: " & extrudeDef.ExtentType)
            End Select

            GetPathFromExtrude = length
        End Function

        Private Function GenerateMidsurfaceFromExtrude(ByRef extFeature As Inventor.ExtrudeFeature) As SurfaceBody

            Dim dir As PartFeatureExtentDirectionEnum = PartFeatureExtentDirectionEnum.kPositiveExtentDirection

            Dim length As Double = GetPathFromExtrude(extFeature, dir)

            ' Get size of the profile and determine if its far smaller compared to Guide-Curve length
            Dim profileDiagonal As Double = Math.Sqrt(extFeature.Profile.RegionProperties.Area)
            Dim isGuideCurveLonger As Boolean = (length / profileDiagonal) > 2

            Dim oCompDef As PartComponentDefinition
            oCompDef = m_partDoc.ComponentDefinition()

            If isGuideCurveLonger Then
                Debug.Print(extFeature.Name + " : Processing Midcurves Way")

                ' utilize same sketch in SHARED mode, no need to extract its params and create a duplicate copy
                Dim oSketch As PlanarSketch
                oSketch = extFeature.Definition.Profile.Parent 'oCompDef.Sketches.Add(oCompDef.WorkPlanes(3))
                oSketch.Shared = True

                ' Get Midcurves of the Existing profile
                Dim midcurves As List(Of BeyazitTest.Vertices) = GenerateMidcurveFromProfile(extFeature.Profile)

                ' Prepapre new profiles using Midcurves
                ' PROBLEM: All miducurves can not be picked in a Single Profile, epsecially if they are branched.
                ' Another problem: To compose a path, a common sketchpoint needs to be re-used in all the lines connected to it.
                ' But it stops at the branch. So some portions are in a path but some are not. Its hard to detect, which curves
                ' have got consumed because of this Path selection rule. Single Extrusion Srf feature can not take multiple
                ' disconnected curves. It does so only in the Solid-output mode. HIGHLY LIMITED SUPPORT
                ' Decision for now: Let all Midcurves be separate. Each one creates one Profile, and one Extrusion Srf Feature

                Dim oProfiles As ObjectCollection = GenerateNewProfilesFromMidcurves(oSketch, midcurves)
                Dim midsurface As SurfaceBody = Nothing

                For Each oProfileOne In oProfiles
                    ' Create new Extrude feature definition, supplying the above parameters
                    Dim oExtrudeDef As ExtrudeDefinition
                    oExtrudeDef = oCompDef.Features.ExtrudeFeatures.CreateExtrudeDefinition(oProfileOne, PartFeatureOperationEnum.kSurfaceOperation)
                    oExtrudeDef.SetDistanceExtent(length, dir)
                    'oExtrudeDef.SetDistanceExtentTwo(profileSideExtension)

                    ' Create Surface Extrude Feature
                    Dim oExtrudeOne As ExtrudeFeature
                    oExtrudeOne = oCompDef.Features.ExtrudeFeatures.Add(oExtrudeDef)
                    midsurface = oExtrudeOne.SurfaceBodies.Item(1)
                Next

                ' Make the Shared Sketch invisible
                oSketch.Visible = False

                ' Return value
                GenerateMidsurfaceFromExtrude = midsurface

            Else
                ' Big profile, so just offset
                Debug.Print(extFeature.Name + " : Processing Offset Way")

                Dim oFaceColl As FaceCollection
                oFaceColl = _invApp.TransientObjects.CreateFaceCollection

                ' FOLLOWING COULD BE BAD PERFORMANCE WISE
                'find the face with max area, and offset it
                Dim maxArea As Double = -0.001
                Dim maxAreaFace As Inventor.Face = Nothing
                For Each f As Inventor.Face In extFeature.Faces
                    Dim fArea As Double = f.Evaluator.Area
                    If fArea > maxArea Then
                        maxArea = fArea
                        maxAreaFace = f
                    End If
                Next
                If Not maxAreaFace Is Nothing Then
                    oFaceColl.Add(maxAreaFace)
                    length = m_Utilities.findDistanceToOppositeFace(maxAreaFace, extFeature)
                End If

                ' START OR END FACE MAY NOT BE ALWAYS the BIGGER
                'If extFeature.StartFaces.Count > 0 Then
                '    For Each oface In extFeature.StartFaces
                '        oFaceColl.Add(oface)
                '    Next
                'ElseIf extFeature.EndFaces.Count > 0 Then
                '    For Each oface In extFeature.EndFaces
                '        oFaceColl.Add(oface)
                '    Next
                'End If

                '' FIND BIGGER OF SIDE OR START FACES
                'Dim normal As Inventor.Vector
                'Dim startFaceArea As Double = extFeature.StartFaces.Item(1).Evaluator.Area
                'Dim sideFaceArea As Double = extFeature.SideFaces.Item(1).Evaluator.Area
                'If startFaceArea > sideFaceArea Then
                '    oFaceColl.Add(extFeature.StartFaces.Item(1))
                '    'length to remain as calculated above
                'Else
                '    oFaceColl.Add(extFeature.SideFaces.Item(1))
                '    length = findDistanceToOppositeFace(extFeature.SideFaces.Item(1), extFeature)
                'End If

                If oFaceColl.Count > 0 Then
                    ' Offset the base face of the extrude
                    ' dir = PartFeatureExtentDirectionEnum.kNegativeExtentDirection ' OVERRIDE
                    If length < 0 Then
                        dir = PartFeatureExtentDirectionEnum.kNegativeExtentDirection
                    End If
                    On Error Resume Next
                    'Dim eLengthUnit As UnitsTypeEnum = m_partDoc.UnitsOfMeasure.LengthUnits
                    Dim offsetdist As Double = length / 2.0 'm_partDoc.UnitsOfMeasure.ConvertUnits(length / 2.0, eLengthUnit, "cm") ' Have to be in centimeters
                    Dim oOffsetFeature As ThickenFeature = oCompDef.Features.ThickenFeatures.Add(oFaceColl, offsetdist, PartFeatureExtentDirectionEnum.kNegativeExtentDirection, PartFeatureOperationEnum.kSurfaceOperation, True, False, False)
                    If Err.Number <> 0 Then
                        'MsgBox("Could not create ThickenFeature.")
                    Else
                        GenerateMidsurfaceFromExtrude = oOffsetFeature.SurfaceBodies.Item(1)
                    End If

                Else
                    Debug.Print(extFeature.Name + " :ERROR Offset did not work")
                End If
            End If

        End Function

        Private Sub GenerateMidsurfaceFromRevolveByAngle(ByRef revFeature As Inventor.RevolveFeature)

            ' Get Revolve Angle
            Dim angle As AngleExtent
            angle = revFeature.Extent
            Dim theta As Double = angle.Angle.Value

            ' Get Extrude Direction
            Dim dir As PartFeatureExtentDirectionEnum = angle.Direction
            Dim axis As SketchLine = revFeature.AxisEntity

            ' For revolve, theta less than 30, qualifies for NON-MIDCURVES case
            Dim isThetaSmaller As Boolean = theta < (Math.PI / 6)

            Dim oCompDef As PartComponentDefinition
            oCompDef = m_partDoc.ComponentDefinition()

            If isThetaSmaller = False Then

                ' Get Midcurves of the Existing profile
                Dim midcurves As List(Of BeyazitTest.Vertices) = GenerateMidcurveFromProfile(revFeature.Profile)

                ' utilize same sketch in SHARED mode, no need to extract its params and create a duplicate copy
                Dim oSketch As PlanarSketch
                oSketch = revFeature.Profile.Parent 'oCompDef.Sketches.Add(oCompDef.WorkPlanes(3))
                oSketch.Shared = True

                Dim oProfiles As ObjectCollection = GenerateNewProfilesFromMidcurves(oSketch, midcurves)

                For Each oProfileOne In oProfiles
                    ' Create Surface Revolve Feature
                    Dim oRevolveOne As RevolveFeature
                    oRevolveOne = oCompDef.Features.RevolveFeatures.AddByAngle(oProfileOne, axis, theta, dir,
                                                                               PartFeatureOperationEnum.kSurfaceOperation)
                Next

                ' Make the Shared Sketch invisible
                oSketch.Visible = False
            Else
                ' Big profile, so just offset

                Dim oFaceColl As FaceCollection
                oFaceColl = _invApp.TransientObjects.CreateFaceCollection

                For Each oFace In revFeature.StartFaces
                    oFaceColl.Add(oFace)
                Next

                ' Offset the base face 
                Dim oOffsetFeature As ThickenFeature
                oOffsetFeature = oCompDef.Features.ThickenFeatures.Add(oFaceColl, 0, dir, PartFeatureOperationEnum.kSurfaceOperation)

                Dim bodyCollection As ObjectCollection
                bodyCollection = _invApp.TransientObjects.CreateObjectCollection

                bodyCollection.Add(oOffsetFeature.SurfaceBodies.Item(1))

                Dim oMoveDef As MoveDefinition
                oMoveDef = oCompDef.Features.MoveFeatures.CreateMoveDefinition(bodyCollection)
                oMoveDef.AddRotateAboutAxis(oCompDef.WorkAxes.Item(2), False, theta / 2) ' DEBUG 'axis'

                Dim oMoveFeature As MoveFeature
                oMoveFeature = oCompDef.Features.MoveFeatures.Add(oMoveDef)

            End If

        End Sub

        Private Sub GenerateMidsurfaceFromRevolveToNext(ByRef revFeature As Inventor.RevolveFeature)

            ' Get Revolve Angle
            Dim toNext As ToExtent = revFeature.Extent
            Dim limiter As WorkPlane = toNext.ToEntity()
            Dim axis As SketchLine = revFeature.AxisEntity

            Dim oSketch As PlanarSketch
            oSketch = revFeature.Profile.Parent 'oCompDef.Sketches.Add(oCompDef.WorkPlanes(3))
            Dim sketchPlane As WorkPlane = oSketch.PlanarEntity
            Dim theta As Double = _invApp.MeasureTools.GetAngle(sketchPlane, limiter)

            ' Experiment!!!!!!!!!!!
            Dim startpoint As Point = revFeature.StartFaces.Item(1).PointOnFace()
            Dim endpoint As Point = limiter.Plane.RootPoint 'revFeature.EndFaces.Item(1).PointOnFace()
            Dim midpoint As Point = axis.Geometry3d.MidPoint
            theta = _invApp.MeasureTools.GetAngle(startpoint, midpoint, endpoint)
 

            ' Get Extrude Direction
            Dim dir As PartFeatureExtentDirectionEnum = toNext.Direction


            ' For revolve, theta less than 30, qualifies for NON-MIDCURVES case
            Dim isThetaSmaller As Boolean = theta < (Math.PI / 6)

            Dim oCompDef As PartComponentDefinition
            oCompDef = m_partDoc.ComponentDefinition()

            If isThetaSmaller = False Then

                ' Get Midcurves of the Existing profile
                Dim midcurves As List(Of BeyazitTest.Vertices) = GenerateMidcurveFromProfile(revFeature.Profile)

                ' utilize same sketch in SHARED mode, no need to extract its params and create a duplicate copy
               
                oSketch.Shared = True

                Dim oProfiles As ObjectCollection = GenerateNewProfilesFromMidcurves(oSketch, midcurves)

                For Each oProfileOne In oProfiles
                    ' Create Surface Revolve Feature
                    Dim oRevolveOne As RevolveFeature
                    oRevolveOne = oCompDef.Features.RevolveFeatures.AddByAngle(oProfileOne, axis, theta, dir,
                                                                               PartFeatureOperationEnum.kSurfaceOperation)
                Next

                ' Make the Shared Sketch invisible
                oSketch.Visible = False
            Else
                ' Big profile, so just offset

                Dim oFaceColl As FaceCollection
                oFaceColl = _invApp.TransientObjects.CreateFaceCollection

                For Each oFace In revFeature.StartFaces
                    oFaceColl.Add(oFace)
                Next

                ' Offset the base face 
                Dim oOffsetFeature As ThickenFeature
                oOffsetFeature = oCompDef.Features.ThickenFeatures.Add(oFaceColl, 0, dir, PartFeatureOperationEnum.kSurfaceOperation)

                Dim bodyCollection As ObjectCollection
                bodyCollection = _invApp.TransientObjects.CreateObjectCollection

                bodyCollection.Add(oOffsetFeature.SurfaceBodies.Item(1))

                Dim oMoveDef As MoveDefinition
                oMoveDef = oCompDef.Features.MoveFeatures.CreateMoveDefinition(bodyCollection)
                oMoveDef.AddRotateAboutAxis(oCompDef.WorkAxes.Item(2), False, theta / 2) ' DEBUG 'axis'

                Dim oMoveFeature As MoveFeature
                oMoveFeature = oCompDef.Features.MoveFeatures.Add(oMoveDef)

            End If

        End Sub

        Private Sub GenerateMidsurfaceFromSweep(ByRef sweepFeature As Inventor.SweepFeature)

            Dim oCompDef As PartComponentDefinition
            oCompDef = m_partDoc.ComponentDefinition()

            Dim path As Inventor.Path
            path = sweepFeature.Path

            Dim profile As Inventor.Profile
            profile = sweepFeature.Profile
            Dim pathlenth As Double = m_Utilities.GetLengthOfPath(path, profile, oCompDef)
            Dim smallestProfileSidelength As Double = m_Utilities.GetSmallestSideLength(profile)

            'Dim isProfileSmaller As Boolean = pathlenth > Math.Sqrt(profile.RegionProperties.Perimeter)
            Dim isProfileSmaller As Boolean = pathlenth > smallestProfileSidelength

            If isProfileSmaller = True Then

                ' Get Midcurves of the Existing profile
                Dim midcurves As List(Of BeyazitTest.Vertices) = GenerateMidcurveFromProfile(profile)

                ' Midcurve as Profile Sketch
                Dim profileSketch As PlanarSketch = profile.Parent
                Dim newProfileSketch As PlanarSketch = m_Utilities.CreateNewSketch(profileSketch) ' Creating EMPTY sketch, so NOT copying the contents. IT HAS TO BE BEFORE PATH SKETCH
                Dim oProfiles As ObjectCollection = GenerateNewProfilesFromMidcurves(newProfileSketch, midcurves)

                ' Copy of original path as Path Sketch
                Dim pathSketch As PlanarSketch = path.Item(1).SketchEntity.Parent
                Dim newPathSketch As PlanarSketch = m_Utilities.CreateNewSketch(pathSketch, True) ' Copy contents from original path to new path sketch

                Dim newPath As Inventor.Path = Nothing

                ' Sometimes offseting PATH to meet PROFILE throws exception below. DONNO WHY. So put TRY-CATCH, and not doing offset in case of exception
                Try
                    Dim oStartPointProfile As SketchPoint = oProfiles.Item(1).Item(1).Item(1).StartSketchPoint
                    Dim wpt As WorkPoint = oCompDef.WorkPoints.AddFixed(oStartPointProfile.Geometry3d, True)
                    Dim newProjectedPoint As SketchPoint = newPathSketch.AddByProjectingEntity(wpt)
                    ' TBD: Need a check if newProjectedPoint is already on any of the sektch geometry entity, if so, do not need to OFFSET as below, at all
                    'Dim interSketch As Sketch3D = oCompDef.Sketches3D.Add
                    'Dim intcurves As IntersectionCurves = interSketch.IntersectionCurves.Add(newProfileSketch.SketchLines.Item(1), newPathSketch.SketchLines.Item(1))

                    Dim oCollection As ObjectCollection = _invApp.TransientObjects.CreateObjectCollection

                    ' DOES NOT WORK if I add all the SketchEntities to this collection. 
                    ' I need some other generic container having only sketch geometry entities and 
                    ' which does not have entities like dimensions constraints etc
                    For Each ske As SketchLine In newPathSketch.SketchLines ' HARDCODED, TBD
                        oCollection.Add(ske)
                    Next
                    For Each skc As SketchArc In newPathSketch.SketchArcs ' HARDCODED, TBD
                        oCollection.Add(skc)
                    Next
                    If oCollection.Count > 0 Then
                        Dim se As SketchEntitiesEnumerator = newPathSketch.OffsetSketchEntitiesUsingPoint(oCollection, newProjectedPoint.Geometry)
                        newPath = oCompDef.Features.CreatePath(se.Item(1))
                    Else
                        newPath = oCompDef.Features.CreatePath(newPathSketch.SketchLines.Item(1))
                    End If
                Catch ex As Exception
                    newPath = oCompDef.Features.CreatePath(newPathSketch.SketchLines.Item(1))
                End Try

                'DebugPrintPathInfo(newPath)
                Dim cleanedNewPath As Inventor.Path = RemoveRedundantEntities(newPath, newPathSketch, oCompDef)


                Dim oProfileOne As Profile = newProfileSketch.Profiles.AddForSurface(newProfileSketch.SketchLines.Item(1))
                Dim oSweepOne As SweepFeature = Nothing
                Try
                    oSweepOne = oCompDef.Features.SweepFeatures.AddUsingPath(oProfileOne, newPath, PartFeatureOperationEnum.kSurfaceOperation, SweepProfileOrientationEnum.kNormalToPath)
                Catch ex As Exception
                    CreateMidurfByOffsettingSweepfaces(sweepFeature, smallestProfileSidelength / 2.0, True)
                End Try


                '' Need any geom entity of the sketch, for shifting/offsetting later
                'Dim newPath As Inventor.Path = Nothing
                'Dim anySketchEntity As SketchEntity = Nothing
                'If newPathSketch.SketchLines.Count > 0 Then
                '    anySketchEntity = newPathSketch.SketchLines.Item(1) ' Is SketchEntities better than SketchLines, hmm. crashes!!
                'ElseIf newPathSketch.SketchArcs.Count > 0 Then
                '    anySketchEntity = newPathSketch.SketchArcs.Item(1) ' SO PATHETIC logic, just becuase sketchentities crashes
                'Else
                '    anySketchEntity = newPathSketch.SketchPoints.Item(1)
                'End If

                '' Profile and Path should intersect, but generally they are away. [ BUT, HOW TO CHECK IF THEY ARE INTERSECTING???]
                '' So, project first point on to path's sketch plane, and then offset the path to that point so that SWEEP's profile and path will intersect
                'Dim oStartPointProfile As SketchPoint = oProfiles.Item(1).Item(1).Item(1).StartSketchPoint
                'Dim wpt As WorkPoint = oCompDef.WorkPoints.AddFixed(oStartPointProfile.Geometry3d, True)
                'Dim whenOffsetStartsWorking As Boolean = False
                'If whenOffsetStartsWorking Then
                '    ' Get a point to offset the path to
                '    Dim newProjectedPoint As SketchPoint = newPathSketch.AddByProjectingEntity(wpt)
                '    Dim oCollection As ObjectCollection = _invApp.TransientObjects.CreateObjectCollection
                '    oCollection.Add(anySketchEntity)
                '    Dim offsettedentities As SketchEntitiesEnumerator = newPathSketch.OffsetSketchEntitiesUsingPoint(oCollection, newProjectedPoint.Geometry, True, False)
                '    newPath = oCompDef.Features.CreatePath(offsettedentities.Item(1))
                'Else
                '    newPath = oCompDef.Features.CreatePath(anySketchEntity)
                'End If

                ' WHY FOLLOWING IS FAILING???
                'Dim oProfileOne As Profile
                'oProfileOne = newProfileSketch.Profiles.AddForSurface(newProfileSketch.SketchLines.Item(1))
                'oSweepOne = oCompDef.Features.SweepFeatures.AddUsingPath(oProfileOne, newPath, PartFeatureOperationEnum.kSurfaceOperation, SweepProfileOrientationEnum.kNormalToPath)

                'For Each oProfileOne In oProfiles
                '    Try
                '        ' Create Surface Sweep Feature
                '        oSweepOne = oCompDef.Features.SweepFeatures.AddUsingPath(oProfileOne, newPath, PartFeatureOperationEnum.kSurfaceOperation, SweepProfileOrientationEnum.kNormalToPath)
                '    Catch ex2 As Exception
                '        Try
                '            oSweepOne = oCompDef.Features.SweepFeatures.AddUsingPath(oProfileOne, newPath, PartFeatureOperationEnum.kSurfaceOperation, SweepProfileOrientationEnum.kParallelToOriginalProfile)
                '        Catch ex As Exception
                '            CreateMidurfByOffsettingSweepfaces(sweepFeature, oCompDef.Thickness.Value / 2.0, True)
                '        End Try
                '    End Try
                'Next

                ' Make the Shared Sketch invisible
                profileSketch.Visible = False
                pathSketch.Visible = False
                newProfileSketch.Visible = False
                newPathSketch.Visible = False

            Else
                CreateMidurfByOffsettingSweepfaces(sweepFeature, pathlenth / 2.0)
            End If

        End Sub

        Private Sub GenerateMidsurfaceFromLoft(ByRef loftFeature As Inventor.LoftFeature)

            Dim oCompDef As PartComponentDefinition
            oCompDef = m_partDoc.ComponentDefinition()

            Dim loftSections As ObjectCollection = loftFeature.Definition.Sections
            Dim midSections As ObjectCollection = _invApp.TransientObjects.CreateObjectCollection

            For Each secObj In loftSections
                If TypeOf secObj Is Inventor.Profile Then
                    Dim profile As Inventor.Profile = secObj
                    Dim midcurves As List(Of BeyazitTest.Vertices) = GenerateMidcurveFromProfile(profile)

                    ' utilize same sketch in SHARED mode, no need to extract its params and create a duplicate copy
                    Dim profileSketch As PlanarSketch
                    profileSketch = profile.Parent 'oCompDef.Sketches.Add(oCompDef.WorkPlanes(3))
                    profileSketch.Shared = True

                    Dim oProfiles As ObjectCollection = GenerateNewProfilesFromMidcurves(profileSketch, midcurves)
                    For Each midprofile In oProfiles
                        midSections.Add(midprofile)
                    Next
                    ' Make the Shared Sketch invisible
                    profileSketch.Visible = False

                End If

            Next

            ' Create the loft definition. Because one of the ends isn't planar,
            ' a surface must be created instead of a solid.
            Dim oLoftDefinition As LoftDefinition = oCompDef.Features.LoftFeatures.CreateLoftDefinition(midSections, PartFeatureOperationEnum.kSurfaceOperation)

            ' Create the loft feature.
            oCompDef.Features.LoftFeatures.Add(oLoftDefinition)


            'For Each oProfileOne In midSections
            '    Try
            '        ' Create Surface Sweep Feature
            '        Dim oSweepOne As SweepFeature
            '        oSweepOne = oCompDef.Features.SweepFeatures.AddUsingPath(oProfileOne, path, PartFeatureOperationEnum.kSurfaceOperation, SweepProfileOrientationEnum.kNormalToPath)
            '    Catch ex2 As Exception
            '        MsgBox(ex2.Message())
            '    End Try
            'Next




        End Sub

        Private Function GenerateMidsurfaceFromFaceFeature(ByRef faceFeature As Inventor.FaceFeature) As SurfaceBody

            Dim dir As PartFeatureExtentDirectionEnum = PartFeatureExtentDirectionEnum.kPositiveExtentDirection

            GenerateMidsurfaceFromFaceFeature = Nothing
            dir = faceFeature.Definition.Direction
            Dim oCompDef As SheetMetalComponentDefinition = faceFeature.Parent

            Dim thickness As Double = oCompDef.Thickness.Value
            Dim oOffsetFeature As ThickenFeature

            If faceFeature.Faces Is Nothing Then
                Exit Function
            End If

            Dim oFaceColl As FaceCollection = _invApp.TransientObjects.CreateFaceCollection

            If faceFeature.Faces.Count > 0 Then
                Dim largestface As Inventor.Face = faceFeature.Faces.Item(1) ' some decent initialization, lets refine it now
                For Each fc As Inventor.Face In faceFeature.Faces
                    If fc.Evaluator.Area > largestface.Evaluator.Area Then
                        largestface = fc
                    End If
                Next
                oFaceColl.Add(largestface)
            End If

            oOffsetFeature = oCompDef.Features.ThickenFeatures.Add(oFaceColl, -1 * thickness / 2, dir, PartFeatureOperationEnum.kSurfaceOperation)

            GenerateMidsurfaceFromFaceFeature = oOffsetFeature.SurfaceBodies.Item(1)

        End Function

        Private Function GenerateMidsurfaceFromBendFeature(ByRef bendFeature As Inventor.BendFeature) As SurfaceBody

            Dim dir As PartFeatureExtentDirectionEnum = PartFeatureExtentDirectionEnum.kPositiveExtentDirection

            GenerateMidsurfaceFromBendFeature = Nothing
            Dim oCompDef As SheetMetalComponentDefinition = bendFeature.Parent
            Dim oOffsetFeature As ThickenFeature
            If bendFeature.Faces Is Nothing Then
                Exit Function
            End If
            Dim oFaceColl As FaceCollection = _invApp.TransientObjects.CreateFaceCollection
            Dim thickness As Double = oCompDef.Thickness.Value
            If bendFeature.Faces.Count > 0 Then
                Dim largestface As Inventor.Face = bendFeature.Faces.Item(1) ' some decent initialization, lets refine it now
                For Each fc As Inventor.Face In bendFeature.Faces
                    If fc.Evaluator.Area > largestface.Evaluator.Area Then
                        largestface = fc
                    End If
                Next
                oFaceColl.Add(largestface)
            End If

            oOffsetFeature = oCompDef.Features.ThickenFeatures.Add(oFaceColl, -1 * thickness / 2, dir, PartFeatureOperationEnum.kSurfaceOperation)

            GenerateMidsurfaceFromBendFeature = oOffsetFeature.SurfaceBodies.Item(1)

        End Function

        Private Function GenerateMidsurfaceFromFlangeFeature(ByRef flangeFeature As Inventor.FlangeFeature) As SurfaceBody

            Dim dir As PartFeatureExtentDirectionEnum = PartFeatureExtentDirectionEnum.kPositiveExtentDirection

            GenerateMidsurfaceFromFlangeFeature = Nothing

            Dim oCompDef As SheetMetalComponentDefinition = flangeFeature.Parent

            If flangeFeature.Faces Is Nothing Then
                Exit Function
            End If

            Dim oFaceColl As FaceCollection = _invApp.TransientObjects.CreateFaceCollection
            If flangeFeature.Faces.Count > 0 Then
                Dim largestface As Inventor.Face = flangeFeature.Faces.Item(1) ' some decent initialization, lets refine it now
                For Each fc As Inventor.Face In flangeFeature.Faces
                    If fc.Evaluator.Area > largestface.Evaluator.Area Then
                        largestface = fc
                    End If
                Next
                oFaceColl.Add(largestface)
                ' find tangentially connected faces to this, which are part of the same feature
                Dim connectedFaces As ObjectCollection = largestface.TangentiallyConnectedFaces
                For Each cfc As Inventor.Face In connectedFaces
                    If cfc.CreatedByFeature().Name = flangeFeature.Name Then
                        oFaceColl.Add(cfc)
                    End If

                Next

            End If
            'oFaceColl.Add(flangeFeature.Faces.Item(1))
            ''FaceColl.Add(flangeFeature.Faces.Item(9))

            Dim thickness As Double = oCompDef.Thickness.Value
            Dim oOffsetFeature As ThickenFeature
            'oOffsetFeature = oCompDef.Features.ThickenFeatures.Add(oFaceColl, -1 * thickness / 2, dir, PartFeatureOperationEnum.kSurfaceOperation, True, False, False)
            oOffsetFeature = oCompDef.Features.ThickenFeatures.Add(oFaceColl, -1 * thickness / 2, dir, PartFeatureOperationEnum.kSurfaceOperation, False, False, True) ' Automatic chaining is causing whole part to be chained for offset

            GenerateMidsurfaceFromFlangeFeature = oOffsetFeature.SurfaceBodies.Item(1)


        End Function

        Private Function GenerateMidsurfaceFromContourFlangeFeature(ByRef cflangeFeature As Inventor.ContourFlangeFeature) As SurfaceBody

            Dim dir As PartFeatureExtentDirectionEnum = PartFeatureExtentDirectionEnum.kPositiveExtentDirection

            GenerateMidsurfaceFromContourFlangeFeature = Nothing

            Dim oCompDef As SheetMetalComponentDefinition = cflangeFeature.Parent

            Dim oFaceColl As FaceCollection = _invApp.TransientObjects.CreateFaceCollection
            'Dim numPathCurves As Integer = cflangeFeature.Definition.Path.Count
            'For i = 1 To numPathCurves - 1
            '    oFaceColl.Add(cflangeFeature.Faces.Item(i))
            'Next
            oFaceColl.Add(cflangeFeature.Faces.Item(2))

            Dim thickness As Double = oCompDef.Thickness.Value
            Dim oOffsetFeature As ThickenFeature
            oOffsetFeature = oCompDef.Features.ThickenFeatures.Add(oFaceColl, -1 * thickness / 2, dir, PartFeatureOperationEnum.kSurfaceOperation, False, False, False)

            GenerateMidsurfaceFromContourFlangeFeature = oOffsetFeature.SurfaceBodies.Item(1)


        End Function

        Public Function GenerateMidsurfacePerFeature(ByRef oFeature As PartFeature) As SurfaceBody

            Dim midsurfBody As SurfaceBody = Nothing

            If oFeature.Suppressed Then
                Debug.Print(oFeature.Name + " : Suppressed, not processing")
                GenerateMidsurfacePerFeature = Nothing
                Exit Function
            End If

            If TypeOf oFeature Is ExtrudeFeature Then

                Dim extrudeDef As ExtrudeDefinition
                extrudeDef = oFeature.Definition
                Dim oper As PartFeatureOperationEnum = extrudeDef.Operation

                Select Case oper
                    Case PartFeatureOperationEnum.kNewBodyOperation
                        Debug.Print(oFeature.Name + " : New Body")
                        midsurfBody = GenerateMidsurfaceFromExtrude(oFeature)
                    Case PartFeatureOperationEnum.kCutOperation
                        Debug.Print(oFeature.Name + " : Cut Operation (not Implemented)")
                        ' dont compute Misurface of oFeature, but just get the tool body can cut the Midsurface
                    Case PartFeatureOperationEnum.kJoinOperation
                        midsurfBody = GenerateMidsurfaceFromExtrude(oFeature)
                        Debug.Print(oFeature.Name + " : Join Operation (not Implemented, doing New Body)")
                        'ExtendTrim(existingMidsurf, featMidsurf)
                End Select

            ElseIf TypeOf oFeature Is RevolveFeature Then
                Debug.Print(oFeature.Name + " : Processing Revolve")
                Dim revFeature As RevolveFeature = oFeature
                If TypeOf revFeature.Extent Is AngleExtent Then
                    GenerateMidsurfaceFromRevolveByAngle(revFeature)
                ElseIf TypeOf revFeature.Extent Is FromToExtent Then
                    Debug.Print(oFeature.Name + " : FromToExtent Revolve not implemented")
                ElseIf TypeOf revFeature.Extent Is FullSweepExtent Then
                    Debug.Print(oFeature.Name + " : FullSweepExtent Revolve not implemented")
                ElseIf TypeOf revFeature.Extent Is ToExtent Then
                    GenerateMidsurfaceFromRevolveToNext(revFeature)
                ElseIf TypeOf revFeature.Extent Is ToNextExtent Then
                    Debug.Print(oFeature.Name + " : ToNextExtent Revolve not implemented")
                Else
                    Debug.Print(oFeature.Name + " : UNKNOWN Revolve not implemented")
                End If


            ElseIf TypeOf oFeature Is SweepFeature Then
                Debug.Print(oFeature.Name + " : Processing Sweep")
                GenerateMidsurfaceFromSweep(oFeature)

            ElseIf TypeOf oFeature Is LoftFeature Then
                Debug.Print(oFeature.Name + " : Processing Loft")
                GenerateMidsurfaceFromLoft(oFeature)

            ElseIf TypeOf oFeature Is FaceFeature Then
                Debug.Print(oFeature.Name + " : Processing Face")
                GenerateMidsurfaceFromFaceFeature(oFeature)

            ElseIf TypeOf oFeature Is BendFeature Then
                Debug.Print(oFeature.Name + " : Processing Bend")
                GenerateMidsurfaceFromBendFeature(oFeature)

            ElseIf TypeOf oFeature Is FlangeFeature Then
                Debug.Print(oFeature.Name + " : Processing Flange")
                GenerateMidsurfaceFromFlangeFeature(oFeature)

            ElseIf TypeOf oFeature Is ContourFlangeFeature Then
                Debug.Print(oFeature.Name + " : Processing Contour Flange")
                GenerateMidsurfaceFromContourFlangeFeature(oFeature)

            Else
                Debug.Print(oFeature.Name + " : Processing Not implemented")
            End If

            GenerateMidsurfacePerFeature = midsurfBody

        End Function

        Public Function GenerateMidsurfaceExtension(ByRef oProfileOne As Profile, ByVal profileSideExtension As Double) As SurfaceBody
            Dim oCompDef As PartComponentDefinition
            oCompDef = m_partDoc.ComponentDefinition()

            Dim midsurfBody As SurfaceBody = Nothing
            ' TILL WE GET ASYMMETRIC EXTRUDE working, will create a new one
            If Not oProfileOne Is Nothing & profileSideExtension > 0.00001 Then
                Dim oExtrudeDef2 As ExtrudeDefinition
                oExtrudeDef2 = oCompDef.Features.ExtrudeFeatures.CreateExtrudeDefinition(oProfileOne, PartFeatureOperationEnum.kSurfaceOperation)
                oExtrudeDef2.SetDistanceExtent(profileSideExtension, PartFeatureExtentDirectionEnum.kNegativeExtentDirection)
                Dim oExtrudeOne2 As ExtrudeFeature
                oExtrudeOne2 = oCompDef.Features.ExtrudeFeatures.Add(oExtrudeDef2)
            End If

            GenerateMidsurfaceExtension = midsurfBody
        End Function

        Public Function GenerateMidsurfaceExtension(ByRef oProfileOne As Profile, ByRef wp As WorkPoint) As SurfaceBody
            Dim oCompDef As PartComponentDefinition
            oCompDef = m_partDoc.ComponentDefinition()

            Dim midsurfBody As SurfaceBody = Nothing

            If Not oProfileOne Is Nothing & Not wp Is Nothing Then

                On Error Resume Next
                Dim oExtrudeDef2 As ExtrudeDefinition
                oExtrudeDef2 = oCompDef.Features.ExtrudeFeatures.CreateExtrudeDefinition(oProfileOne, PartFeatureOperationEnum.kSurfaceOperation)
                oExtrudeDef2.SetToExtent(wp)
                Dim oExtrudeOne2 As ExtrudeFeature
                oExtrudeOne2 = oCompDef.Features.ExtrudeFeatures.Add(oExtrudeDef2)
                If Err.Number <> 0 Then
                    'MsgBox("Could not create Extrude extension.")
                End If
            End If

            GenerateMidsurfaceExtension = midsurfBody
        End Function

        'Main driver function. Per feature Midsurface creation
        Public Function GenerateMidsurface() As ObjectCollection

            GenerateMidsurface = Nothing
            Dim midsurfaces As ObjectCollection = _invApp.TransientObjects.CreateObjectCollection

            Dim sFeatures As Inventor.PartFeatures
            sFeatures = _invApp.ActiveDocument.ComponentDefinition.Features

            Dim oFeature As PartFeature

            For Each oFeature In sFeatures
                If Not oFeature.SurfaceBodies Is Nothing Then
                    If oFeature.SurfaceBodies.Count > 0 Then
                        If oFeature.SurfaceBodies.Item(1).Visible Then
                            If Not oFeature.Suppressed Then
                                Dim midsurf As SurfaceBody = Nothing
                                midsurf = GenerateMidsurfacePerFeature(oFeature)
                                If Not midsurf Is Nothing Then
                                    midsurfaces.Add(midsurf)
                                End If
                            End If
                        End If
                    End If
                End If
            Next

            ' Make Solid bodies invisible
            For Each body As SurfaceBody In _invApp.ActiveDocument.ComponentDefinition.SurfaceBodies
                If body.IsSolid Then
                    body.Visible = False
                End If
            Next
            GenerateMidsurface = midsurfaces
        End Function

        Private Sub CreateMidurfByOffsettingSweepfaces(sweepFeature As SweepFeature, ByVal offsetdist As Double, Optional ByVal facechain As Boolean = False)

            Dim oCompDef As PartComponentDefinition
            oCompDef = m_partDoc.ComponentDefinition()
            Dim dir As PartFeatureExtentDirectionEnum = PartFeatureExtentDirectionEnum.kNegativeExtentDirection

            ' Big profile, so just offset
            Dim oFaceColl As FaceCollection
            oFaceColl = _invApp.TransientObjects.CreateFaceCollection

            oFaceColl.Add(m_Utilities.GetTheLargestFace(sweepFeature.Faces))

            'For Each oFace In sweepFeature.Faces
            '    ' add only if its not part of either of Start/End/Side faces
            '    If (Not ContainsInFaces(sweepFeature.SideFaces, oFace)) And (Not ContainsInFaces(sweepFeature.EndFaces, oFace)) And (Not ContainsInFaces(sweepFeature.StartFaces, oFace)) Then
            '        oFaceColl.Add(oFace)
            '    End If
            'Next

            If oFaceColl.Count < 1 Then
                Exit Sub
            End If

            ' Offset the base face 
            Dim oOffsetFeature As ThickenFeature
            oOffsetFeature = oCompDef.Features.ThickenFeatures.Add(oFaceColl, offsetdist, dir, PartFeatureOperationEnum.kSurfaceOperation, facechain, False, True)

            'Dim bodyCollection As ObjectCollection
            'bodyCollection = _invApp.TransientObjects.CreateObjectCollection

            'bodyCollection.Add(oOffsetFeature.SurfaceBodies.Item(1))

            'Dim oMoveDef As MoveDefinition
            'oMoveDef = oCompDef.Features.MoveFeatures.CreateMoveDefinition(bodyCollection)
            '' MOVE ALONG PATH??
            ''oMoveDef.AddRotateAboutAxis(oCompDef.WorkAxes.Item(2), False, pathLenght / 2) ' DEBUG 'axis'

            'Dim oMoveFeature As MoveFeature
            'oMoveFeature = oCompDef.Features.MoveFeatures.Add(oMoveDef)
        End Sub

        'Private Function GetSketchPoint(ByRef oSketch As PlanarSketch, ByRef point As Inventor.Point2d) As SketchPoint
        '    GetSketchPoint = Nothing

        '    ' DONT send re-used points
        '    'If oSketch.SketchPoints.Count > 0 Then
        '    '    For i As Integer = 1 To oSketch.SketchPoints.Count
        '    '        Dim skPt As SketchPoint = oSketch.SketchPoints.Item(i)
        '    '        If skPt.Geometry.X = point.X And skPt.Geometry.Y = point.Y Then
        '    '            GetSketchPoint = skPt
        '    '            Exit Function
        '    '        End If
        '    '    Next
        '    'End If

        '    ' create new
        '    GetSketchPoint = oSketch.SketchPoints.Add(point)
        'End Function

        'Private Function GetNextOrphanSketchEntity(oSketch As PlanarSketch) As SketchLine
        '    GetNextOrphanSketchEntity = Nothing

        '    'Dim usedLinesCollection As ObjectCollection
        '    'usedLinesCollection = _invApp.TransientObjects.CreateObjectCollection

        '    '' Iterate over all SketchEntities, see if they belong to any Profile, if not return first
        '    'For Each pro As Profile In oSketch.Profiles
        '    '    For Each path As ProfilePath In pro
        '    '        'If path.AddsMaterial = False Then ' only non solids
        '    '        For Each line As ProfileEntity In path
        '    '            If line.CurveType = Curve2dTypeEnum.kLineSegmentCurve2d Then
        '    '                usedLinesCollection.Add(line.Curve)
        '    '            End If
        '    '        Next
        '    '        'End If
        '    '    Next
        '    'Next

        '    'Dim isPresent As Boolean = False
        '    'For Each skent As SketchLine In oSketch.SketchLines
        '    '    For Each ob As Object In usedLinesCollection
        '    '        Dim existingSketchEntity As SketchEntity = ob
        '    '        If SketchEntity.ReferenceEquals(existingSketchEntity, skent) Then
        '    '            isPresent = True
        '    '        End If
        '    '    Next
        '    '    If isPresent = False Then
        '    '        GetNextOrphanSketchEntity = skent
        '    '        Exit For
        '    '    End If

        '    'Next

        'End Function
        'Private Function findDistanceToOppositeFace(ByRef face As Inventor.Face, ByRef feat As PartFeature) As Double

        '    findDistanceToOppositeFace = 0.0
        '    Dim isFlipped As Boolean = False

        '    Dim origin As Inventor.Point = face.PointOnFace

        '    Dim pt(2) As Double
        '    Dim n(2) As Double

        '    pt(0) = origin.X : pt(1) = origin.Y : pt(2) = origin.Z

        '    face.Evaluator.GetNormalAtPoint(pt, n)

        '    Dim normal As Inventor.UnitVector = _invApp.TransientGeometry.CreateUnitVector(n(0), n(1), n(2))
        '    Dim flipnormal As Inventor.UnitVector = _invApp.TransientGeometry.CreateUnitVector(-n(0), -n(1), -n(2))

        '    Dim body As SurfaceBody = feat.SurfaceBodies.Item(1)
        '    Dim radius As Double = Math.Sqrt(face.Evaluator.Area) * 2.0

        '    Dim objects As ObjectsEnumerator
        '    Dim pts As ObjectsEnumerator
        '    Dim objtypes(0 To 1) As SelectionFilterEnum

        '    objtypes(1) = SelectionFilterEnum.kPartFaceFilter

        '    On Error Resume Next
        '    body.FindUsingRay(origin, normal, radius, objects, pts, True)
        '    'objects = m_partDoc.ComponentDefinition().FindUsingVector(origin, normal, objtypes)
        '    If Err.Number <> 0 Then
        '        'MsgBox("Could not create ThickenFeature.")
        '    End If
        '    If objects Is Nothing Then
        '        body.FindUsingRay(origin, flipnormal, radius, objects, pts, True)
        '        'objects = m_partDoc.ComponentDefinition().FindUsingVector(origin, flipnormal, objtypes)
        '        isFlipped = True
        '    End If

        '    If objects.Count > 0 Then
        '        Dim minLen As Double = 100000000
        '        For index As Integer = 1 To objects.Count
        '            Dim point As Inventor.Point = pts.Item(index)
        '            'm_partDoc.ComponentDefinition().WorkPoints.AddFixed(point) ' DEBUG
        '            'Dim length As Double = _invApp.MeasureTools.GetMinimumDistance(origin, objects.Item(index))

        '            '' IMP INSTEAD OF OBJECT find distance between POINTS
        '            Dim length As Double = _invApp.MeasureTools.GetMinimumDistance(origin, point)
        '            If length > 0.0 And length < minLen Then
        '                minLen = length
        '            End If
        '        Next

        '        If isFlipped Then
        '            findDistanceToOppositeFace = -1 * minLen
        '        Else
        '            findDistanceToOppositeFace = minLen
        '        End If
        '    End If

        'End Function

        'Public Sub TestFindDistance()
        '    Dim planeFace As Face
        '    planeFace = _invApp.CommandManager.Pick(SelectionFilterEnum.kPartFacePlanarFilter, "Pick a planar face.")
        '    Dim dist As Double
        '    dist = m_Utilities.findDistanceToOppositeFace(planeFace)
        '    'MsgBox("Distance: " & dist)
        'End Sub
        'Private Function findDistanceToOppositeFace(ByRef face As Inventor.Face) As Double
        '    findDistanceToOppositeFace = 0
        '    Dim isFlipped As Boolean = False
        '    Dim origin As Inventor.Point
        '    origin = face.PointOnFace
        '    Dim pt(2) As Double
        '    pt(0) = origin.X : pt(1) = origin.Y : pt(2) = origin.Z ' Get the normal of the face and create a vector in the reverse direction ' because the face normal points out of the solid. 
        '    Dim n(2) As Double
        '    Call face.Evaluator.GetNormalAtPoint(pt, n)
        '    Dim normal As Inventor.UnitVector
        '    normal = _invApp.TransientGeometry.CreateUnitVector(-n(0), -n(1), -n(2)) ' Get the parent body. 
        '    Dim flipnormal As Inventor.UnitVector = _invApp.TransientGeometry.CreateUnitVector(n(0), n(1), n(2))

        '    Dim body As SurfaceBody
        '    body = face.Parent ' Find all faces intersected by a ray. 
        '    Dim objects As ObjectsEnumerator
        '    Dim pts As ObjectsEnumerator
        '    On Error Resume Next
        '    Call body.FindUsingRay(origin, normal, 0.001, objects, pts, True)
        '    If Err.Number <> 0 Then
        '        'MsgBox("Could not create ThickenFeature.")
        '    End If
        '    If objects Is Nothing Then
        '        body.FindUsingRay(origin, flipnormal, 0.001, objects, pts, True)
        '        'objects = m_partDoc.ComponentDefinition().FindUsingVector(origin, flipnormal, objtypes)
        '        isFlipped = True
        '    End If

        '    If objects.Count > 0 Then
        '        Dim minLen As Double = 100000000
        '        For index As Integer = 1 To objects.Count
        '            Dim point As Inventor.Point = pts.Item(index)
        '            'm_partDoc.ComponentDefinition().WorkPoints.AddFixed(point) ' DEBUG
        '            'Dim length As Double = _invApp.MeasureTools.GetMinimumDistance(origin, objects.Item(index))

        '            '' IMP INSTEAD OF OBJECT find distance between POINTS
        '            Dim length As Double = _invApp.MeasureTools.GetMinimumDistance(origin, point)
        '            If length > 0.0 And length < minLen Then
        '                minLen = length
        '            End If
        '        Next

        '        If isFlipped Then
        '            findDistanceToOppositeFace = -1 * minLen
        '        Else
        '            findDistanceToOppositeFace = minLen
        '        End If
        '    End If
        '    '' Calculate the distance using the second face because the first one will 
        '    '' be the original input face. 
        '    'findDistanceToOppositeFace = _invApp.MeasureTools.GetMinimumDistance(origin, objects.Item(2))
        'End Function
        'Private Function GetLengthOfPath(ByRef path As Inventor.Path, ByRef profile As Inventor.Profile, ByRef oCompDef As PartComponentDefinition) As Double

        '    ' Get the centroid of the sweep profile in sketch space
        '    Dim oProfileOrigin As Point2d
        '    oProfileOrigin = profile.RegionProperties.Centroid

        '    ' Transform the centroid from sketch space to model space
        '    Dim oProfileOrigin3D As Point
        '    oProfileOrigin3D = profile.Parent.SketchToModelSpace(oProfileOrigin)

        '    Dim TotalLength As Double
        '    TotalLength = 0

        '    Try
        '        ' Get the set of curves that represent the true path of the sweep
        '        Dim oCurves As ObjectsEnumerator
        '        oCurves = oCompDef.Features.SweepFeatures.GetTruePath(path, oProfileOrigin3D)
        '        Dim oCurve As Object
        '        For Each oCurve In oCurves

        '            Dim oCurveEval As CurveEvaluator
        '            oCurveEval = oCurve.Evaluator

        '            Dim MinParam As Double
        '            Dim MaxParam As Double
        '            Dim Length As Double

        '            Call oCurveEval.GetParamExtents(MinParam, MaxParam)
        '            Call oCurveEval.GetLengthAtParam(MinParam, MaxParam, Length)

        '            TotalLength = TotalLength + Length
        '        Next
        '    Catch ex As Exception
        '        For Each pathent As PathEntity In path
        '            Dim oCurveEval As CurveEvaluator = pathent.Curve.Evaluator

        '            Dim MinParam As Double
        '            Dim MaxParam As Double
        '            Dim Length As Double

        '            Call oCurveEval.GetParamExtents(MinParam, MaxParam)
        '            Call oCurveEval.GetLengthAtParam(MinParam, MaxParam, Length)

        '            TotalLength = TotalLength + Length
        '        Next
        '    End Try
        '    GetLengthOfPath = TotalLength
        'End Function

        'Private Function GetWorkPlane(planeorig As Object) As WorkPlane
        '    Dim oCompDef As PartComponentDefinition
        '    oCompDef = m_partDoc.ComponentDefinition()

        '    GetWorkPlane = Nothing
        '    If TypeOf planeorig Is Inventor.Face Then
        '        Dim fc As Face = planeorig
        '        Dim pt1 As Inventor.Point = fc.Vertices.Item(1).Point
        '        Dim pt2 As Inventor.Point = fc.Vertices.Item(2).Point
        '        Dim pt3 As Inventor.Point = fc.Vertices.Item(3).Point
        '        Dim wpt1 As WorkPoint = oCompDef.WorkPoints.AddFixed(pt1, True)
        '        Dim wpt2 As WorkPoint = oCompDef.WorkPoints.AddFixed(pt2, True)
        '        Dim wpt3 As WorkPoint = oCompDef.WorkPoints.AddFixed(pt3, True)
        '        'Dim pt As Point = fc.PointOnFace
        '        'Dim vec As UnitVector = GetFaceNormal(fc)
        '        'Dim pln As Plane = _invApp.TransientGeometry.CreatePlane(pt, vec.AsVector)
        '        GetWorkPlane = oCompDef.WorkPlanes.AddByThreePoints(wpt1, wpt2, wpt3, True)
        '    ElseIf TypeOf planeorig Is WorkPlane Then
        '        GetWorkPlane = oCompDef.WorkPlanes.AddByPlaneAndOffset(planeorig, 0.0, True)
        '    End If
        'End Function

        'Private Function CreateNewSketch(faceSketch As PlanarSketch, Optional copyContents As Boolean = False) As PlanarSketch
        '    CreateNewSketch = Nothing

        '    Dim newsketch As PlanarSketch = m_partDoc.ComponentDefinition().Sketches.Add(faceSketch.PlanarEntity)

        '    If copyContents Then
        '        faceSketch.CopyContentsTo(newsketch)
        '    End If

        '    If Not faceSketch.OriginPoint Is Nothing Then
        '        newsketch.OriginPoint = faceSketch.OriginPoint
        '    End If

        '    CreateNewSketch = newsketch
        'End Function

    End Class

End Namespace
