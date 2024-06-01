Module Geometry

    Public Class Triangle
        Public Points(2) As PointF
        Public Sub New(ByVal p0 As PointF, ByVal p1 As PointF, ByVal p2 As PointF)
            Points(0) = p0
            Points(1) = p1
            Points(2) = p2
        End Sub
    End Class

    Public Class Polygon

        Private m_Points As New List(Of PointF)

        Private m_Centroid As PointF

        Const PT_RAD As Integer = 2
        Const PT_WID As Integer = PT_RAD * 2 + 1

        ' NOT FOR PUBLIC, without Points array
        Private Sub New()
        End Sub

        Public Sub New(Points As PointF())
            Me.SetAll(Points)
        End Sub

        Public Function Count() As Integer
            Return m_Points.Count
        End Function

        Public Function PointAt(i As Integer) As PointF
            Return m_Points.Item(i)
        End Function

        Public Function Clone() As Polygon

            'Create a new polygon using the blank constructor
            Dim TestPoly As New Polygon

            'Call the TestPoly.setall sub
            'Feed all of this instance's properties inot the Testpoly.SetAll's sub
            TestPoly.SetAll(Me.m_Points.ToArray)

            'Return the copied polygon object
            Return TestPoly

        End Function

        Private Sub SetAll(Points As PointF())

            Me.m_Points.Clear()

            For I As Integer = 0 To Points.Count - 1
                Me.m_Points.Add(Points(I))
            Next

        End Sub

        Private Sub DrawPoint(gr As Graphics, brush As System.Drawing.Brush, pt As PointF)
            gr.FillRectangle(brush, pt.X - PT_RAD, pt.Y - PT_RAD, PT_WID, PT_WID)
            gr.DrawRectangle(Pens.Black, pt.X - PT_RAD, pt.Y - PT_RAD, PT_WID, PT_WID)
        End Sub


        Public Sub Draw(gr As Graphics, pen As System.Drawing.Pen)
            'gr.FillPolygon(brush, m_Points.ToArray())
            gr.DrawPolygon(pen, m_Points.ToArray())

            For Each pt As PointF In m_Points
                Me.DrawPoint(gr, Brushes.Black, pt)
                'Dim ss As String = "[" + pt.X.ToString + "," + pt.Y.ToString + "]"
                'Dim fn As System.Drawing.Font = New System.Drawing.Font("Arial", 12)
                'gr.DrawString(ss, fn, System.Drawing.Brushes.Black, pt)
            Next pt

            '' draw centroid
            'If (Not m_Centroid.X = 0.0) And (Not m_Centroid.Y = 0.0) Then
            '    Me.DrawPoint(gr, Brushes.Red, m_Centroid)
            'End If

        End Sub

        ' Find the polygon's centroid.
        Public Sub FindCentroid()

            ' Add the first point at the end of the array.
            m_Points.Add(New PointF(m_Points(0).X, m_Points(0).Y))

            ' Find the centroid.
            Dim X As Single = 0
            Dim Y As Single = 0
            Dim second_factor As Single
            For i As Integer = 0 To m_Points.Count - 2
                second_factor = m_Points(i).X * m_Points(i + 1).Y - m_Points(i + 1).X * m_Points(i).Y
                X += (m_Points(i).X + m_Points(i + 1).X) * second_factor
                Y += (m_Points(i).Y + m_Points(i + 1).Y) * second_factor
            Next i

            ' Divide by 6 times the polygon's area.
            Dim polygon_area As Single = Me.PolygonArea()
            X /= (6 * polygon_area)
            Y /= (6 * polygon_area)

            ' If the values are negative, the polygon is
            ' oriented counterclockwise. Reverse the signs.
            If X < 0 Then
                X = -X
                Y = -Y
            End If

            m_Centroid.X = X
            m_Centroid.Y = Y

        End Sub

        ' Return True if the point is in the polygon.
        Public Function PointInPolygon(ByVal X As Single, ByVal Y As Single) As Boolean

            ' Get the angle between the point and the
            ' first and last vertices.
            Dim max_point As Integer = m_Points.Count - 1
            Dim total_angle As Single = GetAngle(m_Points(max_point).X, m_Points(max_point).Y, X, Y, m_Points(0).X, m_Points(0).Y)

            ' Add the angles from the point
            ' to each other pair of vertices.
            For i As Integer = 0 To max_point - 1
                total_angle += GetAngle( _
                    m_Points(i).X, m_Points(i).Y, _
                    X, Y, _
                    m_Points(i + 1).X, m_Points(i + 1).Y)
            Next i

            ' The total angle should be 2 * PI or -2 * PI if
            ' the point is in the polygon and close to zero
            ' if the point is outside the polygon.
            Return Math.Abs(total_angle) > 0.000001

        End Function

        ' Return True if the polygon is oriented clockwise.
        Public Function PolygonIsOrientedClockwise() As Boolean
            Return Me.SignedPolygonArea() < 0
        End Function

        ' If the polygon is oriented counterclockwise,
        ' reverse the order of its points.
        Private Sub OrientPolygonClockwise()

            If Not Me.PolygonIsOrientedClockwise() Then
                m_Points.Reverse()
            End If

        End Sub

        ' Return the polygon's area in "square units."
        ' Add the areas of the trapezoids defined by the
        ' polygon's edges dropped to the X-axis. When the
        ' program considers a bottom edge of a polygon, the
        ' calculation gives a negative area so the space
        ' between the polygon and the axis is subtracted,
        ' leaving the polygon's area. This method gives odd
        ' results for non-simple polygons.
        Public Function PolygonArea() As Single
            ' Return the absolute value of the signed area.
            ' The signed area is negative if the polyogn is
            ' oriented clockwise.
            Return Math.Abs(Me.SignedPolygonArea())
        End Function

        ' Return the polygon's area in "square units."
        ' Add the areas of the trapezoids defined by the
        ' polygon's edges dropped to the X-axis. When the
        ' program considers a bottom edge of a polygon, the
        ' calculation gives a negative area so the space
        ' between the polygon and the axis is subtracted,
        ' leaving the polygon's area. This method gives odd
        ' results for non-simple polygons.
        '
        ' The value will be negative if the polyogn is
        ' oriented clockwise.
        Private Function SignedPolygonArea() As Single
            ' Add the first point to the end.
            m_Points.Add(m_Points(0))

            ' Get the areas.
            Dim area As Single = 0
            For i As Integer = 0 To m_Points.Count - 2
                area += _
                    (m_Points(i + 1).X - m_Points(i).X) * _
                    (m_Points(i + 1).Y + m_Points(i).Y) / 2
            Next i

            'remove the added point
            m_Points.RemoveAt(m_Points.Count - 1)

            ' Return the result.
            Return area
        End Function

        ' Return True if the polygon is convex.
        Public Function PolygonIsConvex() As Boolean
            ' For each set of three adjacent points A, B, C,
            ' find the dot product AB · BC. If the sign of
            ' all the dot products is the same, the angles
            ' are all positive or negative (depending on the
            ' order in which we visit them) so the polygon
            ' is convex.

            Dim got_negative As Boolean = False
            Dim got_positive As Boolean = False
            Dim max_point As Integer = m_Points.Count - 1
            Dim B, C As Integer
            For A As Integer = 0 To max_point
                B = A + 1
                If B > max_point Then B = 0
                C = B + 1
                If C > max_point Then C = 0

                Dim cross_product As Single = _
                    CrossProductLength( _
                        m_Points(A).X, m_Points(A).Y, _
                        m_Points(B).X, m_Points(B).Y, _
                        m_Points(C).X, m_Points(C).Y)
                If cross_product < 0 Then
                    got_negative = True
                ElseIf cross_product > 0 Then
                    got_positive = True
                End If
                If got_negative And got_positive Then Return False
            Next A

            ' If we got this far, the polygon is convex.
            Return True
        End Function

        ' Return the cross product AB x BC.
        ' The cross product is a vector perpendicular to AB
        ' and BC having length |AB| * |BC| * Sin(theta) and
        ' with direction given by the right-hand rule.
        ' For two vectors in the X-Y plane, the result is a
        ' vector with X and Y components 0 so the Z component
        ' gives the vector's length and direction.
        Public Function CrossProductLength( _
            ByVal Ax As Single, ByVal Ay As Single, _
            ByVal Bx As Single, ByVal By As Single, _
            ByVal Cx As Single, ByVal Cy As Single _
          ) As Single
            ' Get the vectors' coordinates.
            Dim BAx As Single = Ax - Bx
            Dim BAy As Single = Ay - By
            Dim BCx As Single = Cx - Bx
            Dim BCy As Single = Cy - By

            ' Calculate the Z coordinate of the cross product.
            Return BAx * BCy - BAy * BCx
        End Function

        ' Return the dot product AB · BC.
        ' Note that AB · BC = |AB| * |BC| * Cos(theta).
        Private Function DotProduct( _
            ByVal Ax As Single, ByVal Ay As Single, _
            ByVal Bx As Single, ByVal By As Single, _
            ByVal Cx As Single, ByVal Cy As Single _
          ) As Single
            ' Get the vectors' coordinates.
            Dim BAx As Single = Ax - Bx
            Dim BAy As Single = Ay - By
            Dim BCx As Single = Cx - Bx
            Dim BCy As Single = Cy - By

            ' Calculate the dot product.
            Return BAx * BCx + BAy * BCy
        End Function

        ' Return the angle ABC.
        ' Return a value between PI and -PI.
        ' Note that the value is the opposite of what you might
        ' expect because Y coordinates increase downward.
        Public Function GetAngle(ByVal Ax As Single, ByVal Ay As Single, ByVal Bx As Single, ByVal By As Single, ByVal Cx As Single, ByVal Cy As Single) As Single
            Dim dot_product As Single
            Dim cross_product As Single

            ' Get the dot product and cross product.
            dot_product = DotProduct(Ax, Ay, Bx, By, Cx, Cy)
            cross_product = CrossProductLength(Ax, Ay, Bx, By, Cx, Cy)

            ' Calculate the angle.
            Return Math.Atan2(cross_product, dot_product)
        End Function

        ' Find the indexes of three points that form an ear.
        Private Sub FindEar(ByRef A As Integer, ByRef B As Integer, ByRef C As Integer)
            Dim max_point As Integer = m_Points.Count - 1

            For A = 0 To max_point
                B = A + 1
                If B > max_point Then B = 0
                C = B + 1
                If C > max_point Then C = 0

                If FormsEar(A, B, C) Then Exit Sub
            Next A

            ' We should never get here because there should
            ' always be at least two ears.
            Stop
        End Sub

        ' Return True if the three points form an ear.
        Private Function FormsEar(ByVal A As Integer, ByVal B As Integer, ByVal C As Integer) As Boolean
            ' See if the angle ABC is concave.
            If GetAngle( _
                m_Points(A).X, m_Points(A).Y, _
                m_Points(B).X, m_Points(B).Y, _
                m_Points(C).X, m_Points(C).Y) > 0 _
            Then
                ' This is a concave corner so the triangle
                ' cannot be an ear.
                Return False
            End If

            ' Make the triangle A, B, C.
            Dim test_points() As PointF = _
                {m_Points(A), m_Points(B), m_Points(C)}

            ' Check the other points to see 
            ' if they lie in triangle A, B, C.
            For i As Integer = 0 To m_Points.Count - 1
                If (i <> A) AndAlso (i <> B) AndAlso (i <> C) Then
                    With m_Points(i)
                        If PointInPolygon(.X, .Y) Then
                            ' This point is in the triangle so
                            ' this is not an ear.
                            Return False
                        End If
                    End With
                End If
            Next i

            ' This is an ear.
            Return True
        End Function

        ' Remove an ear from the polygon.
        Private Sub RemoveEar(ByRef triangles() As Triangle)
            ' Find an ear.
            Dim A, B, C As Integer
            FindEar(A, B, C)

            ' Create a new triangle for the ear.
            ReDim Preserve triangles(triangles.Length)
            triangles(triangles.Length - 1) = _
                New Triangle(m_Points(A), m_Points(B), m_Points(C))

            ' Remove the ear from the polygon.
            RemovePointFromArray(B)
        End Sub

        ' Remove point target from the array.
        Private Sub RemovePointFromArray(ByVal target As Integer)
            m_Points.RemoveAt(target)
        End Sub

        ' Traingulate the polygon.
        '
        ' For a nice, detailed explanation of this method,
        ' see Ian Garton's Web page:
        ' http://www-cgrl.cs.mcgill.ca/~godfried/teaching/cg-projects/97/Ian/cutting_ears.html
        Public Function Triangulate() As Triangle()


            ' Orient the polygon clockwise.
            Dim copyPolygon As Polygon = Me.Clone()
            copyPolygon.OrientPolygonClockwise()

            ' Make room for the triangles.
            Dim triangles() As Triangle = {}

            ' While the copy of the polygon has more than
            ' three points, remove an ear.
            Do While copyPolygon.Count > 3
                ' Remove an ear from the polygon.
                copyPolygon.RemoveEar(triangles)
            Loop

            ' Copy the last three points into their own triangle.
            ReDim Preserve triangles(triangles.Length)
            triangles(triangles.Length - 1) = _
                New Triangle(copyPolygon.PointAt(0), copyPolygon.PointAt(1), copyPolygon.PointAt(2))

            Return triangles
        End Function

    End Class


    Public Class Line

        Private ReadOnly m_StartPoint, m_EndPoint As PointF

        Public Sub New(ByVal startPoint As PointF, ByVal endPoint As PointF)
            m_StartPoint = startPoint
            m_EndPoint = endPoint
        End Sub

        Public ReadOnly Property StartPoint() As PointF
            Get
                Return m_StartPoint
            End Get
        End Property

        Public ReadOnly Property EndPoint() As PointF
            Get
                Return m_EndPoint
            End Get
        End Property


        Enum IntersectResult
            Parallel
            Coincident
            DoNotIntersect
            Intersect
        End Enum


        Public Shared Function Intersect(ByVal lineOne As Line, ByVal lineTwo As Line, ByRef intersection As PointF) As IntersectResult

            Dim denominator As Double = ((lineOne.m_EndPoint.Y - lineOne.m_StartPoint.Y) * (lineTwo.m_EndPoint.X - lineTwo.m_StartPoint.X)) - _
                          ((lineOne.m_EndPoint.X - lineOne.m_StartPoint.X) * (lineTwo.m_EndPoint.Y - lineTwo.m_StartPoint.Y))

            Dim numeratorOne As Double = ((lineOne.m_EndPoint.X - lineOne.m_StartPoint.X) * (lineTwo.m_StartPoint.Y - lineOne.m_StartPoint.Y)) - _
                           ((lineOne.m_EndPoint.Y - lineOne.m_StartPoint.Y) * (lineTwo.m_StartPoint.X - lineOne.m_StartPoint.X))

            Dim numeratorTwo As Double = ((lineTwo.m_EndPoint.X - lineTwo.m_StartPoint.X) * (lineTwo.m_StartPoint.Y - lineOne.m_StartPoint.Y)) - _
                           ((lineTwo.m_EndPoint.Y - lineTwo.m_StartPoint.Y) * (lineTwo.m_StartPoint.X - lineOne.m_StartPoint.X))

            If denominator = 0 Then
                If numeratorOne = 0.0 AndAlso numeratorTwo = 0.0 Then
                    Return IntersectResult.Coincident
                End If

                Return IntersectResult.Parallel
            End If

            Dim a As Double = numeratorOne / denominator
            Dim b As Double = numeratorTwo / denominator

            If a >= 0.0 AndAlso a <= 1.0 AndAlso b >= 0.0 AndAlso b <= 1.0 Then

                intersection.X = lineTwo.m_StartPoint.X + a * (lineTwo.m_EndPoint.X - lineTwo.m_StartPoint.X)
                intersection.Y = lineTwo.m_StartPoint.Y + a * (lineTwo.m_EndPoint.Y - lineTwo.m_StartPoint.Y)

                Return IntersectResult.Intersect
            End If

            Return IntersectResult.DoNotIntersect

        End Function
    End Class

End Module
