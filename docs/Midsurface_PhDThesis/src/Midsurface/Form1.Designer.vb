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
        Me.GenMidsurf = New System.Windows.Forms.Button()
        Me.SuspendLayout()
        '
        'GenMidsurf
        '
        Me.GenMidsurf.Location = New System.Drawing.Point(13, 7)
        Me.GenMidsurf.Name = "GenMidsurf"
        Me.GenMidsurf.Size = New System.Drawing.Size(115, 30)
        Me.GenMidsurf.TabIndex = 0
        Me.GenMidsurf.Text = "Gen Midsurf"
        Me.GenMidsurf.UseVisualStyleBackColor = True
        '
        'Form1
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(8.0!, 16.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.BackColor = System.Drawing.SystemColors.GradientActiveCaption
        Me.ClientSize = New System.Drawing.Size(140, 42)
        Me.Controls.Add(Me.GenMidsurf)
        Me.MaximizeBox = False
        Me.MinimizeBox = False
        Me.Name = "Form1"
        Me.Opacity = 0.9R
        Me.Text = "YhK MidsGen"
        Me.ResumeLayout(False)

    End Sub
    Friend WithEvents GenMidsurf As System.Windows.Forms.Button

End Class
