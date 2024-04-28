Imports System
Imports System.Type
Imports System.Activator
Imports System.Runtime.InteropServices
Imports Inventor
Imports BeyazitTest
Imports BeyazitTest.Vertices
Imports System.Windows.Vector
Imports System.IO


Public Class Form1


    ' App variables.
    Dim _invApp As Inventor.Application
    Private m_partDoc As PartDocument
    Dim _started As Boolean = False
    Dim _initialized As Boolean = False

    Private m_PolyLines As New List(Of Polygon)()
    Private m_InputPolygonVertices As New BeyazitTest.Vertices
    Private m_InputPolygon As Polygon

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

        ' Get a reference to the active part.
        m_partDoc = _invApp.ActiveDocument

        Init = True
    End Function

    Private Sub Form1_FormClosed(sender As Object, e As System.Windows.Forms.FormClosedEventArgs) Handles Me.FormClosed

        If _started Then
            _invApp.Quit()
        End If

        _invApp = Nothing
    End Sub

    ' Allocate the first Bitmap.
    Private Sub Form1_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load

        Me.ResizeRedraw = True

    End Sub


    Private Sub ExtractSketchBtn_Click(sender As System.Object, e As System.EventArgs) Handles ExtractSketchBtn.Click

        ' set active part
        If _initialized = False Then
            _initialized = Init()
        End If

        If _initialized = False Then
            Exit Sub
        End If

        'find first extrude feature
        Dim extrudes As Inventor.ExtrudeFeatures
        extrudes = m_partDoc.ComponentDefinition.Features.ExtrudeFeatures

        If extrudes.Count > 0 Then

            Dim extFeature As Inventor.ExtrudeFeature = extrudes.Item(1) ' YOGESH: Should go thru ALL extrudes not just FIRST

            If Not extFeature.Profile Is Nothing Then

                Dim pathIndex As Integer = 0

                For Each path As Inventor.ProfilePath In extFeature.Profile

                    'YOGESH: path.Count is 0 for profile created by TEXT command. Not yet implemeneted by Inventor APIs (wishlist)
                    If Not path Is Nothing And path.Count > 0 Then

                        Dim pathVertices As BeyazitTest.Vertices = New BeyazitTest.Vertices ' these are for this individual profile-path, outer or inner

                        'YOGESH: Its assumed that curves in the path are connected end-to-end, if not following logic wont work
                        For Each profile_entity As Inventor.ProfileEntity In path

                            Dim entity As SketchEntity = profile_entity.SketchEntity
                            Dim singleEntityVertices As BeyazitTest.Vertices = New BeyazitTest.Vertices ' these are just for this individual curves

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
                                Dim segmentCount As Integer = 12 ' Adjust to resolution needed

                                Dim offset As Double
                                offset = length / segmentCount

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

                            ' Individual entities may be connected in 'reverse' directions, correct it
                            If pathVertices.Index(singleEntityVertices(singleEntityVertices.Count - 1)) = 0 Then
                                pathVertices.Reverse()
                                singleEntityVertices.Reverse()
                            ElseIf pathVertices.Index(singleEntityVertices(singleEntityVertices.Count - 1)) = 1 Then
                                singleEntityVertices.Reverse()
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
                        If extFeature.Profile.Count > 1 Then
                            If pathIndex = 0 Then ' first profile should be CCW
                                pathVertices.Add(pathVertices.Vertex(0))
                                pathVertices.ForceCounterClockWise()
                            Else
                                If Not pathVertices.IsCounterClockWise() Then
                                    m_InputPolygonVertices.Add(pathVertices.Vertex(pathVertices.Count - 1))
                                Else
                                    pathVertices.Add(pathVertices.Vertex(0))
                                    pathVertices.ForceClockWise() ' make it clockwise!!!!!!!!!!!!!
                                End If
                            End If
                            For Each vp As System.Windows.Vector In pathVertices
                                m_InputPolygonVertices.Add(vp)
                            Next
                        Else ' Single path, no holes
                            pathVertices.ForceCounterClockWise()
                            For Each vp As System.Windows.Vector In pathVertices
                                m_InputPolygonVertices.Add(vp)
                            Next
                        End If

                    End If
                    pathIndex = pathIndex + 1
                Next

                ' DEBUG
                Dim myDebug As Boolean = True
                If myDebug = True And m_InputPolygonVertices.Count > 0 Then
                    Dim w As StreamWriter = New StreamWriter("my.dat")
                    For Each v As System.Windows.Vector In m_InputPolygonVertices
                        w.WriteLine(String.Format("{0}   {1}", v.X, v.Y))
                    Next
                    w.Close()
                End If

                ' All profile curves are done now, fill points list for display
                Dim ii As Integer = 0
                Dim ppoints(m_InputPolygonVertices.Count - 1) As PointF
                 For Each v As System.Windows.Vector In m_InputPolygonVertices
                    ppoints(ii) = New PointF(v.X, v.Y)
                    ii = ii + 1
                Next
                m_InputPolygon = New Polygon(ppoints)

            End If
        End If

        Me.Invalidate()

    End Sub

    Private Sub Form1_Paint(ByVal sender As Object, ByVal e As System.Windows.Forms.PaintEventArgs) Handles Me.Paint

        e.Graphics.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.AntiAlias

        e.Graphics.Clear(Me.BackColor)
        e.Graphics.ResetTransform()
        e.Graphics.ScaleTransform(0.5, 0.5, System.Drawing.Drawing2D.MatrixOrder.Append)

        If (Not (m_InputPolygon Is Nothing)) Then
            m_InputPolygon.Draw(e.Graphics, System.Drawing.Pens.Blue)
        End If

        For Each lines As Polygon In m_PolyLines
            lines.Draw(e.Graphics, System.Drawing.Pens.Red)
        Next lines
    End Sub

    ' Map a drawing coordinate rectangle to a graphics object rectangle.
    Private Sub MapDrawing(ByVal gr As Graphics, ByVal _
        drawing_rect As RectangleF, ByVal target_rect As  _
        RectangleF, Optional ByVal stretch As Boolean = False)
        gr.ResetTransform()

        ' Center the drawing area at the origin.
        Dim drawing_cx As Single = (drawing_rect.Left + _
            drawing_rect.Right) / 2
        Dim drawing_cy As Single = (drawing_rect.Top + _
            drawing_rect.Bottom) / 2
        gr.TranslateTransform(-drawing_cx, -drawing_cy)

        ' Scale.
        ' Get scale factors for both directions.
        Dim scale_x As Single = target_rect.Width / _
            drawing_rect.Width
        Dim scale_y As Single = target_rect.Height / _
            drawing_rect.Height
        If (Not stretch) Then
            ' To preserve the aspect ratio, use the smaller
            ' scale factor.
            scale_x = Math.Min(scale_x, scale_y)
            scale_y = scale_x
        End If
        gr.ScaleTransform(scale_x, scale_y, _
            System.Drawing.Drawing2D.MatrixOrder.Append)

        ' Translate to center over the drawing area.
        Dim graphics_cx As Single = (target_rect.Left + _
            target_rect.Right) / 2
        Dim graphics_cy As Single = (target_rect.Top + _
            target_rect.Bottom) / 2
        gr.TranslateTransform(graphics_cx, graphics_cy, _
            System.Drawing.Drawing2D.MatrixOrder.Append)
    End Sub


    Private Sub MidcurvesBtn_Click(sender As System.Object, e As System.EventArgs) Handles MidcurvesBtn.Click

        Dim resultsWithTriangulation As List(Of BeyazitTest.Vertices)
        resultsWithTriangulation = YogeshBayazitDecomposer.ConvexPartition(m_InputPolygonVertices)

        'Dim polygonList As List(Of BeyazitTest.Vertices)
        'polygonList = Triangulator.TriagnulateQuadPlusPolygons(resultsWithTriangulation)

        Dim midcurves As List(Of BeyazitTest.Vertices)
        midcurves = MidcurveGenerator.GenerateMidcurves(resultsWithTriangulation)

        For ii As Integer = 0 To midcurves.Count - 1
            Dim vertices As BeyazitTest.Vertices = midcurves(ii)

            Dim iipoints(1) As PointF
            Dim v1 As System.Windows.Vector = vertices.Vertex(0)
            Dim v2 As System.Windows.Vector = vertices.Vertex(1)
            iipoints(0) = New PointF(v1.X, v1.Y)
            iipoints(1) = New PointF(v2.X, v2.Y)

            Dim line As Polygon = New Polygon(iipoints)
            m_PolyLines.Add(line)
        Next


        Me.Invalidate()

    End Sub
End Class
