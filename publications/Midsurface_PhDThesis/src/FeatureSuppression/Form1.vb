Imports System
Imports System.Type
Imports System.Activator
Imports System.Runtime.InteropServices
Imports Inventor

Public Class Form1

    ' App variables.
    Dim _invApp As Inventor.Application
    Private m_partDoc As PartDocument
    Dim _started As Boolean = False
    Dim _initialized As Boolean = False

    'Feature lists
    Private m_suppressableFeatures As ObjectCollection
    Private m_highlightedFeatures As HighlightSet

    'Size parameters
    Private m_partSize As Double
    Private m_sizeD As Double = 0.05
    Dim m_userSizePercentage As Integer

    'Validation
    Dim m_numFacesBefore As Integer
    Dim m_numFacesAfter As Integer


    'Temporary
    Dim m_ChildLogic As Boolean = False 'waiting for ready parent-child logic, works for basic parts, but TOO slow for complex



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

        Dim pBB As Inventor.Box
        pBB = m_partDoc.ComponentDefinition.RangeBox

        m_partSize = pBB.MinPoint.DistanceTo(pBB.MaxPoint)

    End Function

    Private Function GetParentFromProfile(ByRef profile As Inventor.Profile) As PartFeature

        GetParentFromProfile = Nothing

        If profile Is Nothing Then
            Exit Function
        End If

        '' VERY BAD PLACE TO REMOVE INNER LOOPS, this function is not supposed to change, but, for now...
        'Dim path As ProfilePath
        'For Each path In profile
        '    If path.AddsMaterial = False Then
        '        'get size, if small then  path.Delete()
        '    End If
        'Next


        Dim sketch As Inventor.PlanarSketch = profile.Parent

        If Not sketch Is Nothing Then
            If Not sketch.PlanarEntity Is Nothing Then
                If TypeOf sketch.PlanarEntity Is Face Then
                    GetParentFromProfile = sketch.PlanarEntity.CreatedByFeature
                End If
            End If
        End If
    End Function

    Private Function IsChild(child As PartFeature, parent As PartFeature) As Boolean

        IsChild = False

        Dim parentFeature As PartFeature = Nothing

        If TypeOf child Is ExtrudeFeature Then
            Dim extrude As ExtrudeFeature = child
            parentFeature = GetParentFromProfile(extrude.Profile)

        ElseIf TypeOf child Is RevolveFeature Then
            Dim revolve As RevolveFeature = child
            parentFeature = GetParentFromProfile(revolve.Profile)

        ElseIf TypeOf child Is SweepFeature Then
            Dim sweep As SweepFeature = child
            parentFeature = GetParentFromProfile(sweep.Profile)

        ElseIf TypeOf child Is HoleFeature Then
            Dim hole As HoleFeature = child
            parentFeature = hole.PlacementDefinition.Parent

        Else
            ' Generic way of getting parent via Faces
            Dim faces As Inventor.Faces = child.Faces
            For Each face As Inventor.Face In faces
                parentFeature = face.CreatedByFeature
                Debug.Print(parentFeature.Name)
                If parentFeature Is parent Then ' found the match
                    IsChild = True
                    Exit Function
                End If
            Next
        End If


        If parentFeature Is parent Then ' found the match
            IsChild = True
        End If

    End Function


    Private Sub FindDependentFeatures(ByVal oFeature As PartFeature, ByRef childList As ObjectCollection)

        Debug.Print("Finding Children for " & oFeature.Name)

        Dim allFeatures As Inventor.PartFeatures
        allFeatures = m_partDoc.ComponentDefinition.Features

        Dim toStartTraverse As Boolean = False

        Dim ifeat As PartFeature
        For Each ifeat In allFeatures
            'Debug.Print(ifeat.Name)

            If Not ifeat Is Nothing And ifeat.Equals(oFeature) Then ' till oFeature skip, as children are afterwards
                toStartTraverse = True
                Continue For ' next one is the actual start for the search...re-look to optimize
            ElseIf toStartTraverse = False Then
                Continue For
            End If

            Dim pFeature As PartFeature = Nothing

            If toStartTraverse And Not ifeat Is Nothing And TypeOf ifeat Is PartFeature Then

                If IsChild(ifeat, oFeature) = True Then

                    '============== RECURSION =======================
                    'FindDependentFeatures(ifeat, childList) ' for now only one level

                    childList.Add(ifeat)
                End If

            End If
        Next

        'Debug.Print(childList.Count)

    End Sub

    Private Function UnionBoundingBoxes(ByVal box As Box, ByVal box1 As Box) As Box
        Dim result As Inventor.Box = box

        If box1 Is Nothing Then
            UnionBoundingBoxes = result
            Exit Function
        End If

        'BAD CHECK, but for now

        If ((box1.MinPoint.X < box.MinPoint.X) And _
            (box1.MinPoint.Y < box.MinPoint.Y) And _
            (box1.MinPoint.Z < box.MinPoint.Z)) Then
            result.MinPoint = box1.MinPoint
        End If

        If ((box1.MaxPoint.X > box.MaxPoint.X) And _
            (box1.MaxPoint.Y > box.MaxPoint.Y) And _
            (box1.MaxPoint.Z > box.MaxPoint.Z)) Then
            result.MaxPoint = box1.MaxPoint
        End If

        UnionBoundingBoxes = result

    End Function

    Private Function FindUnionedBoundingBox(ByVal oFeature As PartFeature, ByRef oList As ObjectCollection) As Inventor.Box
        Dim box As Inventor.Box = oFeature.RangeBox

        If oList.Count = 0 Then
            FindUnionedBoundingBox = box
            Exit Function
        End If

        'Debug.Print("FindUnionedBoundingBox: Parent Box size = " & box.MinPoint.DistanceTo(box.MaxPoint))

        ' traverse and collect BB
        Dim oObj As Object
        For Each oObj In oList
            If Not oObj Is Nothing Then
                If TypeOf oObj Is PartFeature Then
                    Dim pFeat As PartFeature
                    pFeat = oObj
                    If Not pFeat.Name.Equals(oFeature.Name) Then
                        Debug.Print(" has child " & pFeat.Name)
                        'Debug.Print("\t Child Box size = " & pFeat.RangeBox.MinPoint.DistanceTo(pFeat.RangeBox.MaxPoint))
                        box = UnionBoundingBoxes(box, pFeat.RangeBox)
                    End If
                End If
            End If
        Next

        'Debug.Print("\t Union Box size = " & box.MinPoint.DistanceTo(box.MaxPoint))

        FindUnionedBoundingBox = box
    End Function

    Private Function IsSuppressible(ByVal oFeature As PartFeature) As Boolean

        IsSuppressible = False

        If Not oFeature Is Nothing Then

            If TypeOf oFeature Is HoleFeature Then
                Dim hFeature As HoleFeature
                hFeature = oFeature
                Dim diameter As Double
                diameter = hFeature.HoleDiameter.Value
                If diameter < m_sizeD Then
                    IsSuppressible = True
                End If

            ElseIf TypeOf oFeature Is MirrorFeature Then
                IsSuppressible = True ' parent will be preserved

            ElseIf TypeOf oFeature Is CircularPatternFeature Then
                IsSuppressible = True ' parent will be preserved

            ElseIf TypeOf oFeature Is RectangularPatternFeature Then
                IsSuppressible = True ' parent will be preserved

            ElseIf TypeOf oFeature Is FilletFeature Then
                Dim fFeature As FilletFeature
                fFeature = oFeature
                Dim radius As Double
                radius = fFeature.Parameters(1).Value
                If (2 * radius) < m_sizeD Then
                    IsSuppressible = True
                End If

            ElseIf TypeOf oFeature Is ChamferFeature Then
                Dim cFeature As ChamferFeature
                cFeature = oFeature
                Dim side As Double
                side = cFeature.Parameters(1).Value
                If side < m_sizeD Then
                    IsSuppressible = True
                End If
            Else

                Dim fBB As Inventor.Box = oFeature.RangeBox

                'find dependent children
                If m_ChildLogic = True Then
                    Dim dlist As ObjectCollection = _invApp.TransientObjects.CreateObjectCollection()
                    FindDependentFeatures(oFeature, dlist)  ' NOT READY YET
                    Debug.Print("Parent " & oFeature.Name & " has " & dlist.Count & " Children")
                    'find Union BB
                    fBB = FindUnionedBoundingBox(oFeature, dlist)
                End If

                ' compare bounding box size
                If Not fBB Is Nothing Then
                    Dim fSize As Double
                    fSize = fBB.MinPoint.DistanceTo(fBB.MaxPoint)
                    If fSize < m_sizeD Then  ' fSize*3 CAN BE DONE TO SUPPRESS REAL REAL SMALL FEATURES
                        IsSuppressible = True
                    End If
                End If
                End If

        End If
    End Function

    Private Sub CollectSuppressibleFeatures()

        If _initialized = False Then
            Exit Sub
        End If

        m_sizeD = (m_userSizePercentage / 100.0) * m_partSize

        Dim sFeatures As Inventor.PartFeatures
        sFeatures = m_partDoc.ComponentDefinition.Features

        m_suppressableFeatures = _invApp.TransientObjects.CreateObjectCollection

        Dim oFeature As PartFeature
        For Each oFeature In sFeatures
            'Debug.Print(oFeature.Name)
            If IsSuppressible(oFeature) = True Then
                m_suppressableFeatures.Add(oFeature)
            End If
        Next
    End Sub

    Private Sub Form1_FormClosed(sender As Object, e As System.Windows.Forms.FormClosedEventArgs) Handles Me.FormClosed

        CleanupForSamePart()

        If _started Then
            _invApp.Quit()
        End If

        _invApp = Nothing
    End Sub

    Private Sub CleanupForSamePart()
        'clean earlier lists if any
        If Not m_suppressableFeatures Is Nothing Then
            If m_suppressableFeatures.Count > 0 Then
                m_suppressableFeatures.Clear()
            End If
        End If


        If Not m_highlightedFeatures Is Nothing Then
            If m_highlightedFeatures.Count > 0 Then
                m_highlightedFeatures.Clear()
            End If
        End If
    End Sub

    Private Sub PreviewButton_Click(sender As System.Object, e As System.EventArgs) Handles PreviewButton.Click

        ' set active part
        If _initialized = False Then
            _initialized = Init()
        End If

        If _initialized = False Then
            Exit Sub
        End If

        ' If Preview button is clicked after changing %age value, while part remaining the samee
        CleanupForSamePart()

        ' generate tree.
        CollectSuppressibleFeatures()

        If m_highlightedFeatures Is Nothing Then
            m_highlightedFeatures = _invApp.ActiveDocument.HighlightSets.Add
        End If


        ' Highlight the features.
        Dim oFeature As PartFeature
        For Each oFeature In m_suppressableFeatures
            If Not oFeature Is Nothing Then
                'Debug.Print(oFeature.Name)
                m_highlightedFeatures.AddItem(oFeature)
            End If
        Next

        'MsgBox("Number of features in suppress list are " & m_suppressableFeatures.Count)

    End Sub

    Private Sub SuppressButton_Click(sender As System.Object, e As System.EventArgs) Handles SuppressButton.Click

        If Not m_highlightedFeatures Is Nothing Then
            m_highlightedFeatures.Clear()
        End If


        'set EndOfPart to Top, then set Suppressed, then restore back, to improve performance
        Dim oCompDef As Inventor.ComponentDefinition
        oCompDef = m_partDoc.ComponentDefinition
        If TypeOf oCompDef Is Inventor.AssemblyComponentDefinition Then
            oCompDef.SetEndOfFeaturesToTopOrBottom(True)
        ElseIf TypeOf oCompDef Is Inventor.PartComponentDefinition Then
            m_numFacesBefore = oCompDef.SurfaceBodies.Item(1).Faces.Count
            oCompDef.SetEndOfPartToTopOrBottom(True)
        End If

 

        ' Suppression
        Dim oObj As Object

        For Each oObj In m_suppressableFeatures
            If Not oObj Is Nothing Then
                If TypeOf oObj Is PartFeature Then
                    Dim oFeature As PartFeature = oObj
                    oFeature.Suppressed = True
                End If
            End If
        Next


        'end restored
        Dim ocCompDef As Inventor.ComponentDefinition
        ocCompDef = m_partDoc.ComponentDefinition
        If TypeOf ocCompDef Is Inventor.AssemblyComponentDefinition Then
            ocCompDef.SetEndOfFeaturesToTopOrBottom(False)
        ElseIf TypeOf ocCompDef Is Inventor.PartComponentDefinition Then
            ocCompDef.SetEndOfPartToTopOrBottom(False)
            'collect stats after
            m_numFacesAfter = oCompDef.SurfaceBodies.Item(1).Faces.Count
        End If


        MsgBox("Num Faces before were " & m_numFacesBefore & " and now Num Faces are " & m_numFacesAfter)

    End Sub

    Private Sub ThresholdValue_TextChanged(sender As System.Object, e As System.EventArgs) Handles ThresholdValue.TextChanged

        m_userSizePercentage = Double.Parse(ThresholdValue.Text)

        Try
            ' if it is a negative number. 
            If (m_userSizePercentage < 0) Then
                'If the number is negative, display it in Red.
                ThresholdValue.ForeColor = Drawing.Color.Red
            Else
                'If the number is not negative, display it in Black.
                ThresholdValue.ForeColor = Drawing.Color.Black
            End If

        Catch

        End Try

        'If there is an error, display the text using the system colors.
        ThresholdValue.ForeColor = SystemColors.ControlText

    End Sub

 


End Class
