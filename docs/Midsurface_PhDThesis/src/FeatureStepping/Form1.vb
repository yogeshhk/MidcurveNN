Imports System
Imports System.Type
Imports System.Activator
Imports System.Runtime.InteropServices
Imports Inventor


Public Class Form1
    ' Member variables.

    Dim _invApp As Inventor.Application
    Private m_partDoc As Document
    Private m_browserList() As Object
    Private m_currentPosition As Integer
    Dim _started As Boolean = False

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

        ' Build up a list of the items in the browser.
        Dim treePane As BrowserPane
        treePane = m_partDoc.BrowserPanes.ActivePane

        ' Get the top node, which should represent a PartComponentDefinition.
        Dim topNode As BrowserNode
        topNode = treePane.topNode
        If Not TypeOf topNode.nativeObject Is PartComponentDefinition Then
            MsgBox("The ""Model"" pane must be active in the browser.")
            Init = False
            Exit Function
        End If

        ' Special case for sheet metal parts because there's an
        ' extra folder for the folded features and the flat pattern.
        If m_partDoc.SubType = "{9C464203-9BAE-11D3-8BAD-0060B0CE6BB4}" Then
            topNode = topNode.BrowserNodes.Item(1)
        End If

        ' Load an array with the features and sketches from the browser.
        Dim actualCount As Integer
        actualCount = 0
        ReDim m_browserList(topNode.BrowserNodes.count - 1)
        Dim i As Integer
        For i = 1 To topNode.BrowserNodes.count
            If topNode.BrowserNodes.Item(i).Visible Then
                Dim nativeObject As Object
                nativeObject = topNode.BrowserNodes.Item(i).nativeObject
                If Not nativeObject Is Nothing Then
                    If TypeOf nativeObject Is PartFeature Or _
                       TypeOf nativeObject Is sketch Or _
                       TypeOf nativeObject Is Sketch3D Then
                        m_browserList(actualCount) = nativeObject
                        actualCount = actualCount + 1
                    End If
                End If
            End If
        Next

        ReDim Preserve m_browserList(actualCount - 1)

        ' Determine the currence position of the stop node within the browser.
        Dim beforeObj As Object
        Dim afterObj As Object

        beforeObj = Nothing
        afterObj = Nothing

        Dim oCompDef As PartComponentDefinition
        oCompDef = _invApp.ActiveDocument.ComponentDefinition()
        oCompDef.GetEndOfPartPosition(afterObj, beforeObj)

        'Call m_partDoc.ComponentDefinition.GetEndOfPartPosition(beforeObj, afterObj)

        If Not beforeObj Is Nothing Then
            For i = 0 To actualCount - 1
                If beforeObj Is m_browserList(i) Then
                    m_currentPosition = i + 1
                End If
            Next
        ElseIf Not afterObj Is Nothing Then
            For i = 0 To actualCount - 1
                If afterObj Is m_browserList(i) Then
                    m_currentPosition = i
                End If
            Next
        End If

        Init = True
    End Function

    Private Sub openInitBtn_Click(sender As System.Object, e As System.EventArgs) Handles OpenInit.Click
        ' generate tree.
        Init()
    End Sub

    Private Sub startBtn_Click(sender As System.Object, e As System.EventArgs) Handles startBtn.Click
        ' Set the stop node to the top.
        Call m_partDoc.ComponentDefinition.SetEndOfPartToTopOrBottom(True)
        m_currentPosition = 0
    End Sub

    Private Sub backBtn_Click(sender As System.Object, e As System.EventArgs) Handles backBtn.Click
        ' Move the stop node up by one.
        If m_currentPosition > 0 Then
            m_currentPosition = m_currentPosition - 1
            Call m_browserList(m_currentPosition).SetEndOfPart(True)
        End If
    End Sub

    Private Sub nextBtn_Click(sender As System.Object, e As System.EventArgs) Handles nextBtn.Click
        ' Move the stop node down by one.
        If m_currentPosition <= UBound(m_browserList) Then
            m_currentPosition = m_currentPosition + 1
            Call m_browserList(m_currentPosition - 1).SetEndOfPart(False)
        End If
    End Sub

    Private Sub endBtn_Click(sender As System.Object, e As System.EventArgs) Handles endBtn.Click
        ' Set the stop node to the bottom.
        Call m_partDoc.ComponentDefinition.SetEndOfPartToTopOrBottom(False)
        m_currentPosition = UBound(m_browserList) + 1
    End Sub

    Private Sub Form1_FormClosed(sender As Object, e As System.Windows.Forms.FormClosedEventArgs) Handles Me.FormClosed
        If _started Then
            _invApp.Quit()
        End If

        _invApp = Nothing
    End Sub
End Class

