
'##### CONFIDENTIAL - CONFIDENTIAL - CONFIDENTIAL ######
'		                    Parco RTLS™ System
'All information and source code contained herein is confidential and proprietary.
'Copying or modifying this source code is strictly prohibited unless under license of Parco Wireless.
'Copyright © 2001-2005 Parco Merged Media Inc. / Parco Wireless
'All rights reserved.
'##### CONFIDENTIAL - CONFIDENTIAL - CONFIDENTIAL ######
'Author:     Michael Farnsworth, Standard I-O Inc.
'Version:   1.0
'Date:       1/28/2005
'
'Modification/Author/Date:

Imports Parco
Imports System.Text

Public Class frmTrigger
	Inherits System.Windows.Forms.Form

#Region " Windows Form Designer generated code "

	Public Sub New()
		MyBase.New()

		'This call is required by the Windows Form Designer.
		InitializeComponent()

		'Add any initialization after the InitializeComponent() call

	End Sub

	'Form overrides dispose to clean up the component list.
	Protected Overloads Overrides Sub Dispose(ByVal disposing As Boolean)
		If disposing Then
			If Not (components Is Nothing) Then
				components.Dispose()
			End If
		End If
		MyBase.Dispose(disposing)
	End Sub

	'Required by the Windows Form Designer
	Private components As System.ComponentModel.IContainer

	'NOTE: The following procedure is required by the Windows Form Designer
	'It can be modified using the Windows Form Designer.  
	'Do not modify it using the code editor.
	Friend WithEvents Label3 As System.Windows.Forms.Label
	Friend WithEvents Label11 As System.Windows.Forms.Label
	Friend WithEvents cboTrigDir As System.Windows.Forms.ComboBox
	Friend WithEvents Label1 As System.Windows.Forms.Label
	Friend WithEvents txtXmin As System.Windows.Forms.TextBox
	Friend WithEvents Label2 As System.Windows.Forms.Label
	Friend WithEvents Label4 As System.Windows.Forms.Label
	Friend WithEvents Label5 As System.Windows.Forms.Label
	Friend WithEvents Label6 As System.Windows.Forms.Label
	Friend WithEvents Label7 As System.Windows.Forms.Label
	Friend WithEvents txtXMax As System.Windows.Forms.TextBox
	Friend WithEvents txtYmin As System.Windows.Forms.TextBox
	Friend WithEvents txtYMax As System.Windows.Forms.TextBox
	Friend WithEvents txtZBottom As System.Windows.Forms.TextBox
	Friend WithEvents txtZTop As System.Windows.Forms.TextBox
	Friend WithEvents btnOK As System.Windows.Forms.Button
	Friend WithEvents txtName As System.Windows.Forms.TextBox
	Friend WithEvents cboTrigColor As System.Windows.Forms.ComboBox
	Friend WithEvents Label16 As System.Windows.Forms.Label
	<System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
		Dim resources As System.Resources.ResourceManager = New System.Resources.ResourceManager(GetType(frmTrigger))
		Me.Label3 = New System.Windows.Forms.Label
		Me.Label11 = New System.Windows.Forms.Label
		Me.cboTrigDir = New System.Windows.Forms.ComboBox
		Me.Label1 = New System.Windows.Forms.Label
		Me.txtXmin = New System.Windows.Forms.TextBox
		Me.txtXMax = New System.Windows.Forms.TextBox
		Me.Label2 = New System.Windows.Forms.Label
		Me.txtYmin = New System.Windows.Forms.TextBox
		Me.Label4 = New System.Windows.Forms.Label
		Me.txtYMax = New System.Windows.Forms.TextBox
		Me.Label5 = New System.Windows.Forms.Label
		Me.txtZBottom = New System.Windows.Forms.TextBox
		Me.Label6 = New System.Windows.Forms.Label
		Me.txtZTop = New System.Windows.Forms.TextBox
		Me.Label7 = New System.Windows.Forms.Label
		Me.btnOK = New System.Windows.Forms.Button
		Me.txtName = New System.Windows.Forms.TextBox
		Me.cboTrigColor = New System.Windows.Forms.ComboBox
		Me.Label16 = New System.Windows.Forms.Label
		Me.SuspendLayout()
		'
		'Label3
		'
		Me.Label3.Location = New System.Drawing.Point(15, 16)
		Me.Label3.Name = "Label3"
		Me.Label3.Size = New System.Drawing.Size(56, 16)
		Me.Label3.TabIndex = 0
		Me.Label3.Text = "Name:"
		Me.Label3.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'Label11
		'
		Me.Label11.Location = New System.Drawing.Point(8, 69)
		Me.Label11.Name = "Label11"
		Me.Label11.Size = New System.Drawing.Size(64, 16)
		Me.Label11.TabIndex = 4
		Me.Label11.Text = "Direction:"
		Me.Label11.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'cboTrigDir
		'
		Me.cboTrigDir.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
		Me.cboTrigDir.Location = New System.Drawing.Point(80, 68)
		Me.cboTrigDir.Name = "cboTrigDir"
		Me.cboTrigDir.Size = New System.Drawing.Size(136, 21)
		Me.cboTrigDir.TabIndex = 5
		'
		'Label1
		'
		Me.Label1.Location = New System.Drawing.Point(8, 95)
		Me.Label1.Name = "Label1"
		Me.Label1.Size = New System.Drawing.Size(64, 16)
		Me.Label1.TabIndex = 6
		Me.Label1.Text = "X Min:"
		Me.Label1.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'txtXmin
		'
		Me.txtXmin.Location = New System.Drawing.Point(80, 94)
		Me.txtXmin.Name = "txtXmin"
		Me.txtXmin.Size = New System.Drawing.Size(72, 20)
		Me.txtXmin.TabIndex = 7
		Me.txtXmin.Text = ""
		'
		'txtXMax
		'
		Me.txtXMax.Location = New System.Drawing.Point(80, 119)
		Me.txtXMax.Name = "txtXMax"
		Me.txtXMax.Size = New System.Drawing.Size(72, 20)
		Me.txtXMax.TabIndex = 9
		Me.txtXMax.Text = ""
		'
		'Label2
		'
		Me.Label2.Location = New System.Drawing.Point(8, 119)
		Me.Label2.Name = "Label2"
		Me.Label2.Size = New System.Drawing.Size(64, 16)
		Me.Label2.TabIndex = 8
		Me.Label2.Text = "X Max:"
		Me.Label2.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'txtYmin
		'
		Me.txtYmin.Location = New System.Drawing.Point(80, 143)
		Me.txtYmin.Name = "txtYmin"
		Me.txtYmin.Size = New System.Drawing.Size(72, 20)
		Me.txtYmin.TabIndex = 11
		Me.txtYmin.Text = ""
		'
		'Label4
		'
		Me.Label4.Location = New System.Drawing.Point(8, 143)
		Me.Label4.Name = "Label4"
		Me.Label4.Size = New System.Drawing.Size(64, 16)
		Me.Label4.TabIndex = 10
		Me.Label4.Text = "Y Min:"
		Me.Label4.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'txtYMax
		'
		Me.txtYMax.Location = New System.Drawing.Point(80, 167)
		Me.txtYMax.Name = "txtYMax"
		Me.txtYMax.Size = New System.Drawing.Size(72, 20)
		Me.txtYMax.TabIndex = 13
		Me.txtYMax.Text = ""
		'
		'Label5
		'
		Me.Label5.Location = New System.Drawing.Point(8, 167)
		Me.Label5.Name = "Label5"
		Me.Label5.Size = New System.Drawing.Size(64, 16)
		Me.Label5.TabIndex = 12
		Me.Label5.Text = "Y Max:"
		Me.Label5.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'txtZBottom
		'
		Me.txtZBottom.Location = New System.Drawing.Point(80, 191)
		Me.txtZBottom.Name = "txtZBottom"
		Me.txtZBottom.Size = New System.Drawing.Size(72, 20)
		Me.txtZBottom.TabIndex = 15
		Me.txtZBottom.Text = ""
		'
		'Label6
		'
		Me.Label6.Location = New System.Drawing.Point(8, 191)
		Me.Label6.Name = "Label6"
		Me.Label6.Size = New System.Drawing.Size(64, 16)
		Me.Label6.TabIndex = 14
		Me.Label6.Text = "Z Bot:"
		Me.Label6.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'txtZTop
		'
		Me.txtZTop.Location = New System.Drawing.Point(80, 215)
		Me.txtZTop.Name = "txtZTop"
		Me.txtZTop.Size = New System.Drawing.Size(72, 20)
		Me.txtZTop.TabIndex = 17
		Me.txtZTop.Text = ""
		'
		'Label7
		'
		Me.Label7.Location = New System.Drawing.Point(8, 216)
		Me.Label7.Name = "Label7"
		Me.Label7.Size = New System.Drawing.Size(64, 16)
		Me.Label7.TabIndex = 16
		Me.Label7.Text = "Z Top:"
		Me.Label7.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'btnOK
		'
		Me.btnOK.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnOK.Location = New System.Drawing.Point(80, 244)
		Me.btnOK.Name = "btnOK"
		Me.btnOK.Size = New System.Drawing.Size(75, 24)
		Me.btnOK.TabIndex = 18
		Me.btnOK.Text = "OK"
		'
		'txtName
		'
		Me.txtName.Location = New System.Drawing.Point(80, 16)
		Me.txtName.Name = "txtName"
		Me.txtName.Size = New System.Drawing.Size(136, 20)
		Me.txtName.TabIndex = 1
		Me.txtName.Text = ""
		'
		'cboTrigColor
		'
		Me.cboTrigColor.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
		Me.cboTrigColor.Location = New System.Drawing.Point(80, 41)
		Me.cboTrigColor.Name = "cboTrigColor"
		Me.cboTrigColor.Size = New System.Drawing.Size(136, 21)
		Me.cboTrigColor.TabIndex = 3
		'
		'Label16
		'
		Me.Label16.Location = New System.Drawing.Point(13, 43)
		Me.Label16.Name = "Label16"
		Me.Label16.Size = New System.Drawing.Size(59, 16)
		Me.Label16.TabIndex = 2
		Me.Label16.Text = "Trig Color:"
		Me.Label16.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'frmTrigger
		'
		Me.AutoScaleBaseSize = New System.Drawing.Size(5, 13)
		Me.ClientSize = New System.Drawing.Size(232, 278)
		Me.Controls.Add(Me.cboTrigColor)
		Me.Controls.Add(Me.Label16)
		Me.Controls.Add(Me.txtName)
		Me.Controls.Add(Me.btnOK)
		Me.Controls.Add(Me.txtZTop)
		Me.Controls.Add(Me.Label7)
		Me.Controls.Add(Me.txtZBottom)
		Me.Controls.Add(Me.Label6)
		Me.Controls.Add(Me.txtYMax)
		Me.Controls.Add(Me.Label5)
		Me.Controls.Add(Me.txtYmin)
		Me.Controls.Add(Me.Label4)
		Me.Controls.Add(Me.txtXMax)
		Me.Controls.Add(Me.Label2)
		Me.Controls.Add(Me.txtXmin)
		Me.Controls.Add(Me.Label1)
		Me.Controls.Add(Me.Label3)
		Me.Controls.Add(Me.Label11)
		Me.Controls.Add(Me.cboTrigDir)
		Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
		Me.MaximizeBox = False
		Me.MinimizeBox = False
		Me.Name = "frmTrigger"
		Me.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent
		Me.Text = "Trigger Area"
		Me.ResumeLayout(False)

	End Sub

#End Region

	Private mTrig As Trigger
	Private mValid As Boolean = False

	Dim zTop As Single = 0
	Dim zBot As Single = 0
	Dim xMax As Single = 0
	Dim xMin As Single = 0
	Dim yMax As Single = 0
    Dim yMin As Single = 0
    Private clr As System.Drawing.Color

    Public Property TrigColor() As System.Drawing.Color
        Get
            Return clr
        End Get
        Set(ByVal Value As System.Drawing.Color)
            clr = Value
        End Set
    End Property
    Friend Property Trig() As Trigger
        Get
            Return mTrig
        End Get
        Set(ByVal Value As Trigger)
            mTrig = Value
        End Set
    End Property
    Public ReadOnly Property IsValid() As Boolean
        Get
            Return mValid
        End Get
    End Property

    Private Sub frmTrigger_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load

        Try
            cboTrigDir.DataSource = System.Enum.GetValues(GetType(Parco.Trigger.Directions))
            cboTrigDir.SelectedIndex = 0

            LoadColors()

            If cboTrigColor.Items.Contains(clr.ToKnownColor.ToString) Then
                cboTrigColor.SelectedItem = clr.ToKnownColor.ToString
            End If

            If mTrig Is Nothing Then
                Me.Text &= " -New"
            Else
                Me.Text &= " -Edit"
                PopFromTrig()
            End If

        Catch ex As Exception
            MessageBox.Show(ex.Message, "Trigger Form Load Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
        End Try
    End Sub

    Private Sub PopFromTrig()
        If Not mTrig Is Nothing Then
            'our regions collection is 1 based, the trig name is used as the key and ID= -1 in this demo....
            '(The ID is used as the Auto number key in the RTLS database if we were saving/retrieving the trigger from there.
            txtName.Text = mTrig.Name
            cboTrigDir.SelectedItem = mTrig.Direction
            With mTrig.Regions.Item(1)
                txtZBottom.Text = .ZBottom.ToString
                txtZTop.Text = .ZTop.ToString
                txtXMax.Text = .XMax.ToString
                txtXmin.Text = .Xmin.ToString
                txtYMax.Text = .YMax.ToString
                txtYmin.Text = .Ymin.ToString
            End With
        End If
    End Sub

    Private Sub LoadColors()
        Dim en As System.Enum = New KnownColor
        Dim aColorName As String    'set a flag for when the system colors end.
        Dim blnStart As Boolean = False
        For Each aColorName In en.GetNames(en.GetType)
            If blnStart Then
                cboTrigColor.Items.Add(aColorName)
            End If
            If aColorName = "Transparent" Then
                blnStart = True
            End If
        Next
        cboTrigColor.SelectedItem = "Red"

    End Sub
    Private Function Valid(ByRef sMsg As String) As Boolean
        'test for broken rules

        Dim sb As New StringBuilder

        If IsNumeric(txtZBottom.Text) Then
            zBot = CType(txtZBottom.Text, Single)
        End If
        If IsNumeric(txtZTop.Text) Then
            zTop = CType(txtZTop.Text, Single)
        End If

        If IsNumeric(txtXmin.Text) Then
            xMin = CType(txtXmin.Text, Single)
        End If
        If IsNumeric(txtXMax.Text) Then
            xMax = CType(txtXMax.Text, Single)
        End If
        If IsNumeric(txtYmin.Text) Then
            yMin = CType(txtYmin.Text, Single)
        End If
        If IsNumeric(txtYMax.Text) Then
            yMax = CType(txtYMax.Text, Single)
        End If
        If IsNumeric(txtZBottom.Text) = False Then
            sb.Append("Trigger bottom Value is not numeric.")
            sb.Append(ControlChars.CrLf)
        End If
        If IsNumeric(txtZTop.Text) = False Then
            sb.Append("Trigger top Value is not numeric.")
            sb.Append(ControlChars.CrLf)
        End If
        If zTop <= zBot Then
            sb.Append("Trigger top must be greater than the trigger bottom.")
            sb.Append(ControlChars.CrLf)
        End If
        If cboTrigDir.SelectedIndex = 0 Then
            sb.Append("Trigger direction must be specified.")
            sb.Append(ControlChars.CrLf)
        End If
        If xMax <= xMin Then
            sb.Append("Trigger XMax must be > XMin.")
            sb.Append(ControlChars.CrLf)
        End If
        If yMax <= yMin Then
            sb.Append("Trigger YMax must be > YMin.")
            sb.Append(ControlChars.CrLf)
        End If
        If txtName.Text = String.Empty Then
            sb.Append("Trigger Name not specified.")
            sb.Append(ControlChars.CrLf)
        End If

        sMsg = sb.ToString
        If sMsg = String.Empty Then
            Return True
        Else
            Return False
        End If
    End Function

    Private Sub txtZBottom_KeyPress(ByVal sender As Object, ByVal e As System.Windows.Forms.KeyPressEventArgs) Handles txtZBottom.KeyPress, txtXMax.KeyPress, txtXmin.KeyPress, txtYMax.KeyPress, txtYmin.KeyPress, txtZTop.KeyPress
        NumberOrControl(e)
    End Sub

    Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
        Dim sMsg As String
        If Valid(sMsg) Then
            mTrig = TriggerCreate(xMin, yMin, xMax, yMax, zBot, zTop, CType(cboTrigDir.SelectedItem, Trigger.Directions), txtName.Text)
            If mTrig.IsValid Then
                mValid = True
                Me.Close()
            Else
                'we should not get here, but just in case
                MessageBox.Show("Sorry, the specified parameters do not create a valid trigger.", "Invalid Trigger Shape", MessageBoxButtons.OK, MessageBoxIcon.Information)
            End If

            mValid = True
            Me.Close()

        Else
            MessageBox.Show(sMsg, "Invalid Parameters", MessageBoxButtons.OK, MessageBoxIcon.Information)
        End If
    End Sub
End Class
