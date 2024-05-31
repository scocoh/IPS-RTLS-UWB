
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
Public Class frmTagTrigger
	Inherits System.Windows.Forms.Form


	Private mTrig As Parco.Trigger
	Private mTag As TagPlus
	Private mValid As Boolean

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
	Friend WithEvents Label1 As System.Windows.Forms.Label
	Friend WithEvents Label14 As System.Windows.Forms.Label
	Friend WithEvents txtTagBottom As System.Windows.Forms.TextBox
	Friend WithEvents Label15 As System.Windows.Forms.Label
	Friend WithEvents txtTagTop As System.Windows.Forms.TextBox
	Friend WithEvents Label11 As System.Windows.Forms.Label
	Friend WithEvents Label9 As System.Windows.Forms.Label
	Friend WithEvents cboRadius As System.Windows.Forms.ComboBox
	Friend WithEvents lblTagID As System.Windows.Forms.Label
	Friend WithEvents cboTrigDir As System.Windows.Forms.ComboBox
	Friend WithEvents btnOK As System.Windows.Forms.Button
	Friend WithEvents lblName As System.Windows.Forms.Label
	Friend WithEvents Label3 As System.Windows.Forms.Label
	Friend WithEvents lblLoc As System.Windows.Forms.Label
	Friend WithEvents Label4 As System.Windows.Forms.Label
	<System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
		Dim resources As System.Resources.ResourceManager = New System.Resources.ResourceManager(GetType(frmTagTrigger))
		Me.Label1 = New System.Windows.Forms.Label
		Me.Label14 = New System.Windows.Forms.Label
		Me.txtTagBottom = New System.Windows.Forms.TextBox
		Me.Label15 = New System.Windows.Forms.Label
		Me.txtTagTop = New System.Windows.Forms.TextBox
		Me.Label11 = New System.Windows.Forms.Label
		Me.cboTrigDir = New System.Windows.Forms.ComboBox
		Me.Label9 = New System.Windows.Forms.Label
		Me.cboRadius = New System.Windows.Forms.ComboBox
		Me.lblTagID = New System.Windows.Forms.Label
		Me.btnOK = New System.Windows.Forms.Button
		Me.lblName = New System.Windows.Forms.Label
		Me.Label3 = New System.Windows.Forms.Label
		Me.lblLoc = New System.Windows.Forms.Label
		Me.Label4 = New System.Windows.Forms.Label
		Me.SuspendLayout()
		'
		'Label1
		'
		Me.Label1.Location = New System.Drawing.Point(16, 12)
		Me.Label1.Name = "Label1"
		Me.Label1.Size = New System.Drawing.Size(56, 16)
		Me.Label1.TabIndex = 0
		Me.Label1.Text = "Tag ID:"
		Me.Label1.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'Label14
		'
		Me.Label14.Location = New System.Drawing.Point(8, 160)
		Me.Label14.Name = "Label14"
		Me.Label14.Size = New System.Drawing.Size(72, 16)
		Me.Label14.TabIndex = 10
		Me.Label14.Text = "Bottom Elev:"
		Me.Label14.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'txtTagBottom
		'
		Me.txtTagBottom.Location = New System.Drawing.Point(83, 157)
		Me.txtTagBottom.Name = "txtTagBottom"
		Me.txtTagBottom.Size = New System.Drawing.Size(106, 20)
		Me.txtTagBottom.TabIndex = 11
		Me.txtTagBottom.Text = "-1"
		'
		'Label15
		'
		Me.Label15.Location = New System.Drawing.Point(16, 132)
		Me.Label15.Name = "Label15"
		Me.Label15.Size = New System.Drawing.Size(56, 16)
		Me.Label15.TabIndex = 8
		Me.Label15.Text = "Top Elev:"
		Me.Label15.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'txtTagTop
		'
		Me.txtTagTop.Location = New System.Drawing.Point(83, 131)
		Me.txtTagTop.Name = "txtTagTop"
		Me.txtTagTop.Size = New System.Drawing.Size(106, 20)
		Me.txtTagTop.TabIndex = 9
		Me.txtTagTop.Text = "8"
		'
		'Label11
		'
		Me.Label11.Location = New System.Drawing.Point(17, 107)
		Me.Label11.Name = "Label11"
		Me.Label11.Size = New System.Drawing.Size(64, 16)
		Me.Label11.TabIndex = 6
		Me.Label11.Text = "Direction:"
		Me.Label11.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'cboTrigDir
		'
		Me.cboTrigDir.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
		Me.cboTrigDir.Location = New System.Drawing.Point(83, 104)
		Me.cboTrigDir.Name = "cboTrigDir"
		Me.cboTrigDir.Size = New System.Drawing.Size(107, 21)
		Me.cboTrigDir.TabIndex = 7
		'
		'Label9
		'
		Me.Label9.Location = New System.Drawing.Point(15, 81)
		Me.Label9.Name = "Label9"
		Me.Label9.Size = New System.Drawing.Size(104, 16)
		Me.Label9.TabIndex = 4
		Me.Label9.Text = "Octogon Radius:"
		Me.Label9.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'cboRadius
		'
		Me.cboRadius.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
		Me.cboRadius.Items.AddRange(New Object() {"1.0", "1.5", "2.0", "2.5", "3.0", "3.5", "4.0", "4.5", "5.0", "5.5", "6.0"})
		Me.cboRadius.Location = New System.Drawing.Point(134, 77)
		Me.cboRadius.Name = "cboRadius"
		Me.cboRadius.Size = New System.Drawing.Size(56, 21)
		Me.cboRadius.TabIndex = 5
		'
		'lblTagID
		'
		Me.lblTagID.ForeColor = System.Drawing.Color.Navy
		Me.lblTagID.Location = New System.Drawing.Point(80, 12)
		Me.lblTagID.Name = "lblTagID"
		Me.lblTagID.Size = New System.Drawing.Size(114, 16)
		Me.lblTagID.TabIndex = 1
		Me.lblTagID.Text = "lblTagID"
		Me.lblTagID.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'btnOK
		'
		Me.btnOK.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnOK.Location = New System.Drawing.Point(113, 190)
		Me.btnOK.Name = "btnOK"
		Me.btnOK.Size = New System.Drawing.Size(75, 24)
		Me.btnOK.TabIndex = 12
		Me.btnOK.Text = "OK"
		'
		'lblName
		'
		Me.lblName.ForeColor = System.Drawing.Color.Navy
		Me.lblName.Location = New System.Drawing.Point(80, 30)
		Me.lblName.Name = "lblName"
		Me.lblName.Size = New System.Drawing.Size(114, 16)
		Me.lblName.TabIndex = 3
		Me.lblName.Text = "lblName"
		Me.lblName.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'Label3
		'
		Me.Label3.Location = New System.Drawing.Point(16, 30)
		Me.Label3.Name = "Label3"
		Me.Label3.Size = New System.Drawing.Size(56, 16)
		Me.Label3.TabIndex = 2
		Me.Label3.Text = "Name:"
		Me.Label3.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'lblLoc
		'
		Me.lblLoc.ForeColor = System.Drawing.Color.Navy
		Me.lblLoc.Location = New System.Drawing.Point(80, 48)
		Me.lblLoc.Name = "lblLoc"
		Me.lblLoc.Size = New System.Drawing.Size(114, 16)
		Me.lblLoc.TabIndex = 14
		Me.lblLoc.Text = "lblLoc"
		Me.lblLoc.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'Label4
		'
		Me.Label4.Location = New System.Drawing.Point(16, 48)
		Me.Label4.Name = "Label4"
		Me.Label4.Size = New System.Drawing.Size(56, 16)
		Me.Label4.TabIndex = 13
		Me.Label4.Text = "Location:"
		Me.Label4.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'frmTagTrigger
		'
		Me.AutoScaleBaseSize = New System.Drawing.Size(5, 13)
		Me.ClientSize = New System.Drawing.Size(200, 222)
		Me.Controls.Add(Me.lblLoc)
		Me.Controls.Add(Me.Label4)
		Me.Controls.Add(Me.lblName)
		Me.Controls.Add(Me.Label3)
		Me.Controls.Add(Me.btnOK)
		Me.Controls.Add(Me.lblTagID)
		Me.Controls.Add(Me.Label14)
		Me.Controls.Add(Me.txtTagBottom)
		Me.Controls.Add(Me.txtTagTop)
		Me.Controls.Add(Me.Label15)
		Me.Controls.Add(Me.Label11)
		Me.Controls.Add(Me.cboTrigDir)
		Me.Controls.Add(Me.Label9)
		Me.Controls.Add(Me.cboRadius)
		Me.Controls.Add(Me.Label1)
		Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
		Me.MaximizeBox = False
		Me.MinimizeBox = False
		Me.Name = "frmTagTrigger"
		Me.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen
		Me.Text = "Tag Trigger"
		Me.ResumeLayout(False)

	End Sub

#End Region

	Public Property Trigger() As Parco.Trigger
		Get
			Return mTrig
		End Get
		Set(ByVal Value As Parco.Trigger)
			mTrig = Value
		End Set
	End Property
	Friend Property TagPlus() As TagPlus
		Get
			Return mTag
		End Get
		Set(ByVal Value As TagPlus)
			mTag = Value
		End Set
	End Property

	Public ReadOnly Property IsValid() As Boolean
		Get
			Return mValid
		End Get
	End Property

	Private Sub frmTagTrigger_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles MyBase.Load
		Try
			cboTrigDir.DataSource = System.Enum.GetValues(GetType(Parco.Trigger.Directions))
			cboTrigDir.SelectedIndex = 0

			cboRadius.SelectedIndex = 0
			If mTag Is Nothing Then
				lblTagID.Text = "Error! - no tag specified."
				lblName.Text = String.Empty
				btnOK.Enabled = False
			Else
				lblTagID.Text = mTag.ID
				lblName.Text = mTag.Name
				If Not mTrig Is Nothing Then
					PopFromTrig()
					Me.Text &= " -Edit"
				Else
					Me.Text &= " -New"
					lblLoc.Text = ToRealCoord(mTag.X, mTag.Y, mTag.Z).ToString
				End If
			End If

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Tag Trigger Form Load Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub

	Private Sub PopFromTrig()
		If Not mTrig Is Nothing Then
			'our regions collection is 1 based
			txtTagBottom.Text = mTrig.Regions.Item(1).ZBottom.ToString
			txtTagTop.Text = mTrig.Regions.Item(1).ZTop.ToString
			cboTrigDir.SelectedItem = mTrig.Direction
			Dim r As Single
			'calulate our radius from the triggers bounding box
			r = (mTrig.Regions.Item(1).XMax - mTrig.Regions.Item(1).Xmin) / 2
			cboRadius.SelectedItem = Format(r, "#0.0")
			'calculate the centroid of the trigger in X and Y, and use zbottom
			lblLoc.Text = New Point3D((mTrig.Regions.Item(1).XMax + mTrig.Regions.Item(1).Xmin) / 2, (mTrig.Regions.Item(1).YMax + mTrig.Regions.Item(1).Ymin) / 2, mTrig.Regions.Item(1).ZBottom).ToString

		End If
	End Sub

	Private Function Valid(ByRef sMsg As String) As Boolean
		'test for broken rules
		Dim zTop As Single = 0
		Dim zBot As Single = 0
		Dim sb As New StringBuilder

		If IsNumeric(txtTagBottom.Text) Then
			zBot = CType(txtTagBottom.Text, Single)
		End If
		If IsNumeric(txtTagTop.Text) Then
			zTop = CType(txtTagTop.Text, Single)
		End If

		If IsNumeric(txtTagBottom.Text) = False Then
			sb.Append("Trigger bottom Value is not numeric.")
			sb.Append(ControlChars.CrLf)
		End If
		If IsNumeric(txtTagTop.Text) = False Then
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
		sMsg = sb.ToString
		If sMsg = String.Empty Then
			Return True
		Else
			Return False
		End If
	End Function

	Private Sub txtTagBottom_KeyPress(ByVal sender As Object, ByVal e As System.Windows.Forms.KeyPressEventArgs) Handles txtTagBottom.KeyPress
		NumberOrControl(e)
	End Sub

	Private Sub txtTagTop_KeyPress(ByVal sender As Object, ByVal e As System.Windows.Forms.KeyPressEventArgs) Handles txtTagTop.KeyPress
		NumberOrControl(e)
	End Sub

	Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
		Try
			Dim sMsg As String
			If Valid(sMsg) Then
				'HACK: see if out tag has a numeric id, only allow tag triggers for numeric ids. - The Trigger class needs to have a key property of type object added.
				'This is only being done to keep from having to create a hash look up.
				If Not IsNumeric(mTag.ID) Then
					MessageBox.Show("Sorry, tag triggers may only be created for numeric tags for this demo.", "Numeric Tags Only", MessageBoxButtons.OK, MessageBoxIcon.Information)
					Return
				End If

				'get a RTLS coordinate from out viewer coordinate
				Dim p As Point3D = ToRealCoord(mTag.X, mTag.Y, mTag.Z)
				mTrig = TagTriggerCreate(p, CType(cboRadius.SelectedItem, Single), CType(txtTagBottom.Text, Single), _
				   CType(txtTagTop.Text, Single), CType(cboTrigDir.SelectedItem, Trigger.Directions), mTag.Name & "'s trigger", CType(mTag.ID, Integer))
				mValid = True
				Me.Close()

			Else
				MessageBox.Show(sMsg, "Invalid Parameters", MessageBoxButtons.OK, MessageBoxIcon.Information)
			End If

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Tag Create Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)

		End Try
	End Sub
End Class
