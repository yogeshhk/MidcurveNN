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
        Me.SuppressRButton = New System.Windows.Forms.Button()
        Me.PreviewRButton = New System.Windows.Forms.Button()
        Me.WrapOption = New System.Windows.Forms.CheckBox()
        Me.InitUnfold = New System.Windows.Forms.Button()
        Me.PreviewSButton = New System.Windows.Forms.Button()
        Me.SuppressSButton = New System.Windows.Forms.Button()
        Me.SizeLabel = New System.Windows.Forms.Label()
        Me.SuspendLayout()
        '
        'ThresholdLabel
        '
        Me.ThresholdLabel.AutoSize = True
        Me.ThresholdLabel.Location = New System.Drawing.Point(17, 16)
        Me.ThresholdLabel.Margin = New System.Windows.Forms.Padding(4, 0, 4, 0)
        Me.ThresholdLabel.Name = "ThresholdLabel"
        Me.ThresholdLabel.Size = New System.Drawing.Size(51, 17)
        Me.ThresholdLabel.TabIndex = 0
        Me.ThresholdLabel.Text = "Size %"
        '
        'ThresholdValue
        '
        Me.ThresholdValue.Location = New System.Drawing.Point(76, 12)
        Me.ThresholdValue.Margin = New System.Windows.Forms.Padding(4)
        Me.ThresholdValue.Name = "ThresholdValue"
        Me.ThresholdValue.Size = New System.Drawing.Size(40, 22)
        Me.ThresholdValue.TabIndex = 2
        Me.ThresholdValue.Text = "5"
        Me.ThresholdValue.TextAlign = System.Windows.Forms.HorizontalAlignment.Right
        '
        'SuppressRButton
        '
        Me.SuppressRButton.Enabled = False
        Me.SuppressRButton.Location = New System.Drawing.Point(20, 294)
        Me.SuppressRButton.Margin = New System.Windows.Forms.Padding(4)
        Me.SuppressRButton.Name = "SuppressRButton"
        Me.SuppressRButton.Size = New System.Drawing.Size(100, 28)
        Me.SuppressRButton.TabIndex = 3
        Me.SuppressRButton.Text = "Suppress R"
        Me.SuppressRButton.UseVisualStyleBackColor = True
        '
        'PreviewRButton
        '
        Me.PreviewRButton.Enabled = False
        Me.PreviewRButton.Location = New System.Drawing.Point(20, 258)
        Me.PreviewRButton.Margin = New System.Windows.Forms.Padding(4)
        Me.PreviewRButton.Name = "PreviewRButton"
        Me.PreviewRButton.Size = New System.Drawing.Size(100, 28)
        Me.PreviewRButton.TabIndex = 5
        Me.PreviewRButton.Text = "Preview R"
        Me.PreviewRButton.UseVisualStyleBackColor = True
        '
        'WrapOption
        '
        Me.WrapOption.AutoSize = True
        Me.WrapOption.Location = New System.Drawing.Point(20, 95)
        Me.WrapOption.Margin = New System.Windows.Forms.Padding(4)
        Me.WrapOption.Name = "WrapOption"
        Me.WrapOption.Size = New System.Drawing.Size(91, 21)
        Me.WrapOption.TabIndex = 6
        Me.WrapOption.Text = "Wrapping"
        Me.WrapOption.UseVisualStyleBackColor = True
        '
        'InitUnfold
        '
        Me.InitUnfold.ForeColor = System.Drawing.Color.Black
        Me.InitUnfold.Location = New System.Drawing.Point(20, 124)
        Me.InitUnfold.Margin = New System.Windows.Forms.Padding(4)
        Me.InitUnfold.Name = "InitUnfold"
        Me.InitUnfold.Size = New System.Drawing.Size(100, 28)
        Me.InitUnfold.TabIndex = 7
        Me.InitUnfold.Text = "Init-Unfold"
        Me.InitUnfold.UseVisualStyleBackColor = True
        '
        'PreviewSButton
        '
        Me.PreviewSButton.Enabled = False
        Me.PreviewSButton.Location = New System.Drawing.Point(20, 174)
        Me.PreviewSButton.Margin = New System.Windows.Forms.Padding(4)
        Me.PreviewSButton.Name = "PreviewSButton"
        Me.PreviewSButton.Size = New System.Drawing.Size(100, 28)
        Me.PreviewSButton.TabIndex = 8
        Me.PreviewSButton.Text = "Preview S"
        Me.PreviewSButton.UseVisualStyleBackColor = True
        '
        'SuppressSButton
        '
        Me.SuppressSButton.Enabled = False
        Me.SuppressSButton.Location = New System.Drawing.Point(20, 210)
        Me.SuppressSButton.Margin = New System.Windows.Forms.Padding(4)
        Me.SuppressSButton.Name = "SuppressSButton"
        Me.SuppressSButton.Size = New System.Drawing.Size(100, 28)
        Me.SuppressSButton.TabIndex = 9
        Me.SuppressSButton.Text = "Suppress S"
        Me.SuppressSButton.UseVisualStyleBackColor = True
        '
        'SizeLabel
        '
        Me.SizeLabel.AutoSize = True
        Me.SizeLabel.Location = New System.Drawing.Point(17, 42)
        Me.SizeLabel.Margin = New System.Windows.Forms.Padding(4)
        Me.SizeLabel.Name = "SizeLabel"
        Me.SizeLabel.Size = New System.Drawing.Size(96, 17)
        Me.SizeLabel.TabIndex = 10
        Me.SizeLabel.Text = "of <unknown>"
        '
        'Form1
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(8.0!, 16.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.BackColor = System.Drawing.Color.FromArgb(CType(CType(255, Byte), Integer), CType(CType(192, Byte), Integer), CType(CType(192, Byte), Integer))
        Me.ClientSize = New System.Drawing.Size(142, 336)
        Me.Controls.Add(Me.SizeLabel)
        Me.Controls.Add(Me.SuppressSButton)
        Me.Controls.Add(Me.PreviewSButton)
        Me.Controls.Add(Me.InitUnfold)
        Me.Controls.Add(Me.WrapOption)
        Me.Controls.Add(Me.PreviewRButton)
        Me.Controls.Add(Me.SuppressRButton)
        Me.Controls.Add(Me.ThresholdValue)
        Me.Controls.Add(Me.ThresholdLabel)
        Me.Margin = New System.Windows.Forms.Padding(4)
        Me.MaximizeBox = False
        Me.MinimizeBox = False
        Me.Name = "Form1"
        Me.Opacity = 0.9R
        Me.Text = "YhK Simplify"
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub
    Friend WithEvents ThresholdLabel As System.Windows.Forms.Label
    Friend WithEvents ThresholdValue As System.Windows.Forms.TextBox
    Friend WithEvents SuppressRButton As System.Windows.Forms.Button
    Friend WithEvents PreviewRButton As System.Windows.Forms.Button
    Friend WithEvents WrapOption As System.Windows.Forms.CheckBox
    Friend WithEvents InitUnfold As System.Windows.Forms.Button
    Friend WithEvents PreviewSButton As System.Windows.Forms.Button
    Friend WithEvents SuppressSButton As System.Windows.Forms.Button
    Friend WithEvents SizeLabel As System.Windows.Forms.Label

End Class
