Imports System
Imports System.Type
Imports System.Activator
Imports System.Runtime.InteropServices
Imports Inventor
Imports SheetMetalLoD.Yogesh
Imports FbMidsurfUtilities.Yogesh

Public Class Form1

    ' App variables.
    Dim _invApp As Inventor.Application
    Dim _started As Boolean = False
    Dim _initialized As Boolean = False

    ' UI elements
    'Size parameters
    Public m_partSize As Double ' either the diagonal of the BB or sqrt of sum-of-face-areas
    Public m_userSizePercentage As Integer ' users input
    Public m_sizeD As Double = 0.05 ' default value, will get calculated by above two

    ' Wrapping: No Negative volumes are kept'
    Public m_Wrapping As Boolean = True

    'ACTUAL DRIVER
    Dim m_defeaturer As Yogesh.SheetMetalDefeaturer

    ' Init Exit functionality ----------------------------------------------------------------------

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

        m_defeaturer = New Yogesh.SheetMetalDefeaturer(_invApp)

    End Sub

    ' Makes sure that part is loaded
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

        m_defeaturer.ClearFeatureListsAndClusters()
        m_defeaturer.CloseWrittenFile()

        If _started Then
            _invApp.Quit()
        End If

        _invApp = Nothing
    End Sub

    ' Callbacks ----------------------------------------------------------------------

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

    Private Sub WrapOption_CheckedChanged(sender As System.Object, e As System.EventArgs) Handles WrapOption.CheckedChanged
        m_Wrapping = WrapOption.Checked
        If Not m_defeaturer Is Nothing Then
            m_defeaturer.m_Wrapping = m_Wrapping
            ' If Preview button is clicked after changing %age value, while part remaining the samee
            m_defeaturer.ClearFeatureListsAndClusters()
        End If
    End Sub

    Private Sub InitUnfold_Click(sender As System.Object, e As System.EventArgs) Handles InitUnfold.Click

        ' set active part
        If _initialized = False Then
            _initialized = Init()
        End If
        m_defeaturer.Init()
        m_defeaturer.SuppressAllUnfoldFeatures()
        m_partSize = m_defeaturer.CalculatePartSize()
        m_defeaturer.m_userSizePercentage = m_userSizePercentage

        m_sizeD = (m_userSizePercentage / 100.0) * m_partSize
        m_defeaturer.m_sizeD = m_sizeD

        SizeLabel.Text = "of " + m_partSize.ToString("#.##") + " = " + m_sizeD.ToString("#.##") ' or bbDiagonal.ToString("#.##")

        '--------------------------------------------------------------------------------------------------

        If m_partSize > 0 Then
            PreviewSButton.Enabled = True
            PreviewRButton.Enabled = True
        End If
        m_defeaturer.WriteToFile("Global Size = " & m_sizeD.ToString("#.##"))
    End Sub

    Private Sub PreviewSButton_Click(sender As System.Object, e As System.EventArgs) Handles PreviewSButton.Click
        If _initialized = False Then
            Exit Sub
        End If
        m_defeaturer.ClearFeatureListsAndClusters()
        SuppressSButton.Enabled = m_defeaturer.CollectAndHighlightSuppressibleSheetMetalFeatures(True, m_Wrapping)
    End Sub

    Private Sub SuppressSButton_Click(sender As System.Object, e As System.EventArgs) Handles SuppressSButton.Click
        If _initialized = False Then
            Exit Sub
        End If

        m_defeaturer.SuppressSheetMetalFeatures(True, True)

    End Sub

    Private Sub PreviewRButton_Click(sender As System.Object, e As System.EventArgs) Handles PreviewRButton.Click

        If _initialized = False Then
            Exit Sub
        End If
        m_defeaturer.ClearFeatureListsAndClusters()
        SuppressRButton.Enabled = m_defeaturer.CollectAndHighlightSuppressibleRemnantFeatures(True)

    End Sub

    Private Sub SuppressRButton_Click(sender As System.Object, e As System.EventArgs) Handles SuppressRButton.Click

        If _initialized = False Then
            Exit Sub
        End If

        m_defeaturer.SuppressRemnantFeatures(True, True)

    End Sub

End Class

Namespace Yogesh

    Public Class SheetMetalDefeaturer

        Private m_partDoc As PartDocument
        Private _invApp As Inventor.Application
        Private m_thickness As Double = 0.0 ' Sheet Metal Thickness from Document properties
        Private m_bendradius As Double = 0.0 ' Sheet Metal component Definition
        Private Const CLSID_InventorSheetMetalPart_RegGUID = "{9C464203-9BAE-11D3-8BAD-0060B0CE6BB4}"
        Private m_compDef As ComponentDefinition

        'Feature lists
        Private m_suppressableSFeatures As ObjectCollection ' Suppressable Sheet Metal features
        Private m_suppressableRFeatures As ObjectCollection ' Suppressable Remnant features
        Private m_suppressableDFeatures As ObjectCollection ' Suppressable Dormant features
        Private m_dormantToolBodies As ObjectCollection     ' To be used for piercing the midsurface

        Private m_highlightedSMFeatures As HighlightSet ' just for user feedback, TODO: user can override, and then this is sent for suppression
        Private m_highlightedRMFeatures As HighlightSet ' just for user feedback, TODO: user can override, and then this is sent for suppression
        Private m_highlightedDMFeatures As HighlightSet ' just for user feedback, TODO: user can override, and then this is sent for suppression
        Private m_clusters As List(Of Cluster) = New List(Of Cluster) ' List of Groups, each goes for suppression together

        'Size parameters
        Private m_partSize As Double ' either the diagonal of the BB or sqrt of sum-of-face-areas
        Public m_userSizePercentage As Integer ' users input
        Public m_sizeD As Double = 0.05 ' default value, will get calculated by above two

        ' Wrapping: No Negative volumes are kept'
        Public m_Wrapping As Boolean = True

        'Validation Statistics
        Private m_numFacesBefore As Integer
        Private m_numFacesAfter As Integer
        Private m_numFeaturesBefore As Integer
        Private m_numFeaturesAfter As Integer

        ' file i/o
        Private sw As IO.StreamWriter

        ' Common Utility functionality
        Private m_Utilities As FbMidsurfUtilities.Yogesh.FbMidsurfUtilities


        Private Class Cluster
            Public m_clusterFeatures As List(Of PartFeature) = New List(Of PartFeature)
            Private m_clusterFaces As List(Of Face) = New List(Of Face)
            Private m_clusterSize As Double = 0.0
            Public m_MarkForDelete As Boolean = False ' After merging, the operand is Marked for delete, not deleted but skipped

            Public Sub New()
            End Sub

            Public Sub MergeCluster(ByRef pCluster As Cluster)

                ' Add faces fro 'Other' into 'Self' and mark that one for 'Delete'
                ' As 'Self' expands, Size calculatations are done on the expanded entity
                For Each face In pCluster.m_clusterFaces
                    AddFaceAndOwnerFeature(face)
                Next
                pCluster.m_MarkForDelete = True
            End Sub

            ' Checks uniqueness and adds the face, Checks uniqueness and adds its owner feature as well
            Public Function AddFaceAndOwnerFeature(ByRef pFace As Face) As Boolean ' true if successfully added
                AddFaceAndOwnerFeature = False

                Dim indexSelfFace As Integer = m_clusterFaces.IndexOf(pFace)
                If indexSelfFace < 0 Then
                    m_clusterFaces.Add(pFace)
                    Dim owner As PartFeature = pFace.CreatedByFeature
                    Dim indexSelfFeature As Integer = m_clusterFeatures.IndexOf(owner)
                    If indexSelfFeature < 0 Then
                        m_clusterFeatures.Add(owner)
                    End If
                End If

            End Function

            ' check if itself 
            Public Function IsAmongstFeatures(ByRef owner As PartFeature) As Boolean
                IsAmongstFeatures = False
                If Not owner Is Nothing Then
                    Dim indexSelf As Integer = m_clusterFeatures.IndexOf(owner)
                    If Not indexSelf < 0 Then
                        IsAmongstFeatures = True
                        'Else
                        '    For Each iFeat In m_clusterFeatures
                        '        If IsChild(owner, iFeat) = True Then
                        '            IsAmongstFeatures = True
                        '            End for
                        '        End If
                        '    Next
                    End If
                End If


                'Dim gotit As PartFeature = m_clusterFeatures.Find(Function(value As PartFeature)
                '                                                      Return Object.ReferenceEquals(value, owner)
                '                                                  End Function)
            End Function

            ' Copied from Form1 class, see how static functions are used in VB
            'Private Function UnionBoundingBoxes(ByVal box As Box, ByVal box1 As Box) As Box
            '    Dim result As Inventor.Box = box

            '    If box Is Nothing Then
            '        UnionBoundingBoxes = box1 ' first time 'box' is 'Nothing'
            '        Exit Function
            '    End If

            '    'BAD CHECK, but for now

            '    If ((box1.MinPoint.X < box.MinPoint.X) And _
            '        (box1.MinPoint.Y < box.MinPoint.Y) And _
            '        (box1.MinPoint.Z < box.MinPoint.Z)) Then
            '        result.MinPoint = box1.MinPoint
            '    End If

            '    If ((box1.MaxPoint.X > box.MaxPoint.X) And _
            '        (box1.MaxPoint.Y > box.MaxPoint.Y) And _
            '        (box1.MaxPoint.Z > box.MaxPoint.Z)) Then
            '        result.MaxPoint = box1.MaxPoint
            '    End If

            '    UnionBoundingBoxes = result

            'End Function

            Public Function GetSize() As Double

                If m_clusterSize = 0.0 Then

                    ' The Bounding box method is not reliable and quick as Face's BB given seems to be of untrimmed surface
                    ' and unioning BB's is taking a lot of time

                    'Dim box As Inventor.Box = Nothing
                    'For Each pFace In m_clusterFaces
                    '    Dim pfBox As Inventor.Box = pFace.Evaluator.RangeBox
                    '    box = UnionBoundingBoxes(box, pfBox)
                    'Next
                    '' compare bounding box size
                    'If Not box Is Nothing Then
                    '    m_clusterSize = box.MinPoint.DistanceTo(box.MaxPoint)
                    'End If

                    For Each pFace In m_clusterFaces
                        m_clusterSize += pFace.Evaluator.Area
                    Next

                    ' To get the dimensionality right, reduce the degree
                    m_clusterSize = Math.Sqrt(m_clusterSize)

                End If

                GetSize = m_clusterSize

            End Function

            ' Debug Dump
            Public Sub WriteToFile(ByVal sw As IO.StreamWriter)
                sw.Write("[ ")
                For Each oFeature In m_clusterFeatures
                    sw.Write(oFeature.Name & " ")
                Next
                sw.Write("] = " & m_clusterSize.ToString("#.##"))
            End Sub



        End Class

        Public Sub New(ByRef app As Inventor.Application)
            _invApp = app
            m_partDoc = _invApp.ActiveDocument()
            OpenForWrite("DebugDumpFile.txt")
        End Sub

        Sub Init()
            m_partDoc = _invApp.ActiveDocument()
            If Not m_partDoc Is Nothing Then
                m_compDef = m_partDoc.ComponentDefinition

                ' Make sure the document is a sheet metal document.
                If m_partDoc.SubType = CLSID_InventorSheetMetalPart_RegGUID Then
                    Dim oSheetMetalCompDef As SheetMetalComponentDefinition
                    oSheetMetalCompDef = m_partDoc.ComponentDefinition

                    Dim thickParam As Parameter
                    thickParam = oSheetMetalCompDef.Thickness
                    m_thickness = thickParam.Value

                    Dim radiusParam As Parameter
                    radiusParam = oSheetMetalCompDef.Thickness
                    m_bendradius = radiusParam.Value
                End If
            End If
            m_Utilities = New FbMidsurfUtilities.Yogesh.FbMidsurfUtilities(_invApp)
        End Sub

        Public Sub ClearFeatureListsAndClusters(Optional ByRef dormantAlso As Boolean = True)
            'clean earlier lists if any
            If Not m_suppressableSFeatures Is Nothing Then
                If m_suppressableSFeatures.Count > 0 Then
                    m_suppressableSFeatures.Clear()
                End If
            End If

            If Not m_suppressableRFeatures Is Nothing Then
                If m_suppressableRFeatures.Count > 0 Then
                    m_suppressableRFeatures.Clear()
                End If
            End If

            ' DORMANT entities may be needed later
            If dormantAlso Then
                If Not m_suppressableDFeatures Is Nothing Then
                    If m_suppressableDFeatures.Count > 0 Then
                        m_suppressableDFeatures.Clear()
                    End If
                End If
                If Not m_dormantToolBodies Is Nothing Then
                    If m_dormantToolBodies.Count > 0 Then
                        m_dormantToolBodies.Clear()
                    End If
                End If
            End If


            If Not m_highlightedSMFeatures Is Nothing Then
                If m_highlightedSMFeatures.Count > 0 Then
                    m_highlightedSMFeatures.Clear()
                End If
            End If
            If Not m_highlightedRMFeatures Is Nothing Then
                If m_highlightedRMFeatures.Count > 0 Then
                    m_highlightedRMFeatures.Clear()
                End If
            End If
            If Not m_highlightedDMFeatures Is Nothing Then
                If m_highlightedDMFeatures.Count > 0 Then
                    m_highlightedDMFeatures.Clear()
                End If
            End If



            If Not m_clusters Is Nothing Then
                If m_clusters.Count > 0 Then
                    m_clusters.Clear()
                End If
            End If
        End Sub

        'Parent Child Access functionality ----------------------------------------------------------------------

        'Private Function GetParentFromProfile(ByRef profile As Inventor.Profile) As PartFeature

        '    GetParentFromProfile = Nothing

        '    If profile Is Nothing Then
        '        Exit Function
        '    End If

        '    '' VERY BAD PLACE TO REMOVE INNER LOOPS, this function is not supposed to change, but, for now...
        '    'Dim path As ProfilePath
        '    'For Each path In profile
        '    '    If path.AddsMaterial = False Then
        '    '        'get size, if small then  path.Delete()
        '    '    End If
        '    'Next


        '    Dim sketch As Inventor.PlanarSketch = profile.Parent

        '    If Not sketch Is Nothing Then
        '        If Not sketch.PlanarEntity Is Nothing Then
        '            If TypeOf sketch.PlanarEntity Is Face Then
        '                GetParentFromProfile = sketch.PlanarEntity.CreatedByFeature
        '            End If
        '        End If
        '    End If
        'End Function

        'Private Function IsChild(child As PartFeature, parent As PartFeature) As Boolean

        '    IsChild = False
        '    Dim parentFeature As PartFeature = Nothing

        '    If TypeOf child Is ExtrudeFeature Then
        '        Dim extrude As ExtrudeFeature = child
        '        parentFeature = GetParentFromProfile(extrude.Profile)

        '    ElseIf TypeOf child Is RevolveFeature Then
        '        Dim revolve As RevolveFeature = child
        '        parentFeature = GetParentFromProfile(revolve.Profile)

        '    ElseIf TypeOf child Is SweepFeature Then
        '        Dim sweep As SweepFeature = child
        '        parentFeature = GetParentFromProfile(sweep.Profile)

        '    ElseIf TypeOf child Is HoleFeature Then
        '        Dim hole As HoleFeature = child
        '        parentFeature = hole.PlacementDefinition.Parent

        '    Else
        '        ' Generic way of getting parent via Faces
        '        Dim faces As Inventor.Faces = child.Faces
        '        For Each face As Inventor.Face In faces
        '            parentFeature = face.CreatedByFeature
        '            Debug.Print(parentFeature.Name)
        '            If parentFeature Is parent Then ' found the match
        '                IsChild = True
        '                Exit Function
        '            End If
        '        Next
        '    End If

        '    If parentFeature Is parent Then ' found the match
        '        IsChild = True
        '    End If

        'End Function
        'Private Sub FindDependentFeatures(ByVal oFeature As PartFeature, ByRef childList As ObjectCollection)

        '    Debug.Print("Finding Children for " & oFeature.Name)

        '    Dim allFeatures As Inventor.PartFeatures
        '    allFeatures = _invApp.ActiveDocument.ComponentDefinition.Features

        '    Dim toStartTraverse As Boolean = False

        '    Dim ifeat As PartFeature
        '    For Each ifeat In allFeatures
        '        'Debug.Print(ifeat.Name)

        '        If Not ifeat Is Nothing And ifeat.Equals(oFeature) Then ' till oFeature skip, as children are afterwards
        '            toStartTraverse = True
        '            Continue For ' next one is the actual start for the search...re-look to optimize
        '        ElseIf toStartTraverse = False Then
        '            Continue For
        '        End If

        '        Dim pFeature As PartFeature = Nothing

        '        If toStartTraverse And Not ifeat Is Nothing And TypeOf ifeat Is PartFeature Then

        '            If IsChild(ifeat, oFeature) = True Then

        '                '============== RECURSION =======================
        '                'FindDependentFeatures(ifeat, childList) ' for now only one level

        '                childList.Add(ifeat)
        '            End If

        '        End If
        '    Next

        '    'Debug.Print(childList.Count)

        'End Sub


        ' Utility functions ----------------------------------------------------------------------

        'Private Function UnionBoundingBoxes(ByVal box As Box, ByVal box1 As Box) As Box
        '    Dim result As Inventor.Box = box

        '    If box1 Is Nothing Then
        '        UnionBoundingBoxes = result
        '        Exit Function
        '    End If

        '    'BAD CHECK, but for now

        '    If ((box1.MinPoint.X < box.MinPoint.X) And _
        '        (box1.MinPoint.Y < box.MinPoint.Y) And _
        '        (box1.MinPoint.Z < box.MinPoint.Z)) Then
        '        result.MinPoint = box1.MinPoint
        '    End If

        '    If ((box1.MaxPoint.X > box.MaxPoint.X) And _
        '        (box1.MaxPoint.Y > box.MaxPoint.Y) And _
        '        (box1.MaxPoint.Z > box.MaxPoint.Z)) Then
        '        result.MaxPoint = box1.MaxPoint
        '    End If

        '    UnionBoundingBoxes = result

        'End Function

        'Private Function FindUnionedBoundingBox(ByVal oFeature As PartFeature, ByRef oList As ObjectCollection) As Inventor.Box
        '    Dim box As Inventor.Box = oFeature.RangeBox

        '    If oList.Count = 0 Then
        '        FindUnionedBoundingBox = box
        '        Exit Function
        '    End If

        '    'Debug.Print("FindUnionedBoundingBox: Parent Box size = " & box.MinPoint.DistanceTo(box.MaxPoint))

        '    ' traverse and collect BB
        '    Dim oObj As Object
        '    For Each oObj In oList
        '        If Not oObj Is Nothing Then
        '            If TypeOf oObj Is PartFeature Then
        '                Dim pFeat As PartFeature
        '                pFeat = oObj
        '                If Not pFeat.Name.Equals(oFeature.Name) Then
        '                    Debug.Print(" has child " & pFeat.Name)
        '                    'Debug.Print("\t Child Box size = " & pFeat.RangeBox.MinPoint.DistanceTo(pFeat.RangeBox.MaxPoint))
        '                    box = UnionBoundingBoxes(box, pFeat.RangeBox)
        '                End If
        '            End If
        '        End If
        '    Next

        '    'Debug.Print("\t Union Box size = " & box.MinPoint.DistanceTo(box.MaxPoint))

        '    FindUnionedBoundingBox = box
        'End Function


        'Private Sub CreateImage(ByVal FileName As String)

        '    ' Create a new camera. 
        '    Dim cam As Inventor.Camera
        '    cam = _invApp.TransientObjects.CreateCamera()

        '    Dim oCompDef As Inventor.ComponentDefinition
        '    oCompDef = _invApp.ActiveDocument.ComponentDefinition


        '    ' Associate the document with the camera. 
        '    cam.SceneObject = oCompDef

        '    ' Define the camera and apply the changes. 
        '    cam.ViewOrientationType = _
        '         Inventor.ViewOrientationTypeEnum.kIsoTopRightViewOrientation
        '    cam.Fit()
        '    cam.ApplyWithoutTransition()

        '    'cam.SaveAsBitmap(FileName + ".png", 800, 600) '1126, 533

        '    'Save the result, defining the background color of the image. WHITE GRADIENT
        '    cam.SaveAsBitmap(FileName + ".png", 800, 600, _
        '            _invApp.TransientObjects.CreateColor(255, 255, 255), _
        '           _invApp.TransientObjects.CreateColor(255, 255, 255))

        '    'Save the result, defining the background color of the image. BLUE GRADIENT
        '    'cam.SaveAsBitmap(FileName + ".png", 800, 600, _
        '    '        _invApp.TransientObjects.CreateColor(255, 255, 255), _
        '    '        _invApp.TransientObjects.CreateColor(15, 15, 215))

        '    ' Save the result, defining the background color of the image. 
        '    'cam.SaveAsBitmap(FileName + ".bmp", 800, 600, _
        '    '        _invApp.TransientObjects.CreateColor(255, 255, 0), _
        '    '        _invApp.TransientObjects.CreateColor(15, 15, 15))
        'End Sub

        'Private Function GetMaxParameterValue(ByRef feat As PartFeature) As Double
        '    GetMaxParameterValue = 0.0
        '    Dim maxValue As Double = -1.0
        '    For Each param In feat.Parameters
        '        If param.Value > maxValue Then
        '            maxValue = param.Value
        '        End If
        '    Next
        '    GetMaxParameterValue = maxValue
        'End Function

        'Private Function DoesContain(ByRef collection As ObjectCollection, ByRef feat As PartFeature) As Boolean
        '    DoesContain = False
        '    For Each obj As PartFeature In collection
        '        If obj.Equals(feat) Then
        '            DoesContain = True
        '            Exit Function
        '        End If
        '    Next
        'End Function

        ' Suppressibility Assessment ----------------------------------------------------------------------

        Private Function IsConstituentOfPattern(ByVal child As PartFeature, ByVal parent As PartFeature) As Boolean

            IsConstituentOfPattern = False

            If child Is Nothing Or parent Is Nothing Then
                Exit Function
            End If

            Dim parentFeature As PartFeature = Nothing

            If TypeOf child Is RectangularPatternFeature Then
                Dim pattern As RectangularPatternFeature = child
                Dim parents As ObjectCollection = pattern.ParentFeatures
                For Each obj In parents
                    Dim partf As PartFeature = obj
                    If Not partf Is Nothing Then
                        parentFeature = partf
                        Exit For
                    End If
                Next

            ElseIf TypeOf child Is CircularPatternFeature Then
                Dim pattern As CircularPatternFeature = child
                Dim parents As ObjectCollection = pattern.ParentFeatures
                For Each obj In parents
                    Dim partf As PartFeature = obj
                    If Not partf Is Nothing Then
                        parentFeature = partf
                        Exit For
                    End If
                Next
            End If

            If parentFeature Is parent Then ' found the match
                IsConstituentOfPattern = True
            End If

        End Function

        Private Function IsPrimaryFeature(ByRef oFeature As PartFeature) As Boolean

            IsPrimaryFeature = False
            If TypeOf oFeature Is BendFeature Then
                IsPrimaryFeature = True
                Exit Function
            ElseIf TypeOf oFeature Is BendPartFeature Then
                IsPrimaryFeature = True
                Exit Function
            ElseIf TypeOf oFeature Is ContourFlangeFeature Then
                IsPrimaryFeature = True
                Exit Function
                'ElseIf TypeOf oFeature Is CornerFeature Then
                '    IsPrimaryFeature = True
                '    Exit Function
            ElseIf TypeOf oFeature Is FaceFeature Then
                IsPrimaryFeature = True
                Exit Function
            ElseIf TypeOf oFeature Is FlangeFeature Then
                IsPrimaryFeature = True
                Exit Function
            End If

        End Function

        Private Function SpecialFeatureSizes(ByRef oFeature As PartFeature) As Double
            SpecialFeatureSizes = 0.0
            If TypeOf oFeature Is HoleFeature Then
                Dim hole As HoleFeature = oFeature
                If Not hole.HoleDiameter Is Nothing Then
                    SpecialFeatureSizes = hole.HoleDiameter.Value
                End If
                Exit Function
            ElseIf TypeOf oFeature Is CutFeature Then
                Dim cut As CutFeature = oFeature
                SpecialFeatureSizes = Math.Sqrt(cut.Definition.Profile.RegionProperties.Area)
                Exit Function
            ElseIf TypeOf oFeature Is iFeature Then
                Dim ifeat As iFeature = oFeature
                Dim bbDiagonal As Double = 0.0
                Dim pBB As Inventor.Box
                pBB = ifeat.RangeBox
                bbDiagonal = pBB.MinPoint.DistanceTo(pBB.MaxPoint)
                SpecialFeatureSizes = Math.Sqrt(bbDiagonal)
                Exit Function
            End If

        End Function

        Private Function IsSecondaryFeature(ByRef oFeature As PartFeature, ByRef featureSize As Double) As Boolean
            IsSecondaryFeature = False
            If TypeOf oFeature Is BossFeature Then
                Dim boss As BossFeature = oFeature
                featureSize = m_Utilities.GetMaxParameterValue(boss) 'boss.Parameters(1).Value m_Utilities
                If featureSize > 0.0 Then
                    IsSecondaryFeature = True
                End If
                Exit Function
            ElseIf TypeOf oFeature Is ChamferFeature Then
                Dim chamfer As ChamferFeature = oFeature
                featureSize = m_Utilities.GetMaxParameterValue(chamfer) 'chamfer.Parameters(1).Value
                If featureSize > 0.0 Then
                    IsSecondaryFeature = True
                End If
                Exit Function
            ElseIf TypeOf oFeature Is CornerChamferFeature Then
                Dim cchamfer As CornerChamferFeature = oFeature
                featureSize = m_Utilities.GetMaxParameterValue(cchamfer) 'cchamfer.Parameters(1).Value
                If featureSize > 0.0 Then
                    IsSecondaryFeature = True
                End If
                Exit Function
            ElseIf TypeOf oFeature Is CornerRoundFeature Then
                Dim round As CornerRoundFeature = oFeature
                featureSize = 2 * (m_Utilities.GetMaxParameterValue(round)) 'round.Parameters(1).Value
                If featureSize > 0.0 Then
                    IsSecondaryFeature = True
                End If
                Exit Function
            ElseIf TypeOf oFeature Is CutFeature Then
                Dim cut As CutFeature = oFeature
                featureSize = Math.Sqrt(cut.Definition.Profile.RegionProperties.Area)
                'featureSize = cut.Parameters(1).Value ' 1st param gives 0 value
                If featureSize > 0.0 Then
                    IsSecondaryFeature = True
                End If
                Exit Function
            ElseIf TypeOf oFeature Is EmbossFeature Then
                Dim emboss As EmbossFeature = oFeature
                featureSize = m_Utilities.GetMaxParameterValue(emboss) 'emboss.Parameters(1).Value
                If featureSize > 0.0 Then
                    IsSecondaryFeature = True
                End If
                Exit Function
            ElseIf TypeOf oFeature Is FilletFeature Then
                Dim fillet As FilletFeature = oFeature
                featureSize = 2 * (m_Utilities.GetMaxParameterValue(fillet)) 'fillet.Parameters(1).Value
                If featureSize > 0.0 Then
                    IsSecondaryFeature = True
                End If
                Exit Function
            ElseIf TypeOf oFeature Is FoldFeature Then
                Dim fold As FoldFeature = oFeature
                featureSize = m_Utilities.GetMaxParameterValue(fold) 'fold.Parameters(1).Value
                If featureSize > 0.0 Then
                    IsSecondaryFeature = True
                End If
                Exit Function
            ElseIf TypeOf oFeature Is HoleFeature Then
                Dim hole As HoleFeature = oFeature
                If Not hole.HoleDiameter Is Nothing Then
                    featureSize = hole.HoleDiameter.Value
                Else
                    featureSize = m_Utilities.GetMaxParameterValue(hole) 'hole.Parameters(1).Value
                End If
                If featureSize > 0.0 Then
                    IsSecondaryFeature = True
                End If
                Exit Function
            ElseIf TypeOf oFeature Is iFeature Then
                Dim ifeat As iFeature = oFeature
                featureSize = m_Utilities.GetMaxParameterValue(ifeat) 'ifeat.Parameters(1).Value
                If featureSize > 0.0 Then
                    IsSecondaryFeature = True
                End If
                Exit Function
            End If
        End Function

        Private Function IsTertiaryFeature(ByRef oFeature As PartFeature) As Boolean

            IsTertiaryFeature = False
            If TypeOf oFeature Is HemFeature Then
                IsTertiaryFeature = True
                Exit Function
            ElseIf TypeOf oFeature Is LipFeature Then
                IsTertiaryFeature = True
                Exit Function
            ElseIf TypeOf oFeature Is RestFeature Then
                IsTertiaryFeature = True
                Exit Function
            ElseIf TypeOf oFeature Is CornerFeature Then
                IsTertiaryFeature = True
                Exit Function
            End If
        End Function

        Private Function IsGroupFeature(ByRef oFeature As PartFeature, ByRef featureSize As Double, ByRef parent As PartFeature) As Boolean
            IsGroupFeature = False
            If TypeOf oFeature Is CircularPatternFeature Then
                IsGroupFeature = True
                Exit Function
            ElseIf TypeOf oFeature Is GrillFeature Then
                IsGroupFeature = True
                Exit Function
            ElseIf TypeOf oFeature Is MirrorFeature Then
                Dim mirr As MirrorFeature = oFeature
                If mirr.MirrorOfBody = True Then
                    ' TBD
                Else
                    parent = mirr.ParentFeatures.Item(1)
                    Dim parentsize As Double = m_Utilities.GetMaxParameterValue(parent) 'parent.Parameters(1).Value
                    If parentsize = 0.0 Then
                        parentsize = SpecialFeatureSizes(parent)
                    End If
                    featureSize = parentsize * mirr.PatternElements.Count
                    If featureSize > 0.0 Then
                        IsGroupFeature = True
                    End If
                    Exit Function
                End If
            ElseIf TypeOf oFeature Is RectangularPatternFeature Then
                Dim rectpat As RectangularPatternFeature = oFeature
                parent = rectpat.ParentFeatures.Item(1)
                Dim parentsize As Double = m_Utilities.GetMaxParameterValue(parent) 'parent.Parameters(1).Value
                If parentsize = 0.0 Then
                    parentsize = SpecialFeatureSizes(parent)
                End If
                featureSize = parentsize * rectpat.PatternElements.Count
                If featureSize > 0.0 Then
                    IsGroupFeature = True
                End If
                Exit Function
            End If
        End Function

        Private Function IsNegativeFeature(ByRef oFeature As PartFeature) As Boolean
            IsNegativeFeature = False
            If TypeOf oFeature Is CutFeature Then
                IsNegativeFeature = True
                Exit Function
            ElseIf TypeOf oFeature Is HoleFeature Then
                IsNegativeFeature = True
                Exit Function
                ' EVEN if Extrude has inner holes, it can be a significantly big feature. It can not be added for suppression as it.
                ' At most its inner loops can be suppressed. But then, these holes will need to be converted into dormant bodies, significant logic.
                ' Actually profile with holes is easy to compute midsurface for, so let it stay as is
                'ElseIf TypeOf oFeature Is ExtrudeFeature Then
                '    ' find if it is a negative boolean extrude, or a positive with a hole inside
                '    IsNegativeFeature = IsExtrudeNegativeOrHasHoles(oFeature)
            End If
        End Function

        Private Function IsSheetMetalFeatureSupressible2(ByRef oFeature As PartFeature) As Boolean
            IsSheetMetalFeatureSupressible2 = False
            Dim param As Double = 2 * m_sizeD ' some initialization with high value
            Dim parent As PartFeature = Nothing

            If Not oFeature Is Nothing Then
                ' Do Not Suppress Primary features at all, so no Size checking
                If IsPrimaryFeature(oFeature) Then
                    IsSheetMetalFeatureSupressible2 = False
                    sw.WriteLine(oFeature.Name & " is Primary => Not Suppressible")
                    ' Do Suppress Tertiary features compulsorily, so no Size checking
                ElseIf IsTertiaryFeature(oFeature) Then
                    IsSheetMetalFeatureSupressible2 = True
                    sw.WriteLine(oFeature.Name & " is Tertiary => Suppressible")
                ElseIf IsSecondaryFeature(oFeature, param) Then
                    If param < m_sizeD Then
                        IsSheetMetalFeatureSupressible2 = True
                        sw.WriteLine(oFeature.Name & " is Secondary with size = " & param.ToString("#.##") & " => Suppressible")
                    Else
                        sw.WriteLine(oFeature.Name & " is Secondary with size = " & param.ToString("#.##") & " => Not Suppressible")
                    End If
                ElseIf IsGroupFeature(oFeature, param, parent) Then
                    If param < m_sizeD Then
                        IsSheetMetalFeatureSupressible2 = True
                        sw.WriteLine(oFeature.Name & " is Group with size = " & param.ToString("#.##") & " => Suppressible")
                    Else
                        ' remove parent is already in the suppression list
                        If m_Utilities.DoesContain(m_suppressableSFeatures, parent) = True Then
                            m_suppressableSFeatures.RemoveByObject(parent)
                            sw.WriteLine(oFeature.Name & " is Group with size = " & param.ToString("#.##") & " => Not Suppressible")
                        End If
                    End If
                End If
            End If
        End Function

        Private Function IsSheetMetalFeatureSupressible(ByRef oFeature As PartFeature) As Boolean

            IsSheetMetalFeatureSupressible = False

            If Not oFeature Is Nothing Then

                ' Total feature list under Inventor.SheetMetalFeatures interface
                ' Those marked "->" are considred for suppression here
                ' Rest will be handled Size-wise in generic way

                ' AliasFreeFormFeature
                ' BendFeature
                ' BendPartFeature
                ' BossFeature
                ' BoundaryPatchFeature
                ' ChamferFeature  ->
                ' CircularPatternFeature
                ' ClientFeature
                ' CoilFeature
                ' CombineFeature
                ' ContourFlangeFeature
                ' ContourRollFeature
                ' CoreCavityFeature
                ' CornerChamferFeature ->
                ' CornerFeature
                ' CornerRoundFeature  ->
                ' CutFeature  ->
                ' DecalFeature
                ' DeletefaceFeature
                ' EmbossFeature ->
                ' ExtendFeature
                ' ExtrudeFeature
                ' FaceDraftFeature
                ' FaceFeature
                ' FaceOffsetFeature
                ' FilletFeature   ->
                ' FlangeFeature
                ' FoldFeature
                ' GrillFeature
                ' HemFeature  ->
                ' HoleFeature ->
                ' KnitFeature
                ' LipFeature
                ' LoftedFlageFeature
                ' LoftFeature
                ' MidsurfaceFeature
                ' MirrorFeature
                ' MoveFaceFeature
                ' MoveFeature
                ' NonParametricBaseFeature
                ' PunchToolFeature
                ' RectangularPatternFeature
                ' RefoldFeature
                ' ReplaceFaceFeature
                ' RestFeature
                ' RevolveFeature
                ' RibFeature
                ' RipFeature
                ' RuleFilletFeature
                ' SculptFeature
                ' ShellFeature
                ' SnapFitFeature
                ' SplitFeature
                ' SweepFeature
                ' ThickenFeature
                ' ThreadFeature
                ' TrimFeature
                ' UnfoldFeature
                '

                If TypeOf oFeature Is HoleFeature Then
                    Dim diameter As Double = 2 * m_sizeD ' some initialization with high value
                    If Not oFeature.HoleDiameter Is Nothing Then
                        diameter = oFeature.HoleDiameter.Value
                    Else
                        diameter = oFeature.Parameters(1).Value
                    End If
                    If diameter < m_sizeD Then
                        IsSheetMetalFeatureSupressible = True
                    End If

                ElseIf TypeOf oFeature Is FoldFeature Then
                    Dim length As Double
                    length = oFeature.Parameters(1).Value
                    If length < m_sizeD Then
                        IsSheetMetalFeatureSupressible = True
                    End If

                ElseIf TypeOf oFeature Is FilletFeature Then
                    Dim radius As Double
                    radius = oFeature.Parameters(1).Value
                    If (2 * radius) < m_sizeD Then
                        IsSheetMetalFeatureSupressible = True
                    End If

                ElseIf TypeOf oFeature Is CornerRoundFeature Then
                    Dim radius As Double
                    radius = oFeature.Parameters(1).Value
                    If (2 * radius) < m_sizeD Then
                        IsSheetMetalFeatureSupressible = True
                    End If

                ElseIf TypeOf oFeature Is ChamferFeature Then
                    Dim side As Double
                    side = oFeature.Parameters(1).Value
                    If side < m_sizeD Then
                        IsSheetMetalFeatureSupressible = True
                    End If

                ElseIf TypeOf oFeature Is CornerChamferFeature Then
                    Dim side As Double
                    side = oFeature.Parameters(1).Value
                    If side < m_sizeD Then
                        IsSheetMetalFeatureSupressible = True
                    End If

                ElseIf TypeOf oFeature Is EmbossFeature Then
                    IsSheetMetalFeatureSupressible = True 'irrespective of size

                ElseIf TypeOf oFeature Is HemFeature Then
                    IsSheetMetalFeatureSupressible = True 'irrespective of size

                ElseIf TypeOf oFeature Is LipFeature Then
                    IsSheetMetalFeatureSupressible = True 'irrespective of size

                ElseIf TypeOf oFeature Is RestFeature Then
                    IsSheetMetalFeatureSupressible = True 'irrespective of size

                ElseIf TypeOf oFeature Is GrillFeature Then
                    IsSheetMetalFeatureSupressible = True 'irrespective of size

                ElseIf TypeOf oFeature Is CornerChamferFeature Then
                    IsSheetMetalFeatureSupressible = True 'irrespective of size

                Else

                End If

            End If

        End Function

        Private Sub MergeParentChildClusters()

            For Each iObj In m_clusters
                Dim iCluster As Cluster = iObj
                If iCluster.m_MarkForDelete = True Then
                    Continue For
                End If
                For Each jObj In m_clusters
                    Dim jCluster As Cluster = jObj
                    If jCluster.m_MarkForDelete = True Then
                        Continue For
                    End If
                    If Not Object.ReferenceEquals(iObj, jObj) Then
                        Dim iOwnerFeature As PartFeature = iCluster.m_clusterFeatures.Item(0)
                        Dim jOwnerFeature As PartFeature = jCluster.m_clusterFeatures.Item(0)
                        If IsConstituentOfPattern(iOwnerFeature, jOwnerFeature) Or IsConstituentOfPattern(jOwnerFeature, iOwnerFeature) Then
                            iCluster.MergeCluster(jCluster)
                        End If
                    End If
                Next
            Next

        End Sub

        Private Sub CollectRemnantSuppressableFeatures()

            'If _initialized = False Then
            '    Exit Sub
            'End If

            ' Cluster is a collection of remnant (whats remaining in final brep) faces belonging to a particular feature
            ' Down the road we will see if even the dependencies can be clubbed together or not

            Dim pFaces As Faces = _invApp.ActiveDocument.ComponentDefinition.SurfaceBodies.Item(1).Faces
            If Not pFaces Is Nothing Then
                For Each pFace In pFaces
                    Dim found As Boolean = False
                    Dim faceOwnerFeature As PartFeature = pFace.CreatedByFeature

                    ' Each face is test for containment in each cluster
                    ' Add if face's owner feature is in Cluster
                    For Each oObj In m_clusters
                        Dim pCluster As Cluster = oObj
                        Dim faceOfThisCluster As Boolean = False
                        If Not faceOwnerFeature Is Nothing Then
                            faceOfThisCluster = pCluster.IsAmongstFeatures(faceOwnerFeature)
                        End If
                        If faceOfThisCluster = True Then
                            pCluster.AddFaceAndOwnerFeature(pFace) 'will not add if duplicate
                            found = True
                            Exit For
                        End If
                    Next

                    If found = False Then   ' if the Face is not in any existsing clusters, create new and add to that
                        Dim nCluster As Cluster = New Cluster()
                        nCluster.AddFaceAndOwnerFeature(pFace)
                        m_clusters.Add(nCluster)
                    End If
                Next
            End If

            ' If parent-child (only for patterns), MERGE
            MergeParentChildClusters()
            sw.WriteLine("=================== Remnant Volume  ==========================")

            ' Calculate Cluster Size, which is the Unioned BB of the remnant faces, there are two other methods:
            '   - Just summation of remnant face areas (crude, but quick method)
            '   - Actual volume by suppressing and unsupressing the feature and taking volume difference
            For Each pCluster In m_clusters
                If Not pCluster.m_MarkForDelete = True Then
                    Dim size As Double = pCluster.GetSize()
                    pCluster.WriteToFile(sw)
                    If size < m_sizeD Then
                        ' Add all the features in the cluster
                        For Each oFeature In pCluster.m_clusterFeatures
                            If Not IsPrimaryFeature(oFeature) Then
                                m_suppressableRFeatures.Add(oFeature)
                                sw.WriteLine(" => Suppressed ")
                            Else
                                sw.WriteLine(" => Not Suppressed as it is Primary")
                            End If
                        Next
                    Else
                        sw.WriteLine(" => Not Suppressed ")
                    End If
                End If
            Next
        End Sub

        Private Sub CollectSheetMetalSuppressibleFeatures(ByVal collectDormantAsWell As Boolean)

            'If _initialized = False Then
            '    Exit Sub
            'End If
            sw.WriteLine("=================== Sheet Metal ==========================")
            Dim sFeatures As Inventor.PartFeatures
            sFeatures = _invApp.ActiveDocument.ComponentDefinition.Features

            Dim oFeature As PartFeature
            For Each oFeature In sFeatures
                'Debug.Print(oFeature.Name)

                'If IsSheetMetalFeatureSupressible(oFeature) = True Then
                If IsSheetMetalFeatureSupressible2(oFeature) = True Then
                    m_suppressableSFeatures.Add(oFeature)
                End If
            Next
        End Sub

        Private Sub CollectBigNegativeSuppressibleFeatures()

            'If _initialized = False Then
            '    Exit Sub
            'End If
            sw.WriteLine("=================== Dorman features ==========================")
            Dim sFeatures As Inventor.PartFeatures
            sFeatures = _invApp.ActiveDocument.ComponentDefinition.Features

            Dim oFeature As PartFeature
            For Each oFeature In sFeatures
                'Debug.Print(oFeature.Name)
                If m_Utilities.DoesContain(m_suppressableSFeatures, oFeature) Then
                    Continue For
                ElseIf IsNegativeFeature(oFeature) = True Then
                    Dim newDormantToolBodyFeature As PartFeature = ComputeNewToolBodyFeature(oFeature)
                    If Not newDormantToolBodyFeature Is Nothing Then
                        m_suppressableDFeatures.Add(newDormantToolBodyFeature)
                        ' Mostly I will be creating extrudes for such bodies TEMP TEMP
                        Dim dormantExtrudeToolBody As ExtrudeFeature = newDormantToolBodyFeature
                        Dim affectedbodies As ObjectCollection = dormantExtrudeToolBody.Definition.AffectedBodies
                        For Each bdy As SurfaceBody In affectedbodies
                            m_dormantToolBodies.Add(bdy)
                        Next
                    End If
                    m_suppressableSFeatures.Add(oFeature) ' add here as well so that it gets suppressed 
                End If
            Next

        End Sub

        Private Sub SuppressFeatures(ByVal features As ObjectCollection, Optional ByVal suppressing As Boolean = True)

            'set EndOfPart to Top, then set Suppressed, then restore back, to improve performance
            Dim oCompDef As Inventor.ComponentDefinition
            oCompDef = _invApp.ActiveDocument.ComponentDefinition
            If TypeOf oCompDef Is Inventor.AssemblyComponentDefinition Then
                oCompDef.SetEndOfFeaturesToTopOrBottom(True)
            ElseIf TypeOf oCompDef Is Inventor.PartComponentDefinition Then
                m_numFacesBefore = oCompDef.SurfaceBodies.Item(1).Faces.Count
                oCompDef.SetEndOfPartToTopOrBottom(True)
            End If

            ' Suppression
            Dim oObj As Object

            For Each oObj In features
                If Not oObj Is Nothing Then
                    If TypeOf oObj Is PartFeature Then
                        Dim oFeature As PartFeature = oObj
                        oFeature.Suppressed = suppressing
                    End If
                End If
            Next


            'end restored
            Dim ocCompDef As Inventor.ComponentDefinition
            ocCompDef = _invApp.ActiveDocument.ComponentDefinition
            If TypeOf ocCompDef Is Inventor.AssemblyComponentDefinition Then
                ocCompDef.SetEndOfFeaturesToTopOrBottom(False)
            ElseIf TypeOf ocCompDef Is Inventor.PartComponentDefinition Then
                ocCompDef.SetEndOfPartToTopOrBottom(False)
                'collect stats after
                Dim body As SurfaceBody = Nothing
                If oCompDef.SurfaceBodies.Count > 0 Then
                    body = ocCompDef.SurfaceBodies.Item(1)
                    If Not body Is Nothing And Not body.Faces Is Nothing Then
                        m_numFacesAfter = body.Faces.Count
                    End If
                Else
                    MsgBox("Error : Lost the Brep body")
                End If
            End If

            ' See if any additional feature has been suppressed
            Dim allFeatures As Inventor.PartFeatures = _invApp.ActiveDocument.ComponentDefinition.Features
            Dim newSuppressed As String = ""
            For Each oObj In allFeatures
                If Not oObj Is Nothing Then
                    If TypeOf oObj Is PartFeature Then
                        Dim jfeat As PartFeature = oObj
                        Dim suppressedInTree As Boolean = jfeat.Suppressed
                        Dim isUnfoldFeature As Boolean = TypeOf jfeat Is UnfoldFeature
                        Dim isPresentInGivenList As Boolean = False
                        For Each ifeat In features
                            Dim oFeature As PartFeature = ifeat
                            If jfeat.Name = oFeature.Name Then
                                isPresentInGivenList = True
                            End If
                        Next
                        If suppressedInTree And Not isPresentInGivenList And Not isUnfoldFeature Then
                            newSuppressed = newSuppressed + " " + jfeat.Name
                        End If
                    End If
                End If
            Next
            If newSuppressed.Length > 1 Then
                Debug.Print("Additional un/suppresssions were " & newSuppressed)
            End If
        End Sub

        Public Sub OpenForWrite(ByVal p1 As String)
            sw = New IO.StreamWriter(p1)
        End Sub

        Public Sub CloseWrittenFile()
            sw.Close()
        End Sub

        Public Sub SuppressAllUnfoldFeatures()
            '--------------------------------------------------------------------------------------------------

            ' Suppress ALL Unfold features so that part comes in natural shape
            If _invApp.ActiveDocument Is Nothing Then
                Exit Sub
            End If

            Dim allFeatures As Inventor.PartFeatures = _invApp.ActiveDocument.ComponentDefinition.Features
            Dim suppressableUnfoldFeatures As ObjectCollection = _invApp.TransientObjects.CreateObjectCollection

            Dim ifeat As PartFeature
            For Each ifeat In allFeatures
                If TypeOf ifeat Is UnfoldFeature Then
                    Dim unfoldfeat As UnfoldFeature = ifeat
                    If Not unfoldfeat.Suppressed Then
                        suppressableUnfoldFeatures.Add(ifeat)
                    End If
                End If
            Next

            If (suppressableUnfoldFeatures.Count > 0) Then
                SuppressFeatures(suppressableUnfoldFeatures)
                suppressableUnfoldFeatures.Clear()
            End If

        End Sub

        Public Function CalculatePartSize() As Double
            ' BB method
            Dim bbDiagonal As Double = 0.0
            Dim pBB As Inventor.Box
            pBB = _invApp.ActiveDocument.ComponentDefinition.RangeBox
            bbDiagonal = pBB.MinPoint.DistanceTo(pBB.MaxPoint)

            ' Face Area Method
            Dim brepArea As Double = 0.0
            Dim body As SurfaceBody = Nothing
            If _invApp.ActiveDocument.ComponentDefinition.SurfaceBodies.Count > 0 Then
                body = _invApp.ActiveDocument.ComponentDefinition.SurfaceBodies.Item(1)
                If Not body Is Nothing And Not body.Faces Is Nothing Then
                    For Each face As Inventor.Face In body.Faces
                        brepArea = brepArea + face.Evaluator.Area
                    Next
                End If
            End If

            brepArea = Math.Sqrt(brepArea)
            m_partSize = brepArea ' CHOICE
            CalculatePartSize = m_partSize
        End Function

        Public Sub WriteToFile(ByVal p1 As String)
            sw.WriteLine(p1)
        End Sub

        Public Function CollectAndHighlightSuppressibleSheetMetalFeatures(ByVal isInteractive As Boolean, ByVal collectDormantAsWell As Boolean) As Boolean

            CollectAndHighlightSuppressibleSheetMetalFeatures = False

            ' If Preview button is clicked after changing %age value, while part remaining the same
            ' ClearFeatureListsAndClusters()
            Debug.Print("============================ Preview S =========================")
            m_suppressableSFeatures = _invApp.TransientObjects.CreateObjectCollection
            m_suppressableDFeatures = _invApp.TransientObjects.CreateObjectCollection
            m_dormantToolBodies = _invApp.TransientObjects.CreateObjectCollection

            'Create a variable for start time:
            Dim TimerStart As DateTime
            TimerStart = Now

            ' First Pass : Type based selection
            CollectSheetMetalSuppressibleFeatures(collectDormantAsWell)

            If collectDormantAsWell Then
                CollectBigNegativeSuppressibleFeatures()
            End If


            Dim TimeSpent As System.TimeSpan
            TimeSpent = Now.Subtract(TimerStart)

            If isInteractive Then
                MsgBox("Collected " & m_suppressableSFeatures.Count & " and " & m_suppressableDFeatures.Count & " SheetMetal type features in " & TimeSpent.TotalSeconds & " seconds")
            End If

            If m_highlightedSMFeatures Is Nothing Then
                m_highlightedSMFeatures = _invApp.ActiveDocument.HighlightSets.Add
            End If
            m_highlightedSMFeatures.Color = _invApp.TransientObjects.CreateColor(255, 0, 0)

            ' Highlight the features.
            Dim oFeature As PartFeature
            For Each oFeature In m_suppressableSFeatures
                If Not oFeature Is Nothing Then
                    Debug.Print(oFeature.Name)
                    m_highlightedSMFeatures.AddItem(oFeature)
                End If
            Next

            If m_highlightedDMFeatures Is Nothing Then
                m_highlightedDMFeatures = _invApp.ActiveDocument.HighlightSets.Add
            End If
            m_highlightedDMFeatures.Color = _invApp.TransientObjects.CreateColor(0, 255, 0)

            ' Highlight the features.
            For Each oFeature In m_suppressableDFeatures
                If Not oFeature Is Nothing Then
                    Debug.Print(oFeature.Name)
                    m_highlightedDMFeatures.AddItem(oFeature)
                End If
            Next

            If m_highlightedSMFeatures.Count > 0 Or m_highlightedDMFeatures.Count > 0 Then
                CollectAndHighlightSuppressibleSheetMetalFeatures = True
            End If
            'MsgBox("Number of features in suppress list are " & m_suppressableFeatures.Count)

        End Function

        Public Function CollectAndHighlightSuppressibleRemnantFeatures(ByRef isInteractive As Boolean) As Boolean

            CollectAndHighlightSuppressibleRemnantFeatures = False

            ' If Preview button is clicked after changing %age value, while part remaining the same
            ' ClearFeatureListsAndClusters()

            m_suppressableRFeatures = _invApp.TransientObjects.CreateObjectCollection


            'Create a variable for start time:
            Dim TimerStart As DateTime
            TimerStart = Now


            ' Second Pass : Remnant size based selection
            CollectRemnantSuppressableFeatures()


            Dim TimeSpent As System.TimeSpan
            TimeSpent = Now.Subtract(TimerStart)

            If isInteractive Then
                MsgBox("Suppressed " & m_suppressableRFeatures.Count & " Features by Remnant Method in " & TimeSpent.TotalSeconds & " seconds")
            End If

            If m_highlightedSMFeatures Is Nothing Then
                m_highlightedSMFeatures = _invApp.ActiveDocument.HighlightSets.Add
            End If


            ' Highlight the features.
            Dim oFeature As PartFeature
            For Each oFeature In m_suppressableRFeatures
                If Not oFeature Is Nothing Then
                    Debug.Print(oFeature.Name)
                    m_highlightedSMFeatures.AddItem(oFeature)
                End If
            Next

            If m_highlightedSMFeatures.Count > 0 Then
                CollectAndHighlightSuppressibleRemnantFeatures = True
            End If
            'MsgBox("Number of features in suppress list are " & m_suppressableFeatures.Count)
        End Function

        Public Sub SuppressSheetMetalFeatures(ByRef isInteractive As Boolean, ByRef dumpImages As Boolean)
            If Not m_highlightedSMFeatures Is Nothing Then
                m_highlightedSMFeatures.Clear()
            End If

            If Not m_highlightedDMFeatures Is Nothing Then
                m_highlightedDMFeatures.Clear()
            End If

            If _invApp.ActiveDocument.ComponentDefinition Is Nothing Then
                Exit Sub
            End If

            Dim iptFileName As String = _invApp.ActiveDocument.DisplayName
            If dumpImages Then
                m_Utilities.CreateImage(iptFileName + "_OriginalPart")
            End If

            SuppressFeatures(m_suppressableSFeatures)

            If dumpImages Then
                m_Utilities.CreateImage(iptFileName + "_SMSpecific_After")
            End If

            If isInteractive Then
                MsgBox("Num Faces before were " & m_numFacesBefore & " and now Num Faces are " & m_numFacesAfter)
            End If

            SuppressFeatures(m_suppressableDFeatures)

            If dumpImages Then
                m_Utilities.CreateImage(iptFileName + "_DMSpecific_After")
            End If

            'If isInteractive Then
            '    MsgBox("Num Faces before were " & m_numFacesBefore & " and now Num Faces are " & m_numFacesAfter)
            'End If
            ' NOW WORK is over, lets clean the lists
            ' ClearFeatureListsAndClusters()

        End Sub

        Public Sub SuppressRemnantFeatures(ByRef isInteractive As Boolean, ByRef dumpImages As Boolean)
            If Not m_highlightedSMFeatures Is Nothing Then
                m_highlightedSMFeatures.Clear()
            End If

            If _invApp.ActiveDocument.ComponentDefinition Is Nothing Then
                Exit Sub
            End If

            Dim iptFileName As String = _invApp.ActiveDocument.DisplayName
            'm_Utilities.CreateImage(iptFileName + "_SMSpecific_After")

            SuppressFeatures(m_suppressableRFeatures)
            If dumpImages Then
                m_Utilities.CreateImage(iptFileName + "_FinalPart")
            End If

            If isInteractive Then
                MsgBox("Num Faces before were " & m_numFacesBefore & " and now Num Faces are " & m_numFacesAfter)
            End If


            ' NOW WORK is over, lets clean the lists
            ' ClearFeatureListsAndClusters()
        End Sub

        Public Sub SuppressDormantFeatures(ByRef isInteractive As Boolean, ByRef dumpImages As Boolean, Optional ByVal suppressing As Boolean = True)
            If Not m_highlightedDMFeatures Is Nothing Then
                m_highlightedDMFeatures.Clear()
            End If

            If _invApp.ActiveDocument.ComponentDefinition Is Nothing Then
                Exit Sub
            End If

            Dim iptFileName As String = _invApp.ActiveDocument.DisplayName
            'm_Utilities.CreateImage(iptFileName + "_SMSpecific_After")

            SuppressFeatures(m_suppressableDFeatures, suppressing)
            If dumpImages Then
                m_Utilities.CreateImage(iptFileName + "_FinalPart")
            End If

            If isInteractive Then
                MsgBox("Num Faces before were " & m_numFacesBefore & " and now Num Faces are " & m_numFacesAfter)
            End If


            ' NOW WORK is over, lets clean the lists
            ' ClearFeatureListsAndClusters()
        End Sub

        Public Sub ComputeDefeaturedPart(Optional ByVal userpercent As Integer = 0, Optional ByVal wrap As Boolean = False)
            SuppressAllUnfoldFeatures()
            m_partSize = CalculatePartSize()
            If userpercent = 0 Then
                m_userSizePercentage = CalculateThresholdPercentage()
            Else
                m_userSizePercentage = userpercent
            End If

            m_sizeD = (m_userSizePercentage / 100.0) * m_partSize
            m_Wrapping = wrap
            CollectAndHighlightSuppressibleSheetMetalFeatures(False, True)
            SuppressSheetMetalFeatures(False, True)
            CollectAndHighlightSuppressibleRemnantFeatures(False)
            SuppressRemnantFeatures(False, True)
            ClearFeatureListsAndClusters(False) ' AVOID clearing dormant features and dormant bodies
            CloseWrittenFile()
        End Sub

        Public Function DefeatureAndReturnDormandFeatures(Optional ByVal userpercent As Integer = 0, Optional ByVal wrap As Boolean = False) As ObjectCollection
            Init()
            ComputeDefeaturedPart(userpercent, wrap)
            SuppressFeatures(m_suppressableDFeatures, False)
            DefeatureAndReturnDormandFeatures = m_suppressableDFeatures
        End Function

        'Private Function GetWorkPlane(planeorig As Object) As WorkPlane
        '    GetWorkPlane = Nothing
        '    If TypeOf planeorig Is Inventor.Face Then
        '        Dim fc As Face = planeorig
        '        Dim pt1 As Inventor.Point = fc.Vertices.Item(1).Point
        '        Dim pt2 As Inventor.Point = fc.Vertices.Item(2).Point
        '        Dim pt3 As Inventor.Point = fc.Vertices.Item(3).Point
        '        Dim wpt1 As WorkPoint = m_compDef.WorkPoints.AddFixed(pt1, True)
        '        Dim wpt2 As WorkPoint = m_compDef.WorkPoints.AddFixed(pt2, True)
        '        Dim wpt3 As WorkPoint = m_compDef.WorkPoints.AddFixed(pt3, True)
        '        'Dim pt As Point = fc.PointOnFace
        '        'Dim vec As UnitVector = GetFaceNormal(fc)
        '        'Dim pln As Plane = _invApp.TransientGeometry.CreatePlane(pt, vec.AsVector)
        '        GetWorkPlane = m_compDef.WorkPlanes.AddByThreePoints(wpt1, wpt2, wpt3, True)
        '    ElseIf TypeOf planeorig Is WorkPlane Then
        '        GetWorkPlane = m_compDef.WorkPlanes.AddByPlaneAndOffset(planeorig, 0.0, True)
        '    End If
        'End Function

        'Private Function CreateNewSketch(ByVal profile As Profile) As PlanarSketch
        '    Dim currentSketch As PlanarSketch = profile.Parent

        '    Dim oProfPath As ProfilePath = Nothing
        '    Dim skt As PlanarSketch = Nothing

        '    For Each oProfPath In profile
        '        Dim pointsCollection As ObjectCollection = _invApp.TransientObjects.CreateObjectCollection()
        '        For Each ent As ProfileEntity In oProfPath
        '            ' IF profile entity is SketchCircle there is no Start Point
        '            Dim pt As Point = currentSketch.SketchToModelSpace(ent.SketchEntity.StartSketchPoint().Geometry)
        '            pointsCollection.Add(pt)
        '        Next
        '        Dim pl As Inventor.Polyline3d = _invApp.TransientGeometry.CreatePolyline3d(pointsCollection)
        '        CreateSketchOutOfFaceBoundary(pl, skt, currentSketch)
        '    Next
        '    CreateNewSketch = skt
        'End Function
        'Private Function CreateNewSketch(faceSketch As PlanarSketch, Optional copyContents As Boolean = False) As PlanarSketch
        '   CreateNewSketch = Nothing

        '    Dim newsketch As PlanarSketch = m_partDoc.ComponentDefinition().Sketches.Add(faceSketch.PlanarEntity)

        '    If copyContents Then
        '        faceSketch.CopyContentsTo(newsketch)
        '    End If

        '    If Not faceSketch.OriginPoint Is Nothing Then
        '        newsketch.OriginPoint = faceSketch.OriginPoint
        '    End If

        '    CreateNewSketch = newsketch
        'End Function
        ''Private Function CreateNewSketch(faceSketch As PlanarSketch) As PlanarSketch
        ''    CreateNewSketch = Nothing
        ''    Dim sketchpts As SketchPoints = faceSketch.SketchPoints
        ''    Dim pl As WorkPlane = GetWorkPlane(faceSketch.PlanarEntity) 'm_compDef.WorkPlanes.AddByPlaneAndOffset(faceSketch.PlanarEntity, 0.0, True)

        ''    Dim newsketch As PlanarSketch = Nothing

        ''    Try
        ''        newsketch = m_compDef.Sketches.Add(pl)
        ''        faceSketch.CopyContentsTo(newsketch)
        ''    Catch ex As Exception
        ''        MsgBox(ex.Message)
        ''    End Try

        ''    CreateNewSketch = newsketch
        ''End Function
        'Private Function CreateNewSketch(fc2 As Face) As PlanarSketch
        '    CreateNewSketch = Nothing
        '    Dim pl As WorkPlane = m_compDef.WorkPlanes.AddByPlaneAndOffset(fc2, 0.0, True)
        '    Dim newsketch As PlanarSketch = m_compDef.Sketches.Add(pl)
        '    For Each ed As Inventor.Edge In fc2.Edges
        '        newsketch.AddByProjectingEntity(ed)
        '    Next
        '    CreateNewSketch = newsketch
        'End Function
        'Private Sub CreateSketchOutOfFaceBoundary(ByVal oPl As Inventor.Polyline3d, ByRef addToSketch As PlanarSketch, Optional ByVal sourceSketch As PlanarSketch = Nothing)
        '    ' oPl points are used to only form a plane and create a blank sketch on it
        '    Dim point1 As Point = oPl.PointAtIndex(1)
        '    Dim point2 As Point = oPl.PointAtIndex(2)
        '    Dim point3 As Point = oPl.PointAtIndex(3)
        '    Dim point4 As Point = oPl.PointAtIndex(4)
        '    Dim debugFlag As Boolean = True
        '    If debugFlag Then
        '        Debug.Print(point1.X & "," & point1.Y & "," & point1.Z)
        '        Debug.Print(point2.X & "," & point2.Y & "," & point2.Z)
        '        Debug.Print(point3.X & "," & point3.Y & "," & point3.Z)
        '        Debug.Print(point4.X & "," & point4.Y & "," & point4.Z)
        '    End If
        '    Dim oCompDef As ComponentDefinition = _invApp.ActiveDocument.ComponentDefinition
        '    If addToSketch Is Nothing Then
        '        If sourceSketch Is Nothing Then
        '            Dim v1 As Vector = _invApp.TransientGeometry.CreateVector(point2.X - point1.X, point2.Y - point1.Y, point2.Z - point1.Z)
        '            Dim uv1 As UnitVector = v1.AsUnitVector

        '            Dim v2 As Vector = _invApp.TransientGeometry.CreateVector(point4.X - point1.X, point4.Y - point1.Y, point4.Z - point1.Z)
        '            Dim uv2 As UnitVector = v2.AsUnitVector

        '            Dim pl As WorkPlane = oCompDef.WorkPlanes.AddFixed(point1, uv1, uv2, True)
        '            addToSketch = oCompDef.Sketches.Add(pl)
        '            pl.Visible = False
        '        Else
        '            Dim pl As WorkPlane = GetWorkPlane(sourceSketch.PlanarEntity) 'oCompDef.WorkPlanes.AddByPlaneAndOffset(sourceSketch.PlanarEntity, 0.0, True)
        '            addToSketch = oCompDef.Sketches.Add(pl)
        '            pl.Visible = False
        '            If Not sourceSketch.OriginPoint Is Nothing Then
        '                addToSketch.OriginPoint = sourceSketch.OriginPoint
        '            End If
        '        End If

        '    End If

        '    If sourceSketch Is Nothing Then
        '        Dim wpt1 As WorkPoint = oCompDef.WorkPoints.AddFixed(point1, True)
        '        Dim wpt3 As WorkPoint = oCompDef.WorkPoints.AddFixed(point3, True)

        '        Dim skpt1 As SketchPoint = addToSketch.AddByProjectingEntity(wpt1)
        '        Dim skpt2 As SketchPoint = addToSketch.AddByProjectingEntity(wpt3)
        '        Dim oRectangleLines As SketchEntitiesEnumerator
        '        oRectangleLines = addToSketch.SketchLines.AddAsTwoPointRectangle(skpt1, skpt2)

        '        wpt1.Visible = False
        '        wpt3.Visible = False
        '    Else
        '        sourceSketch.CopyContentsTo(addToSketch)
        '        If Not sourceSketch.OriginPoint Is Nothing Then
        '            addToSketch.OriginPoint = sourceSketch.OriginPoint
        '        End If
        '    End If


        '    addToSketch.Visible = False
        'End Sub
        'Private Function GetNormalOfPlanarEntity(p1 As Object) As UnitVector
        '    GetNormalOfPlanarEntity = Nothing
        '    If TypeOf p1 Is Inventor.Face Then
        '        Dim params(1) As Double
        '        params(0) = 0.5
        '        params(1) = 0.5
        '        Dim normals(2) As Double
        '        p1.Evaluator.GetNormal(params, normals)
        '        Dim normal As Inventor.Vector = _invApp.TransientGeometry.CreateVector(normals(0), normals(1), normals(2))
        '        GetNormalOfPlanarEntity = normal.AsUnitVector
        '    ElseIf TypeOf p1 Is WorkPlane Then
        '        GetNormalOfPlanarEntity = p1.Plane.Normal
        '    End If
        'End Function
        'Private Function ReverseDirectionIfNecessary(faceSketch As PlanarSketch, newSketch As PlanarSketch, extentdir As PartFeatureExtentDirectionEnum) As PartFeatureExtentDirectionEnum
        '    ReverseDirectionIfNecessary = extentdir

        '    Dim sourceNormal As UnitVector = GetNormalOfPlanarEntity(faceSketch.PlanarEntity)
        '    Dim destinationNormal As UnitVector = GetNormalOfPlanarEntity(newSketch.PlanarEntity)

        '    Dim angle As Double = sourceNormal.AngleTo(destinationNormal) ' make sure that original sketch and new sketch has plane normals same
        '    If Math.Abs(angle - Math.PI) <= 0.001 Then
        '        If extentdir = PartFeatureExtentDirectionEnum.kPositiveExtentDirection Then
        '            ReverseDirectionIfNecessary = PartFeatureExtentDirectionEnum.kNegativeExtentDirection
        '        Else
        '            ReverseDirectionIfNecessary = PartFeatureExtentDirectionEnum.kPositiveExtentDirection
        '        End If
        '    End If
        'End Function
        'Private Function CreateNewExtrude(ByVal oProfileOne As Inventor.Profile, ByVal length As Double, ByRef oper As PartFeatureOperationEnum, ByVal extentdir As PartFeatureExtentDirectionEnum) As ExtrudeFeature
        '    Dim oCompDef As ComponentDefinition = m_partDoc.ComponentDefinition
        '    Dim oExtrudeDef As ExtrudeDefinition
        '    oExtrudeDef = oCompDef.Features.ExtrudeFeatures.CreateExtrudeDefinition(oProfileOne, oper)
        '    oExtrudeDef.SetDistanceExtent(length, extentdir)

        '    Dim oExtrudeOne As ExtrudeFeature
        '    oExtrudeOne = oCompDef.Features.ExtrudeFeatures.Add(oExtrudeDef)
        '    Dim newbody As SurfaceBody = oExtrudeOne.SurfaceBodies.Item(1)
        '    CreateNewExtrude = oExtrudeOne

        'End Function

        Private Function ComputeNewToolBodyFeature(ByVal oFeature As PartFeature) As PartFeature

            ComputeNewToolBodyFeature = Nothing

            If TypeOf oFeature Is CutFeature Then
                Dim cut As CutFeature = oFeature
                Dim profile As Inventor.Profile = cut.Definition.Profile
                Dim extentdir As PartFeatureExtentDirectionEnum = PartFeatureExtentDirectionEnum.kSymmetricExtentDirection
                Dim distance As Double = 2 * m_thickness
                If cut.Definition.ExtentType = PartFeatureExtentEnum.kThroughAllExtent Then
                    Dim bx As Inventor.Box = cut.RangeBox
                    If Not bx Is Nothing Then
                        distance = bx.MinPoint.DistanceTo(bx.MaxPoint)
                        extentdir = PartFeatureExtentDirectionEnum.kNegativeExtentDirection
                    End If
                ElseIf cut.Definition.ExtentType = PartFeatureExtentEnum.kDistanceExtent Then
                    Dim distext As DistanceExtent = cut.Definition.Extent
                    distance = distext.Distance.Value
                    extentdir = distext.Direction
                End If

                Dim faceSketch As PlanarSketch = profile.Parent
                Dim newSketch As PlanarSketch = m_Utilities.CreateNewSketch(profile)
                extentdir = m_Utilities.ReverseDirectionIfNecessary(faceSketch, newSketch, extentdir)
                Dim profileNew As Profile = newSketch.Profiles.AddForSolid
                Dim newExtrude As ExtrudeFeature = m_Utilities.CreateNewExtrude(profileNew, distance, PartFeatureOperationEnum.kNewBodyOperation, extentdir) 'TWICE the thickness both sides symmetric
                'newExtrude.Appearance = m_partDoc.Assets.Item(m_partDoc.Assets.Count - 1)
                ComputeNewToolBodyFeature = newExtrude
                Exit Function
            ElseIf TypeOf oFeature Is HoleFeature Then
                Dim hole As HoleFeature = oFeature
                If TypeOf hole.PlacementDefinition Is LinearHolePlacementDefinition Then
                    Dim placement As LinearHolePlacementDefinition = hole.PlacementDefinition
                    Dim wp As WorkPlane = m_compDef.WorkPlanes.AddByPlaneAndOffset(placement.Plane, 0.0, True)
                    Dim skt As PlanarSketch = m_compDef.Sketches.Add(wp)
                    Dim center As Point = hole.HoleCenterPoints.Item(1)
                    Dim wpt As WorkPoint = m_compDef.WorkPoints.AddFixed(center, True)
                    Dim skpt As SketchPoint = skt.AddByProjectingEntity(wpt)
                    Dim sketchcircle As SketchCircle = skt.SketchCircles.AddByCenterRadius(skpt, 0.5 * hole.HoleDiameter.Value)
                    Dim profileNew As Profile = skt.Profiles.AddForSolid
                    Dim extentdir As PartFeatureExtentDirectionEnum = PartFeatureExtentDirectionEnum.kSymmetricExtentDirection

                    Dim distance As Double = 2 * m_thickness
                    If hole.ExtentType = PartFeatureExtentEnum.kThroughAllExtent Then
                        Dim bx As Inventor.Box = hole.RangeBox
                        If Not bx Is Nothing Then
                            distance = bx.MinPoint.DistanceTo(bx.MaxPoint)
                            extentdir = PartFeatureExtentDirectionEnum.kNegativeExtentDirection
                        End If
                    End If

                    Dim newExtrude As ExtrudeFeature = m_Utilities.CreateNewExtrude(profileNew, distance, PartFeatureOperationEnum.kNewBodyOperation, extentdir) 'TWICE the thickness both sides symmetric
                    'newExtrude.Appearance = m_partDoc.Assets.Item(m_partDoc.Assets.Count - 1)
                    ComputeNewToolBodyFeature = newExtrude
                End If


                'ElseIf TypeOf oFeature Is ExtrudeFeature Then
                '    If oFeature.Definition.Operation = PartFeatureOperationEnum.kCutOperation Then
                '    Else
                '        If oFeature.Definition.Profile.Count > 1 Then
                '            For Each profilepth As ProfilePath In oFeature.Definition.Profile
                '                If profilepth.AddsMaterial = False Then

                '                    Exit Function
                '                End If
                '            Next
                '        End If
                '    End If
            End If


        End Function

        Public Function CalculateThresholdPercentage() As Integer
            '''''''''''' TO BE IMPLEMENTED
            CalculateThresholdPercentage = 5
        End Function

        Private Function IsExtrudeNegativeOrHasHoles(ByVal oFeature As ExtrudeFeature) As Boolean
            IsExtrudeNegativeOrHasHoles = False
            If oFeature.Definition.Operation = PartFeatureOperationEnum.kCutOperation Then
                IsExtrudeNegativeOrHasHoles = True
            Else
                If oFeature.Definition.Profile.Count > 1 Then
                    For Each profilepth As ProfilePath In oFeature.Definition.Profile
                        If profilepth.AddsMaterial = False Then
                            IsExtrudeNegativeOrHasHoles = True
                            Exit Function
                        End If
                    Next
                End If
            End If
        End Function

    End Class

End Namespace

