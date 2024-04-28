Imports System
Imports System.Type
Imports System.Activator
Imports System.Runtime.InteropServices
Imports Inventor

Public Class Form1

    ' App variables.
    Dim _invApp As Inventor.Application
    Dim _started As Boolean = False
    Dim _initialized As Boolean = False

    'Feature lists
    Private m_suppressableSFeatures As ObjectCollection ' Suppressable Sheet Metal features
    Private m_suppressableRFeatures As ObjectCollection ' Suppressable Remnant features

    Private m_highlightedFeatures As HighlightSet ' just for user feedback, TODO: user can override, and then this is sent for suppression
    Private m_clusters As List(Of Cluster) = New List(Of Cluster) ' List of Groups, each goes for suppression together

    'Size parameters
    Private m_partSize As Double ' either the diagonal of the BB or sqrt of sum-of-face-areas
    Dim m_userSizePercentage As Integer ' users input
    Private m_sizeD As Double = 0.05 ' default value, will get calculated by above two

    ' Wrapping: No Negative volumes are kept'
    Private m_Wrapping As Boolean = False

    'Validation Statistics
    Dim m_numFacesBefore As Integer
    Dim m_numFacesAfter As Integer
    Dim m_numFeaturesBefore As Integer
    Dim m_numFeaturesAfter As Integer

    'Group of Faces and their owner features.
    ' Nested class as info is not required outside
    Public Class Cluster
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
        Sub WriteToFile(sw As IO.StreamWriter)
            sw.Write(m_clusterSize.ToString("#.##") & ": [")
            For Each oFeature In m_clusterFeatures
                sw.Write(oFeature.Name & ", ")
            Next
            sw.Write("]")
        End Sub

    End Class

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

        ClearFeatureListsAndClusters()

        If _started Then
            _invApp.Quit()
        End If

        _invApp = Nothing
    End Sub

    Private Sub ClearFeatureListsAndClusters()
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

        If Not m_highlightedFeatures Is Nothing Then
            If m_highlightedFeatures.Count > 0 Then
                m_highlightedFeatures.Clear()
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

    Private Function IsConstituentOfPattern(child As PartFeature, parent As PartFeature) As Boolean

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

    Private Sub CreateImage(FileName As String)

        ' Create a new camera. 
        Dim cam As Inventor.Camera
        cam = _invApp.TransientObjects.CreateCamera()

        Dim oCompDef As Inventor.ComponentDefinition
        oCompDef = _invApp.ActiveDocument.ComponentDefinition


        ' Associate the document with the camera. 
        cam.SceneObject = oCompDef

        ' Define the camera and apply the changes. 
        cam.ViewOrientationType = _
             Inventor.ViewOrientationTypeEnum.kIsoTopRightViewOrientation
        cam.Fit()
        cam.ApplyWithoutTransition()

        'cam.SaveAsBitmap(FileName + ".png", 800, 600) '1126, 533

        cam.SaveAsBitmap(FileName + ".png", 800, 600, _
                _invApp.TransientObjects.CreateColor(255, 255, 255), _
               _invApp.TransientObjects.CreateColor(255, 255, 255))

        'Save the result, defining the background color of the image. BLUE GRADIENT
        'cam.SaveAsBitmap(FileName + ".png", 800, 600, _
        '        _invApp.TransientObjects.CreateColor(255, 255, 255), _
        '        _invApp.TransientObjects.CreateColor(15, 15, 215))

        ' Save the result, defining the background color of the image. 
        'cam.SaveAsBitmap(FileName + ".bmp", 800, 600, _
        '        _invApp.TransientObjects.CreateColor(255, 255, 0), _
        '        _invApp.TransientObjects.CreateColor(15, 15, 15))
    End Sub

    ' Suppressibility Assessment ----------------------------------------------------------------------

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
                If m_Wrapping = True Then
                    IsSheetMetalFeatureSupressible = True ' in case of Wrapping suppress holes irrespective of size
                Else
                    Dim diameter As Double = 2 * m_sizeD ' some initialization with high value
                    If Not oFeature.HoleDiameter Is Nothing Then
                        diameter = oFeature.HoleDiameter.Value
                    Else
                        diameter = oFeature.Parameters(1).Value
                    End If
                    If diameter < m_sizeD Then
                        IsSheetMetalFeatureSupressible = True
                    End If
                End If

            ElseIf TypeOf oFeature Is FoldFeature Then
                Dim length As Double
                length = oFeature.Parameters(1).Value
                If length < m_sizeD Then
                    IsSheetMetalFeatureSupressible = True
                End If


            ElseIf TypeOf oFeature Is CutFeature Then
                If m_Wrapping = True Then
                    IsSheetMetalFeatureSupressible = True ' in case of Wrapping suppress holes irrespective of size
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

    ' If parent-child (only for patterns), MERGE
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

        If _initialized = False Then
            Exit Sub
        End If

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


        ' Calculate Cluster Size, which is the Unioned BB of the remnant faces, there are two other methods:
        '   - Just summation of remnant face areas (crude, but quick method)
        '   - Actual volume by suppressing and unsupressing the feature and taking volume difference
        Dim sw As New IO.StreamWriter("DebugDumpFile.txt")

        sw.WriteLine("Global Size = " & m_sizeD.ToString("#.##"))

        For Each pCluster In m_clusters
            If Not pCluster.m_MarkForDelete = True Then
                Dim size As Double = pCluster.GetSize()
                pCluster.WriteToFile(sw)
                If size < m_sizeD Then
                    ' Add all the features in the cluster
                    For Each oFeature In pCluster.m_clusterFeatures
                        m_suppressableRFeatures.Add(oFeature)
                    Next
                    sw.WriteLine(" => Suppressed ")
                Else
                    sw.WriteLine(" => Not Suppressed ")
                End If
            End If
        Next
        sw.Close()

    End Sub

    Private Sub CollectSheetMetalSuppressibleFeatures()

        If _initialized = False Then
            Exit Sub
        End If

        Dim sFeatures As Inventor.PartFeatures
        sFeatures = _invApp.ActiveDocument.ComponentDefinition.Features

        Dim oFeature As PartFeature
        For Each oFeature In sFeatures
            'Debug.Print(oFeature.Name)
            If IsSheetMetalFeatureSupressible(oFeature) = True Then
                m_suppressableSFeatures.Add(oFeature)
            End If
        Next
    End Sub

    Private Sub SuppressFeatures(features As ObjectCollection)

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
                    oFeature.Suppressed = True
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
            MsgBox("Additional suppresssions were " & newSuppressed)
        End If
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

        ' If Preview button is clicked after changing %age value, while part remaining the samee
        ClearFeatureListsAndClusters()
    End Sub

    Private Sub InitUnfold_Click(sender As System.Object, e As System.EventArgs) Handles InitUnfold.Click

        ' set active part
        If _initialized = False Then
            _initialized = Init()
        End If

        '--------------------------------------------------------------------------------------------------

        ' Suppress ALL Unfold features so that part comes in natural shape
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

        '--------------------------------------------------------------------------------------------------


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
        m_sizeD = (m_userSizePercentage / 100.0) * m_partSize

        SizeLabel.Text = "of " + brepArea.ToString("#.##") + " = " + m_sizeD.ToString("#.##") ' or bbDiagonal.ToString("#.##")

        '--------------------------------------------------------------------------------------------------

        If m_partSize > 0 Then
            PreviewSButton.Enabled = True
            PreviewRButton.Enabled = True
        End If
    End Sub

    Private Sub PreviewSButton_Click(sender As System.Object, e As System.EventArgs) Handles PreviewSButton.Click
        If _initialized = False Then
            Exit Sub
        End If

        ' If Preview button is clicked after changing %age value, while part remaining the same
        ' ClearFeatureListsAndClusters()

        m_suppressableSFeatures = _invApp.TransientObjects.CreateObjectCollection

        'Create a variable for start time:
        Dim TimerStart As DateTime
        TimerStart = Now

        ' First Pass : Type based selection
        CollectSheetMetalSuppressibleFeatures()

        Dim TimeSpent As System.TimeSpan
        TimeSpent = Now.Subtract(TimerStart)

        MsgBox("Suppressed " & m_suppressableSFeatures.Count & " Sheet Metal Features in " & TimeSpent.TotalSeconds & " seconds")

        If m_highlightedFeatures Is Nothing Then
            m_highlightedFeatures = _invApp.ActiveDocument.HighlightSets.Add
        End If


        ' Highlight the features.
        Dim oFeature As PartFeature
        For Each oFeature In m_suppressableSFeatures
            If Not oFeature Is Nothing Then
                Debug.Print(oFeature.Name)
                m_highlightedFeatures.AddItem(oFeature)
            End If
        Next

        If m_highlightedFeatures.Count > 0 Then
            SuppressSButton.Enabled = True
        End If
        'MsgBox("Number of features in suppress list are " & m_suppressableFeatures.Count)

    End Sub

    Private Sub SuppressSButton_Click(sender As System.Object, e As System.EventArgs) Handles SuppressSButton.Click
        If _initialized = False Then
            Exit Sub
        End If

        If Not m_highlightedFeatures Is Nothing Then
            m_highlightedFeatures.Clear()
        End If

        If _invApp.ActiveDocument.ComponentDefinition Is Nothing Then
            Exit Sub
        End If

        Dim iptFileName As String = _invApp.ActiveDocument.DisplayName
        CreateImage(iptFileName + "_OriginalPart")

        SuppressFeatures(m_suppressableSFeatures)

        CreateImage(iptFileName + "_SMSpecific_After")

        MsgBox("Num Faces before were " & m_numFacesBefore & " and now Num Faces are " & m_numFacesAfter)

        ' NOW WORK is over, lets clean the lists
        ClearFeatureListsAndClusters()
    End Sub

    Private Sub PreviewRButton_Click(sender As System.Object, e As System.EventArgs) Handles PreviewRButton.Click

        If _initialized = False Then
            Exit Sub
        End If

        ' If Preview button is clicked after changing %age value, while part remaining the same
        ClearFeatureListsAndClusters()

        m_suppressableRFeatures = _invApp.TransientObjects.CreateObjectCollection


        'Create a variable for start time:
        Dim TimerStart As DateTime
        TimerStart = Now


        ' Second Pass : Remnant size based selection
        CollectRemnantSuppressableFeatures()


        Dim TimeSpent As System.TimeSpan
        TimeSpent = Now.Subtract(TimerStart)

        MsgBox("Suppressed " & m_suppressableRFeatures.Count & " Features by Remnant Method in " & TimeSpent.TotalSeconds & " seconds")

        If m_highlightedFeatures Is Nothing Then
            m_highlightedFeatures = _invApp.ActiveDocument.HighlightSets.Add
        End If


        ' Highlight the features.
        Dim oFeature As PartFeature
        For Each oFeature In m_suppressableRFeatures
            If Not oFeature Is Nothing Then
                Debug.Print(oFeature.Name)
                m_highlightedFeatures.AddItem(oFeature)
            End If
        Next

        If m_highlightedFeatures.Count > 0 Then
            SuppressRButton.Enabled = True
        End If
        'MsgBox("Number of features in suppress list are " & m_suppressableFeatures.Count)

    End Sub

    Private Sub SuppressRButton_Click(sender As System.Object, e As System.EventArgs) Handles SuppressRButton.Click

        If _initialized = False Then
            Exit Sub
        End If

        If Not m_highlightedFeatures Is Nothing Then
            m_highlightedFeatures.Clear()
        End If

        If _invApp.ActiveDocument.ComponentDefinition Is Nothing Then
            Exit Sub
        End If

        Dim iptFileName As String = _invApp.ActiveDocument.DisplayName
        'CreateImage(iptFileName + "_SMSpecific_After")

        SuppressFeatures(m_suppressableRFeatures)

        CreateImage(iptFileName + "_FinalPart")

        MsgBox("Num Faces before were " & m_numFacesBefore & " and now Num Faces are " & m_numFacesAfter)

        ' NOW WORK is over, lets clean the lists
        ClearFeatureListsAndClusters()

    End Sub

End Class
