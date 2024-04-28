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
        Me.Label1 = New System.Windows.Forms.Label()
        Me.Label2 = New System.Windows.Forms.Label()
        Me.startBtn = New System.Windows.Forms.Button()
        Me.backBtn = New System.Windows.Forms.Button()
        Me.nextBtn = New System.Windows.Forms.Button()
        Me.endBtn = New System.Windows.Forms.Button()
        Me.OpenInit = New System.Windows.Forms.Button()
        Me.SuspendLayout()
        '
        'Label1
        '
        Me.Label1.AutoSize = True
        Me.Label1.Location = New System.Drawing.Point(141, 94)
        Me.Label1.Name = "Label1"
        Me.Label1.Size = New System.Drawing.Size(98, 13)
        Me.Label1.TabIndex = 0
        Me.Label1.Text = "by Yogesh Kulkarni"
        '
        'Label2
        '
        Me.Label2.AutoSize = True
        Me.Label2.Font = New System.Drawing.Font("Microsoft Sans Serif", 9.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label2.Location = New System.Drawing.Point(26, 9)
        Me.Label2.Name = "Label2"
        Me.Label2.Size = New System.Drawing.Size(192, 16)
        Me.Label2.TabIndex = 0
        Me.Label2.Text = "Inventor Feature Traverser"
        '
        'startBtn
        '
        Me.startBtn.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.startBtn.Location = New System.Drawing.Point(61, 38)
        Me.startBtn.Name = "startBtn"
        Me.startBtn.Size = New System.Drawing.Size(40, 40)
        Me.startBtn.TabIndex = 1
        Me.startBtn.Text = "<<"
        Me.startBtn.UseVisualStyleBackColor = True
        '
        'backBtn
        '
        Me.backBtn.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.backBtn.Location = New System.Drawing.Point(107, 38)
        Me.backBtn.Name = "backBtn"
        Me.backBtn.Size = New System.Drawing.Size(40, 40)
        Me.backBtn.TabIndex = 1
        Me.backBtn.Text = "<"
        Me.backBtn.UseVisualStyleBackColor = True
        '
        'nextBtn
        '
        Me.nextBtn.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.nextBtn.Location = New System.Drawing.Point(153, 38)
        Me.nextBtn.Name = "nextBtn"
        Me.nextBtn.Size = New System.Drawing.Size(40, 40)
        Me.nextBtn.TabIndex = 1
        Me.nextBtn.Text = ">"
        Me.nextBtn.UseVisualStyleBackColor = True
        '
        'endBtn
        '
        Me.endBtn.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.endBtn.Location = New System.Drawing.Point(199, 38)
        Me.endBtn.Name = "endBtn"
        Me.endBtn.Size = New System.Drawing.Size(40, 40)
        Me.endBtn.TabIndex = 1
        Me.endBtn.Text = ">>"
        Me.endBtn.UseVisualStyleBackColor = True
        '
        'OpenInit
        '
        Me.OpenInit.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.OpenInit.Location = New System.Drawing.Point(15, 38)
        Me.OpenInit.Name = "OpenInit"
        Me.OpenInit.Size = New System.Drawing.Size(40, 40)
        Me.OpenInit.TabIndex = 1
        Me.OpenInit.Text = "O"
        Me.OpenInit.UseVisualStyleBackColor = True
        '
        'Form1
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.BackColor = System.Drawing.SystemColors.ActiveCaption
        Me.ClientSize = New System.Drawing.Size(254, 116)
        Me.Controls.Add(Me.endBtn)
        Me.Controls.Add(Me.nextBtn)
        Me.Controls.Add(Me.backBtn)
        Me.Controls.Add(Me.OpenInit)
        Me.Controls.Add(Me.startBtn)
        Me.Controls.Add(Me.Label2)
        Me.Controls.Add(Me.Label1)
        Me.Name = "Form1"
        Me.Text = "Form1"
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub
    Friend WithEvents Label1 As System.Windows.Forms.Label
    Friend WithEvents Label2 As System.Windows.Forms.Label
    Friend WithEvents startBtn As System.Windows.Forms.Button
    Friend WithEvents backBtn As System.Windows.Forms.Button
    Friend WithEvents nextBtn As System.Windows.Forms.Button
    Friend WithEvents endBtn As System.Windows.Forms.Button
    Friend WithEvents OpenInit As System.Windows.Forms.Button

End Class
