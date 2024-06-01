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
        Me.ThresholdValue.Size = New System.Drawing.Size(31, 20)
        Me.ThresholdValue.TabIndex = 2
        Me.ThresholdValue.Text = "5"
        Me.ThresholdValue.TextAlign = System.Windows.Forms.HorizontalAlignment.Right
        '
        'SuppressRButton
        '
        Me.SuppressRButton.Enabled = False
        Me.SuppressRButton.Location = New System.Drawing.Point(15, 239)
        Me.SuppressRButton.Name = "SuppressRButton"
        Me.SuppressRButton.Size = New System.Drawing.Size(75, 23)
        Me.SuppressRButton.TabIndex = 3
        Me.SuppressRButton.Text = "Suppress R"
        Me.SuppressRButton.UseVisualStyleBackColor = True
        '
        'PreviewRButton
        '
        Me.PreviewRButton.Enabled = False
        Me.PreviewRButton.Location = New System.Drawing.Point(15, 210)
        Me.PreviewRButton.Name = "PreviewRButton"
        Me.PreviewRButton.Size = New System.Drawing.Size(75, 23)
        Me.PreviewRButton.TabIndex = 5
        Me.PreviewRButton.Text = "Preview R"
        Me.PreviewRButton.UseVisualStyleBackColor = True
        '
        'WrapOption
        '
        Me.WrapOption.AutoSize = True
        Me.WrapOption.Checked = True
        Me.WrapOption.CheckState = System.Windows.Forms.CheckState.Checked
        Me.WrapOption.Location = New System.Drawing.Point(15, 77)
        Me.WrapOption.Name = "WrapOption"
        Me.WrapOption.Size = New System.Drawing.Size(66, 17)
        Me.WrapOption.TabIndex = 6
        Me.WrapOption.Text = "Dormant"
        Me.WrapOption.UseVisualStyleBackColor = True
        '
        'InitUnfold
        '
        Me.InitUnfold.ForeColor = System.Drawing.Color.Black
        Me.InitUnfold.Location = New System.Drawing.Point(15, 101)
        Me.InitUnfold.Name = "InitUnfold"
        Me.InitUnfold.Size = New System.Drawing.Size(75, 23)
        Me.InitUnfold.TabIndex = 7
        Me.InitUnfold.Text = "Init-Unfold"
        Me.InitUnfold.UseVisualStyleBackColor = True
        '
        'PreviewSButton
        '
        Me.PreviewSButton.Enabled = False
        Me.PreviewSButton.Location = New System.Drawing.Point(15, 141)
        Me.PreviewSButton.Name = "PreviewSButton"
        Me.PreviewSButton.Size = New System.Drawing.Size(75, 23)
        Me.PreviewSButton.TabIndex = 8
        Me.PreviewSButton.Text = "Preview S"
        Me.PreviewSButton.UseVisualStyleBackColor = True
        '
        'SuppressSButton
        '
        Me.SuppressSButton.Enabled = False
        Me.SuppressSButton.Location = New System.Drawing.Point(15, 171)
        Me.SuppressSButton.Name = "SuppressSButton"
        Me.SuppressSButton.Size = New System.Drawing.Size(75, 23)
        Me.SuppressSButton.TabIndex = 9
        Me.SuppressSButton.Text = "Suppress S"
        Me.SuppressSButton.UseVisualStyleBackColor = True
        '
        'SizeLabel
        '
        Me.SizeLabel.AutoSize = True
        Me.SizeLabel.Location = New System.Drawing.Point(13, 34)
        Me.SizeLabel.Margin = New System.Windows.Forms.Padding(3, 3, 3, 3)
        Me.SizeLabel.Name = "SizeLabel"
        Me.SizeLabel.Size = New System.Drawing.Size(75, 13)
        Me.SizeLabel.TabIndex = 10
        Me.SizeLabel.Text = "of <unknown>"
        '
        'Form1
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.BackColor = System.Drawing.Color.FromArgb(CType(CType(255, Byte), Integer), CType(CType(192, Byte), Integer), CType(CType(192, Byte), Integer))
        Me.ClientSize = New System.Drawing.Size(116, 273)
        Me.Controls.Add(Me.SizeLabel)
        Me.Controls.Add(Me.SuppressSButton)
        Me.Controls.Add(Me.PreviewSButton)
        Me.Controls.Add(Me.InitUnfold)
        Me.Controls.Add(Me.WrapOption)
        Me.Controls.Add(Me.PreviewRButton)
        Me.Controls.Add(Me.SuppressRButton)
        Me.Controls.Add(Me.ThresholdValue)
        Me.Controls.Add(Me.ThresholdLabel)
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
