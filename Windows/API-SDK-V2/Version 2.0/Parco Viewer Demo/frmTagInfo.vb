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


Public Class frmTagInfo
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
	Friend WithEvents lblID As System.Windows.Forms.Label
	Friend WithEvents lblName As System.Windows.Forms.Label
	Friend WithEvents Label1 As System.Windows.Forms.Label
	Friend WithEvents Label2 As System.Windows.Forms.Label
	Friend WithEvents lblChild As System.Windows.Forms.Label
	Friend WithEvents lblChildData As System.Windows.Forms.Label
	Friend WithEvents pnlChild As System.Windows.Forms.Panel
	Friend WithEvents PictureBox1 As System.Windows.Forms.PictureBox
	Friend WithEvents ImageList1 As System.Windows.Forms.ImageList
	Friend WithEvents Label3 As System.Windows.Forms.Label
	Friend WithEvents lblLocation As System.Windows.Forms.Label
	<System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
		Me.components = New System.ComponentModel.Container
		Dim resources As System.Resources.ResourceManager = New System.Resources.ResourceManager(GetType(frmTagInfo))
		Me.lblID = New System.Windows.Forms.Label
		Me.lblName = New System.Windows.Forms.Label
		Me.Label1 = New System.Windows.Forms.Label
		Me.Label2 = New System.Windows.Forms.Label
		Me.pnlChild = New System.Windows.Forms.Panel
		Me.PictureBox1 = New System.Windows.Forms.PictureBox
		Me.lblChildData = New System.Windows.Forms.Label
		Me.lblChild = New System.Windows.Forms.Label
		Me.ImageList1 = New System.Windows.Forms.ImageList(Me.components)
		Me.Label3 = New System.Windows.Forms.Label
		Me.lblLocation = New System.Windows.Forms.Label
		Me.pnlChild.SuspendLayout()
		Me.SuspendLayout()
		'
		'lblID
		'
		Me.lblID.ForeColor = System.Drawing.Color.Navy
		Me.lblID.Location = New System.Drawing.Point(71, 10)
		Me.lblID.Name = "lblID"
		Me.lblID.Size = New System.Drawing.Size(216, 16)
		Me.lblID.TabIndex = 0
		Me.lblID.Text = "lblID"
		Me.lblID.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'lblName
		'
		Me.lblName.ForeColor = System.Drawing.Color.Navy
		Me.lblName.Location = New System.Drawing.Point(71, 24)
		Me.lblName.Name = "lblName"
		Me.lblName.Size = New System.Drawing.Size(216, 16)
		Me.lblName.TabIndex = 1
		Me.lblName.Text = "lblName"
		Me.lblName.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'Label1
		'
		Me.Label1.Location = New System.Drawing.Point(10, 9)
		Me.Label1.Name = "Label1"
		Me.Label1.Size = New System.Drawing.Size(48, 16)
		Me.Label1.TabIndex = 2
		Me.Label1.Text = "Tag ID:"
		Me.Label1.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'Label2
		'
		Me.Label2.Location = New System.Drawing.Point(18, 24)
		Me.Label2.Name = "Label2"
		Me.Label2.Size = New System.Drawing.Size(40, 16)
		Me.Label2.TabIndex = 3
		Me.Label2.Text = "Name:"
		Me.Label2.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'pnlChild
		'
		Me.pnlChild.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
					Or System.Windows.Forms.AnchorStyles.Left) _
					Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
		Me.pnlChild.Controls.Add(Me.PictureBox1)
		Me.pnlChild.Controls.Add(Me.lblChildData)
		Me.pnlChild.Controls.Add(Me.lblChild)
		Me.pnlChild.Location = New System.Drawing.Point(8, 56)
		Me.pnlChild.Name = "pnlChild"
		Me.pnlChild.Size = New System.Drawing.Size(320, 168)
		Me.pnlChild.TabIndex = 7
		'
		'PictureBox1
		'
		Me.PictureBox1.Location = New System.Drawing.Point(96, 40)
		Me.PictureBox1.Name = "PictureBox1"
		Me.PictureBox1.Size = New System.Drawing.Size(112, 112)
		Me.PictureBox1.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.PictureBox1.TabIndex = 6
		Me.PictureBox1.TabStop = False
		'
		'lblChildData
		'
		Me.lblChildData.ForeColor = System.Drawing.Color.Navy
		Me.lblChildData.Location = New System.Drawing.Point(91, 8)
		Me.lblChildData.Name = "lblChildData"
		Me.lblChildData.Size = New System.Drawing.Size(213, 16)
		Me.lblChildData.TabIndex = 5
		Me.lblChildData.Text = "Label3"
		Me.lblChildData.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'lblChild
		'
		Me.lblChild.Location = New System.Drawing.Point(8, 8)
		Me.lblChild.Name = "lblChild"
		Me.lblChild.Size = New System.Drawing.Size(72, 16)
		Me.lblChild.TabIndex = 4
		Me.lblChild.Text = "Temperature:"
		Me.lblChild.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'ImageList1
		'
		Me.ImageList1.ImageSize = New System.Drawing.Size(16, 16)
		Me.ImageList1.ImageStream = CType(resources.GetObject("ImageList1.ImageStream"), System.Windows.Forms.ImageListStreamer)
		Me.ImageList1.TransparentColor = System.Drawing.Color.Transparent
		'
		'Label3
		'
		Me.Label3.Location = New System.Drawing.Point(2, 38)
		Me.Label3.Name = "Label3"
		Me.Label3.Size = New System.Drawing.Size(56, 16)
		Me.Label3.TabIndex = 9
		Me.Label3.Text = "Location:"
		Me.Label3.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'lblLocation
		'
		Me.lblLocation.ForeColor = System.Drawing.Color.Navy
		Me.lblLocation.Location = New System.Drawing.Point(71, 38)
		Me.lblLocation.Name = "lblLocation"
		Me.lblLocation.Size = New System.Drawing.Size(216, 16)
		Me.lblLocation.TabIndex = 8
		Me.lblLocation.Text = "lblLocation"
		Me.lblLocation.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'frmTagInfo
		'
		Me.AutoScaleBaseSize = New System.Drawing.Size(5, 13)
		Me.ClientSize = New System.Drawing.Size(336, 230)
		Me.Controls.Add(Me.Label3)
		Me.Controls.Add(Me.lblLocation)
		Me.Controls.Add(Me.pnlChild)
		Me.Controls.Add(Me.Label2)
		Me.Controls.Add(Me.Label1)
		Me.Controls.Add(Me.lblName)
		Me.Controls.Add(Me.lblID)
		Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
		Me.MaximizeBox = False
		Me.MinimizeBox = False
		Me.Name = "frmTagInfo"
		Me.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen
		Me.Text = "Asset/Person Information"
		Me.pnlChild.ResumeLayout(False)
		Me.ResumeLayout(False)

	End Sub

#End Region

	Private mtag As TagPlus
	Private mTagChild As SIO3DViewer.TagChild


	Friend Property TagPlus() As TagPlus
		Get
			Return mtag
		End Get
		Set(ByVal Value As TagPlus)
			mtag = Value
		End Set
	End Property

	Friend Property TagChild() As SIO3DViewer.TagChild
		Get
			Return mTagChild
		End Get
		Set(ByVal Value As SIO3DViewer.TagChild)
			mTagChild = Value
		End Set
	End Property
	Private Sub frmTagInfo_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
		If Not mtag Is Nothing Then
			lblID.Text = mtag.ID
			lblName.Text = mtag.Name
			lblLocation.Text = ToRealCoord(mtag.X, mtag.Y, mtag.Z).ToString

		End If
		If Not mTagChild Is Nothing Then
			pnlChild.Visible = True
			'we have preloaded images in an imagelist to show here, could just as well be from a database or other source.
			Select Case mTagChild.Key.ToString
				Case TagImages.Thermometer.ToString
					PictureBox1.Image = ImageList1.Images(2)
					lblChild.Text = "Temperature:"
				Case TagImages.Heartbeat.ToString
					PictureBox1.Image = ImageList1.Images(1)
					lblChild.Text = "EKG:"
				Case TagImages.Xray.ToString
					PictureBox1.Image = ImageList1.Images(0)
					lblChild.Text = "X-Ray:"
			End Select
			lblChildData.Text = mTagChild.Data.ToString

		Else
			pnlChild.Visible = False
			Me.Height = 120
		End If
	End Sub
End Class
