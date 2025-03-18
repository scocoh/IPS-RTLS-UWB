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

Public Class frmTag
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
	Friend WithEvents Label1 As System.Windows.Forms.Label
	Friend WithEvents txtTagID As System.Windows.Forms.TextBox
	Friend WithEvents txtTagName As System.Windows.Forms.TextBox
	Friend WithEvents Label2 As System.Windows.Forms.Label
	Friend WithEvents btnSave As System.Windows.Forms.Button
	Friend WithEvents Label3 As System.Windows.Forms.Label
	Friend WithEvents cboImages As System.Windows.Forms.ComboBox
	Friend WithEvents cboSizeH As System.Windows.Forms.ComboBox
	Friend WithEvents Label4 As System.Windows.Forms.Label
	Friend WithEvents Label5 As System.Windows.Forms.Label
	Friend WithEvents cboSizeW As System.Windows.Forms.ComboBox
	Friend WithEvents GroupBox1 As System.Windows.Forms.GroupBox
	Friend WithEvents chkThermometer As System.Windows.Forms.CheckBox
	Friend WithEvents txtTherm As System.Windows.Forms.TextBox
	Friend WithEvents Label6 As System.Windows.Forms.Label
	Friend WithEvents Label7 As System.Windows.Forms.Label
	Friend WithEvents chkEKG As System.Windows.Forms.CheckBox
	Friend WithEvents chkXray As System.Windows.Forms.CheckBox
	Friend WithEvents Label8 As System.Windows.Forms.Label
	Friend WithEvents cboSizeChild As System.Windows.Forms.ComboBox
	Friend WithEvents txtEKG As System.Windows.Forms.TextBox
	Friend WithEvents txtXray As System.Windows.Forms.TextBox
	Friend WithEvents chkProcess As System.Windows.Forms.CheckBox
	Friend WithEvents Label9 As System.Windows.Forms.Label
	Friend WithEvents txtProcess As System.Windows.Forms.TextBox
	<System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
		Dim resources As System.Resources.ResourceManager = New System.Resources.ResourceManager(GetType(frmTag))
		Me.Label1 = New System.Windows.Forms.Label
		Me.txtTagID = New System.Windows.Forms.TextBox
		Me.txtTagName = New System.Windows.Forms.TextBox
		Me.Label2 = New System.Windows.Forms.Label
		Me.btnSave = New System.Windows.Forms.Button
		Me.cboImages = New System.Windows.Forms.ComboBox
		Me.Label3 = New System.Windows.Forms.Label
		Me.cboSizeH = New System.Windows.Forms.ComboBox
		Me.Label4 = New System.Windows.Forms.Label
		Me.Label5 = New System.Windows.Forms.Label
		Me.cboSizeW = New System.Windows.Forms.ComboBox
		Me.GroupBox1 = New System.Windows.Forms.GroupBox
		Me.txtXray = New System.Windows.Forms.TextBox
		Me.txtEKG = New System.Windows.Forms.TextBox
		Me.chkXray = New System.Windows.Forms.CheckBox
		Me.chkEKG = New System.Windows.Forms.CheckBox
		Me.Label7 = New System.Windows.Forms.Label
		Me.Label6 = New System.Windows.Forms.Label
		Me.txtTherm = New System.Windows.Forms.TextBox
		Me.chkThermometer = New System.Windows.Forms.CheckBox
		Me.Label8 = New System.Windows.Forms.Label
		Me.cboSizeChild = New System.Windows.Forms.ComboBox
		Me.txtProcess = New System.Windows.Forms.TextBox
		Me.chkProcess = New System.Windows.Forms.CheckBox
		Me.Label9 = New System.Windows.Forms.Label
		Me.GroupBox1.SuspendLayout()
		Me.SuspendLayout()
		'
		'Label1
		'
		Me.Label1.Location = New System.Drawing.Point(37, 25)
		Me.Label1.Name = "Label1"
		Me.Label1.Size = New System.Drawing.Size(56, 16)
		Me.Label1.TabIndex = 0
		Me.Label1.Text = "Tag ID:"
		Me.Label1.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'txtTagID
		'
		Me.txtTagID.Location = New System.Drawing.Point(97, 22)
		Me.txtTagID.Name = "txtTagID"
		Me.txtTagID.Size = New System.Drawing.Size(170, 20)
		Me.txtTagID.TabIndex = 1
		Me.txtTagID.Text = ""
		'
		'txtTagName
		'
		Me.txtTagName.Location = New System.Drawing.Point(97, 48)
		Me.txtTagName.Name = "txtTagName"
		Me.txtTagName.Size = New System.Drawing.Size(168, 20)
		Me.txtTagName.TabIndex = 3
		Me.txtTagName.Text = ""
		'
		'Label2
		'
		Me.Label2.Location = New System.Drawing.Point(12, 50)
		Me.Label2.Name = "Label2"
		Me.Label2.Size = New System.Drawing.Size(80, 16)
		Me.Label2.TabIndex = 2
		Me.Label2.Text = "Display Name:"
		Me.Label2.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'btnSave
		'
		Me.btnSave.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnSave.Location = New System.Drawing.Point(230, 384)
		Me.btnSave.Name = "btnSave"
		Me.btnSave.TabIndex = 11
		Me.btnSave.Text = "OK"
		'
		'cboImages
		'
		Me.cboImages.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
		Me.cboImages.Location = New System.Drawing.Point(97, 74)
		Me.cboImages.Name = "cboImages"
		Me.cboImages.Size = New System.Drawing.Size(168, 21)
		Me.cboImages.TabIndex = 5
		'
		'Label3
		'
		Me.Label3.Location = New System.Drawing.Point(11, 76)
		Me.Label3.Name = "Label3"
		Me.Label3.Size = New System.Drawing.Size(80, 16)
		Me.Label3.TabIndex = 4
		Me.Label3.Text = "Tag Image:"
		Me.Label3.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'cboSizeH
		'
		Me.cboSizeH.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
		Me.cboSizeH.Items.AddRange(New Object() {"0.5", "1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0", "8.0", "9.0", "10.0"})
		Me.cboSizeH.Location = New System.Drawing.Point(97, 101)
		Me.cboSizeH.Name = "cboSizeH"
		Me.cboSizeH.Size = New System.Drawing.Size(88, 21)
		Me.cboSizeH.TabIndex = 7
		'
		'Label4
		'
		Me.Label4.Location = New System.Drawing.Point(11, 104)
		Me.Label4.Name = "Label4"
		Me.Label4.Size = New System.Drawing.Size(80, 16)
		Me.Label4.TabIndex = 6
		Me.Label4.Text = "Tag Height:"
		Me.Label4.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'Label5
		'
		Me.Label5.Location = New System.Drawing.Point(10, 130)
		Me.Label5.Name = "Label5"
		Me.Label5.Size = New System.Drawing.Size(80, 16)
		Me.Label5.TabIndex = 8
		Me.Label5.Text = "Tag Width:"
		Me.Label5.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'cboSizeW
		'
		Me.cboSizeW.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
		Me.cboSizeW.Items.AddRange(New Object() {"0.5", "1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0", "8.0", "9.0", "10.0"})
		Me.cboSizeW.Location = New System.Drawing.Point(96, 128)
		Me.cboSizeW.Name = "cboSizeW"
		Me.cboSizeW.Size = New System.Drawing.Size(89, 21)
		Me.cboSizeW.TabIndex = 9
		'
		'GroupBox1
		'
		Me.GroupBox1.Controls.Add(Me.Label9)
		Me.GroupBox1.Controls.Add(Me.txtProcess)
		Me.GroupBox1.Controls.Add(Me.chkProcess)
		Me.GroupBox1.Controls.Add(Me.txtXray)
		Me.GroupBox1.Controls.Add(Me.txtEKG)
		Me.GroupBox1.Controls.Add(Me.chkXray)
		Me.GroupBox1.Controls.Add(Me.chkEKG)
		Me.GroupBox1.Controls.Add(Me.Label7)
		Me.GroupBox1.Controls.Add(Me.Label6)
		Me.GroupBox1.Controls.Add(Me.txtTherm)
		Me.GroupBox1.Controls.Add(Me.chkThermometer)
		Me.GroupBox1.Controls.Add(Me.Label8)
		Me.GroupBox1.Controls.Add(Me.cboSizeChild)
		Me.GroupBox1.Location = New System.Drawing.Point(25, 152)
		Me.GroupBox1.Name = "GroupBox1"
		Me.GroupBox1.Size = New System.Drawing.Size(280, 224)
		Me.GroupBox1.TabIndex = 10
		Me.GroupBox1.TabStop = False
		Me.GroupBox1.Text = "Tag Children"
		'
		'txtXray
		'
		Me.txtXray.Location = New System.Drawing.Point(103, 117)
		Me.txtXray.Name = "txtXray"
		Me.txtXray.Size = New System.Drawing.Size(169, 20)
		Me.txtXray.TabIndex = 9
		Me.txtXray.Text = ""
		'
		'txtEKG
		'
		Me.txtEKG.Location = New System.Drawing.Point(104, 91)
		Me.txtEKG.Name = "txtEKG"
		Me.txtEKG.Size = New System.Drawing.Size(168, 20)
		Me.txtEKG.TabIndex = 7
		Me.txtEKG.Text = ""
		'
		'chkXray
		'
		Me.chkXray.Location = New System.Drawing.Point(11, 113)
		Me.chkXray.Name = "chkXray"
		Me.chkXray.Size = New System.Drawing.Size(64, 24)
		Me.chkXray.TabIndex = 8
		Me.chkXray.Text = "X-Ray"
		'
		'chkEKG
		'
		Me.chkEKG.Location = New System.Drawing.Point(11, 89)
		Me.chkEKG.Name = "chkEKG"
		Me.chkEKG.Size = New System.Drawing.Size(56, 24)
		Me.chkEKG.TabIndex = 6
		Me.chkEKG.Text = "EKG"
		'
		'Label7
		'
		Me.Label7.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Underline, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label7.Location = New System.Drawing.Point(104, 49)
		Me.Label7.Name = "Label7"
		Me.Label7.Size = New System.Drawing.Size(64, 16)
		Me.Label7.TabIndex = 3
		Me.Label7.Text = "Item Value"
		'
		'Label6
		'
		Me.Label6.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Underline, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label6.Location = New System.Drawing.Point(11, 49)
		Me.Label6.Name = "Label6"
		Me.Label6.Size = New System.Drawing.Size(40, 16)
		Me.Label6.TabIndex = 2
		Me.Label6.Text = "Item"
		'
		'txtTherm
		'
		Me.txtTherm.Location = New System.Drawing.Point(104, 66)
		Me.txtTherm.Name = "txtTherm"
		Me.txtTherm.Size = New System.Drawing.Size(168, 20)
		Me.txtTherm.TabIndex = 5
		Me.txtTherm.Text = ""
		'
		'chkThermometer
		'
		Me.chkThermometer.Location = New System.Drawing.Point(11, 65)
		Me.chkThermometer.Name = "chkThermometer"
		Me.chkThermometer.Size = New System.Drawing.Size(96, 24)
		Me.chkThermometer.TabIndex = 4
		Me.chkThermometer.Text = "Thermometer"
		'
		'Label8
		'
		Me.Label8.Location = New System.Drawing.Point(8, 22)
		Me.Label8.Name = "Label8"
		Me.Label8.Size = New System.Drawing.Size(80, 16)
		Me.Label8.TabIndex = 0
		Me.Label8.Text = "Children Size:"
		Me.Label8.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'cboSizeChild
		'
		Me.cboSizeChild.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
		Me.cboSizeChild.Items.AddRange(New Object() {"0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0", "1.5", "2.0", "4.0"})
		Me.cboSizeChild.Location = New System.Drawing.Point(103, 20)
		Me.cboSizeChild.Name = "cboSizeChild"
		Me.cboSizeChild.Size = New System.Drawing.Size(97, 21)
		Me.cboSizeChild.TabIndex = 1
		'
		'txtProcess
		'
		Me.txtProcess.Location = New System.Drawing.Point(103, 143)
		Me.txtProcess.Name = "txtProcess"
		Me.txtProcess.Size = New System.Drawing.Size(169, 20)
		Me.txtProcess.TabIndex = 11
		Me.txtProcess.Text = ""
		'
		'chkProcess
		'
		Me.chkProcess.Location = New System.Drawing.Point(11, 140)
		Me.chkProcess.Name = "chkProcess"
		Me.chkProcess.Size = New System.Drawing.Size(117, 24)
		Me.chkProcess.TabIndex = 10
		Me.chkProcess.Text = "From File"
		'
		'Label9
		'
		Me.Label9.Location = New System.Drawing.Point(8, 169)
		Me.Label9.Name = "Label9"
		Me.Label9.Size = New System.Drawing.Size(264, 40)
		Me.Label9.TabIndex = 12
		Me.Label9.Text = "From File will display a valid url or file  in a new process. Double clicking the" & _
		" globe child will start the process."
		'
		'frmTag
		'
		Me.AutoScaleBaseSize = New System.Drawing.Size(5, 13)
		Me.ClientSize = New System.Drawing.Size(328, 414)
		Me.Controls.Add(Me.GroupBox1)
		Me.Controls.Add(Me.Label5)
		Me.Controls.Add(Me.cboSizeW)
		Me.Controls.Add(Me.Label4)
		Me.Controls.Add(Me.cboSizeH)
		Me.Controls.Add(Me.Label3)
		Me.Controls.Add(Me.cboImages)
		Me.Controls.Add(Me.btnSave)
		Me.Controls.Add(Me.txtTagName)
		Me.Controls.Add(Me.txtTagID)
		Me.Controls.Add(Me.Label2)
		Me.Controls.Add(Me.Label1)
		Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
		Me.MaximizeBox = False
		Me.MinimizeBox = False
		Me.Name = "frmTag"
		Me.Text = "Viewer Tag Configuration"
		Me.GroupBox1.ResumeLayout(False)
		Me.ResumeLayout(False)

	End Sub

#End Region

	Private mTag As TagPlus	' inherits SIOViewer.Tag and extends some properties
	Private mValid As Boolean = False

	Friend Property TagPlus() As TagPlus
		Get
			Return mTag
		End Get
		Set(ByVal Value As TagPlus)
			mTag = Value
		End Set
	End Property

	Public ReadOnly Property Valid() As Boolean
		Get
			Return mValid

		End Get
	End Property
	Private Sub frmTag_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles MyBase.Load
		Try
			'load the combo from our TagImage enumerated values...
			cboImages.DataSource = System.Enum.GetValues(GetType(TagImages))
			cboImages.SelectedIndex = 0

			'set the default size values
			cboSizeChild.SelectedItem = Format(gTagChildSizeDefault, "#0.0")
			cboSizeH.SelectedItem = Format(gTagHieghtDefault, "#0.0")
			cboSizeW.SelectedItem = Format(gTagWidthDefault, "#0.0")


			txtTagID.Text = String.Empty
			txtTagName.Text = String.Empty
			txtTherm.Text = String.Empty
			txtXray.Text = String.Empty
			txtEKG.Text = String.Empty
			If Not mTag Is Nothing Then
				PopFromTag()
			End If

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Tag Form Load Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub

	Private Sub PopFromTag()
		txtTagID.Text = mTag.ID
		txtTagName.Text = mTag.Name
		cboImages.SelectedItem = mTag.ImageEnum

		'TODO: Note: how do I figure out what the current tag size is?
		'I added my own values in the super tag (tagPlus)- Look into adding these
		'properties to the Sioviewer.Tag
		cboSizeH.SelectedItem = Format(mTag.ImageHeight, "#0.0")
		cboSizeW.SelectedItem = Format(mTag.ImageWidth, "#0.0")


		If mTag.Children.Count > 0 Then
			Dim fsize As Single
			Dim tc As SIO3DViewer.TagChild
			For Each tc In mTag.Children
				fsize = GetChildSize(tc)
				Select Case tc.Key.ToString
					Case TagImages.Thermometer.ToString
						chkThermometer.Checked = True
						txtTherm.Text = tc.Data.ToString
					Case TagImages.Heartbeat.ToString
						chkEKG.Checked = True
						txtEKG.Text = tc.Data.ToString
					Case TagImages.Xray.ToString
						chkXray.Checked = True
						txtXray.Text = tc.Data.ToString
					Case TagImages.Globe.ToString
						chkProcess.Checked = True
						txtProcess.Text = tc.Data.ToString
				End Select
			Next
			cboSizeChild.SelectedItem = Format(fsize, "#0.0")
		End If

	End Sub


	Private Function IsValid() As Boolean
		Dim bRet As Boolean = True
		Select Case True
			Case txtTagName.Text = String.Empty
				Return False
			Case txtTagID.Text = String.Empty
				Return False
			Case cboImages.SelectedItem Is Nothing
				Return False
		End Select
		Return True

	End Function
	Private Sub btnSave_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnSave.Click
		Try
			Dim tc As SIO3DViewer.TagChild
			If IsValid() Then
				'set the default tag position to 0,0,0 in real coordinates
				Dim p As Point3D = ToViewerCoord(0, 0, 0)
				If Not mTag Is Nothing Then
					'get and save the current Tag's viewer coordinates
					p.X = mTag.X
					p.Y = mTag.Y
					p.Z = mTag.Z
				End If
				mTag = CreateFigure(CType(cboImages.SelectedValue, TagImages), CType(cboSizeW.SelectedItem, Single), CType(cboSizeH.SelectedItem, Single), txtTagID.Text, txtTagName.Text)
				mTag.X = p.X
				mTag.Y = p.Y
				mTag.Z = p.Z
				If chkThermometer.Checked Then
					tc = New SIO3DViewer.TagChild(TagImages.Thermometer.ToString, CType(cboSizeChild.SelectedItem, Single), CType(cboSizeChild.SelectedItem, Single))
					tc.Data = txtTherm.Text
					mTag.Children.Add(TagImages.Thermometer.ToString, tc)
				End If
				If chkEKG.Checked Then
					tc = New SIO3DViewer.TagChild(TagImages.Heartbeat.ToString, CType(cboSizeChild.SelectedItem, Single), CType(cboSizeChild.SelectedItem, Single))
					tc.Data = txtEKG.Text
					mTag.Children.Add(TagImages.Heartbeat.ToString, tc)
				End If
				If chkXray.Checked Then
					tc = New SIO3DViewer.TagChild(TagImages.Xray.ToString, CType(cboSizeChild.SelectedItem, Single), CType(cboSizeChild.SelectedItem, Single))
					tc.Data = txtXray.Text
					mTag.Children.Add(TagImages.Xray.ToString, tc)
				End If
				If chkProcess.Checked Then
					tc = New SIO3DViewer.TagChild(TagImages.Globe.ToString, CType(cboSizeChild.SelectedItem, Single), CType(cboSizeChild.SelectedItem, Single))
					tc.Data = txtProcess.Text
					mTag.Children.Add(TagImages.Globe.ToString, tc)

				End If
				If mTag.Children.Count > 0 Then
					mTag.Children.Visible = True
				End If
				mValid = True
				Me.Close()

			Else
				Throw New Exception("Tag fields are not valid.")
				mValid = False
			End If

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Tag Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub



	Private Sub txtTagID_KeyPress(ByVal sender As Object, ByVal e As System.Windows.Forms.KeyPressEventArgs) Handles txtTagID.KeyPress
		IntegerOrControl(e)
	End Sub
End Class
