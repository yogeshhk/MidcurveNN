<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class Form1
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Me.ExtractSketchBtn = New System.Windows.Forms.Button()
        Me.MidcurvesBtn = New System.Windows.Forms.Button()
        Me.SuspendLayout()
        '
        'ExtractSketchBtn
        '
        Me.ExtractSketchBtn.Location = New System.Drawing.Point(12, 427)
        Me.ExtractSketchBtn.Name = "ExtractSketchBtn"
        Me.ExtractSketchBtn.Size = New System.Drawing.Size(122, 23)
        Me.ExtractSketchBtn.TabIndex = 1
        Me.ExtractSketchBtn.Text = "Extract Sketch"
        Me.ExtractSketchBtn.UseVisualStyleBackColor = True
        '
        'MidcurvesBtn
        '
        Me.MidcurvesBtn.Location = New System.Drawing.Point(149, 427)
        Me.MidcurvesBtn.Name = "MidcurvesBtn"
        Me.MidcurvesBtn.Size = New System.Drawing.Size(124, 23)
        Me.MidcurvesBtn.TabIndex = 2
        Me.MidcurvesBtn.Text = "Calculate Midcurves"
        Me.MidcurvesBtn.UseVisualStyleBackColor = True
        '
        'Form1
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(384, 462)
        Me.Controls.Add(Me.MidcurvesBtn)
        Me.Controls.Add(Me.ExtractSketchBtn)
        Me.Name = "Form1"
        Me.Text = "Form1"
        Me.ResumeLayout(False)

    End Sub
    Friend WithEvents ExtractSketchBtn As System.Windows.Forms.Button
    Friend WithEvents MidcurvesBtn As System.Windows.Forms.Button

End Class
