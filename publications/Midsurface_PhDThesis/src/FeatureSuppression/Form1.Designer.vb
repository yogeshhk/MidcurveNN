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
        Me.ThresholdLabel = New System.Windows.Forms.Label()
        Me.ThresholdValue = New System.Windows.Forms.TextBox()
        Me.SuppressButton = New System.Windows.Forms.Button()
        Me.CancelButton = New System.Windows.Forms.Button()
        Me.PreviewButton = New System.Windows.Forms.Button()
        Me.SuspendLayout()
        '
        'ThresholdLabel
        '
        Me.ThresholdLabel.AutoSize = True
        Me.ThresholdLabel.Location = New System.Drawing.Point(13, 13)
        Me.ThresholdLabel.Name = "ThresholdLabel"
        Me.ThresholdLabel.Size = New System.Drawing.Size(38, 13)
        Me.ThresholdLabel.TabIndex = 0
        Me.ThresholdLabel.Text = "Size %"
        '
        'ThresholdValue
        '
        Me.ThresholdValue.Location = New System.Drawing.Point(57, 10)
        Me.ThresholdValue.Name = "ThresholdValue"
        Me.ThresholdValue.Size = New System.Drawing.Size(34, 20)
        Me.ThresholdValue.TabIndex = 2
        Me.ThresholdValue.Text = "5"
        Me.ThresholdValue.TextAlign = System.Windows.Forms.HorizontalAlignment.Right
        '
        'SuppressButton
        '
        Me.SuppressButton.Location = New System.Drawing.Point(16, 57)
        Me.SuppressButton.Name = "SuppressButton"
        Me.SuppressButton.Size = New System.Drawing.Size(75, 23)
        Me.SuppressButton.TabIndex = 3
        Me.SuppressButton.Text = "Suppress"
        Me.SuppressButton.UseVisualStyleBackColor = True
        '
        'CancelButton
        '
        Me.CancelButton.Location = New System.Drawing.Point(97, 57)
        Me.CancelButton.Name = "CancelButton"
        Me.CancelButton.Size = New System.Drawing.Size(65, 23)
        Me.CancelButton.TabIndex = 4
        Me.CancelButton.Text = "Cancel"
        Me.CancelButton.UseVisualStyleBackColor = True
        '
        'PreviewButton
        '
        Me.PreviewButton.Location = New System.Drawing.Point(97, 8)
        Me.PreviewButton.Name = "PreviewButton"
        Me.PreviewButton.Size = New System.Drawing.Size(65, 23)
        Me.PreviewButton.TabIndex = 5
        Me.PreviewButton.Text = "Preview"
        Me.PreviewButton.UseVisualStyleBackColor = True
        '
        'Form1
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(173, 92)
        Me.Controls.Add(Me.PreviewButton)
        Me.Controls.Add(Me.CancelButton)
        Me.Controls.Add(Me.SuppressButton)
        Me.Controls.Add(Me.ThresholdValue)
        Me.Controls.Add(Me.ThresholdLabel)
        Me.Name = "Form1"
        Me.Text = "Simplify"
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub
    Friend WithEvents ThresholdLabel As System.Windows.Forms.Label
    Friend WithEvents ThresholdValue As System.Windows.Forms.TextBox
    Friend WithEvents SuppressButton As System.Windows.Forms.Button
    Friend WithEvents CancelButton As System.Windows.Forms.Button
    Friend WithEvents PreviewButton As System.Windows.Forms.Button

End Class
