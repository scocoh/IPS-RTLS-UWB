'##### CONFIDENTIAL - CONFIDENTIAL - CONFIDENTIAL ######
'		                    Parco RTLS™ System
'All information and source code contained herein is confidential and proprietary.
'Copying or modifying this source code is strictly prohibited unless under license of Parco Wireless.
'Copyright © 2001-2004 Parco Merged Media Inc. / Parco Wireless
'All rights reserved.
'##### CONFIDENTIAL - CONFIDENTIAL - CONFIDENTIAL ######
'Author:     Michael Farnsworth, Standard I-O Inc.
'Version:   1.0
'Date:       6/2/2004
'
'Modification/Author/Date:
'

Imports Parco
Imports SIO3DViewer
Imports System.IO
Imports Microsoft.DirectX
Imports Microsoft.DirectX.Direct3D
Imports System.Runtime.Serialization
Imports System.Runtime.Serialization.Formatters

Public Class Form1
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
    Friend WithEvents Panel1 As System.Windows.Forms.Panel
    Friend WithEvents Panel2 As System.Windows.Forms.Panel
    Friend WithEvents picWorld As SIO3DViewer.DefaultMiniMap
    Friend WithEvents mViewer As SIO3DViewer.SIO3DViewer
    Friend WithEvents TextBox1 As System.Windows.Forms.TextBox
    Friend WithEvents picLookNegativeX As System.Windows.Forms.PictureBox
    Friend WithEvents picLookNegativeZ As System.Windows.Forms.PictureBox
    Friend WithEvents picLookPositiveX As System.Windows.Forms.PictureBox
    Friend WithEvents picLookPositiveZ As System.Windows.Forms.PictureBox
    Friend WithEvents Panel3 As System.Windows.Forms.Panel
    Friend WithEvents picTiltBackward As System.Windows.Forms.PictureBox
    Friend WithEvents picSpinRight As System.Windows.Forms.PictureBox
    Friend WithEvents picMoveBackward As System.Windows.Forms.PictureBox
    Friend WithEvents picSpinLeft As System.Windows.Forms.PictureBox
    Friend WithEvents picMoveDown As System.Windows.Forms.PictureBox
    Friend WithEvents picZoomOut As System.Windows.Forms.PictureBox
    Friend WithEvents picTiltForward As System.Windows.Forms.PictureBox
    Friend WithEvents picMoveRight As System.Windows.Forms.PictureBox
    Friend WithEvents picMoveForward As System.Windows.Forms.PictureBox
    Friend WithEvents picMoveLeft As System.Windows.Forms.PictureBox
    Friend WithEvents picMoveUp As System.Windows.Forms.PictureBox
    Friend WithEvents picZoomIn As System.Windows.Forms.PictureBox
    Friend WithEvents Label1 As System.Windows.Forms.Label
	Friend WithEvents btnConnect As System.Windows.Forms.Button
    Friend WithEvents btnDisConnect As System.Windows.Forms.Button
    Friend WithEvents rbParco As System.Windows.Forms.RadioButton
    Friend WithEvents rbLocalServer As System.Windows.Forms.RadioButton
	Friend WithEvents TabControl1 As System.Windows.Forms.TabControl
	Friend WithEvents TabPageDataSource As System.Windows.Forms.TabPage
	Friend WithEvents GroupBox1 As System.Windows.Forms.GroupBox
	Friend WithEvents GroupBox2 As System.Windows.Forms.GroupBox
	Friend WithEvents rbFullStream As System.Windows.Forms.RadioButton
	Friend WithEvents rbSubscription As System.Windows.Forms.RadioButton
	Friend WithEvents btnLoadRes As System.Windows.Forms.Button
	Friend WithEvents Label17 As System.Windows.Forms.Label
	Friend WithEvents cboResourses As System.Windows.Forms.ComboBox
	Friend WithEvents Label2 As System.Windows.Forms.Label
	Friend WithEvents BlinkData As ucBlink.Blinker
	Friend WithEvents Label4 As System.Windows.Forms.Label
	Friend WithEvents lblConState As System.Windows.Forms.Label
	Friend WithEvents TabPageTags As System.Windows.Forms.TabPage
	Friend WithEvents btnTagEdit As System.Windows.Forms.Button
	Friend WithEvents btnTagRem As System.Windows.Forms.Button
	Friend WithEvents btnTagAdd As System.Windows.Forms.Button
	Friend WithEvents lstTags As System.Windows.Forms.ListBox
	Friend WithEvents Label5 As System.Windows.Forms.Label
	Friend WithEvents ContextMenu1 As System.Windows.Forms.ContextMenu
	Friend WithEvents TabPageTEvents As System.Windows.Forms.TabPage
	Friend WithEvents lstEvts As System.Windows.Forms.ListBox
	Friend WithEvents LinkLabelClearEvts As System.Windows.Forms.LinkLabel
	Friend WithEvents btnTagTrigEdit As System.Windows.Forms.Button
	Friend WithEvents btnTagTrigDel As System.Windows.Forms.Button
	Friend WithEvents TabPageTrigs As System.Windows.Forms.TabPage
	Friend WithEvents lstTriggers As System.Windows.Forms.ListBox
	Friend WithEvents Label3 As System.Windows.Forms.Label
	Friend WithEvents btnTrigEdit As System.Windows.Forms.Button
	Friend WithEvents btnTrigDel As System.Windows.Forms.Button
	Friend WithEvents btnTrigAdd As System.Windows.Forms.Button
	Friend WithEvents TabPageTagTrig As System.Windows.Forms.TabPage
	Friend WithEvents btnTagTrigEdit2 As System.Windows.Forms.Button
	Friend WithEvents btnTagTrigDel2 As System.Windows.Forms.Button
	Friend WithEvents lstTagTrig As System.Windows.Forms.ListBox
	Friend WithEvents Label6 As System.Windows.Forms.Label
    Friend WithEvents chkShowAreaTrigs As System.Windows.Forms.CheckBox
	Friend WithEvents chkShowStats As System.Windows.Forms.CheckBox
	<System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
		Dim resources As System.Resources.ResourceManager = New System.Resources.ResourceManager(GetType(Form1))
		Me.mViewer = New SIO3DViewer.SIO3DViewer
		Me.picWorld = New SIO3DViewer.DefaultMiniMap
		Me.ContextMenu1 = New System.Windows.Forms.ContextMenu
		Me.Panel1 = New System.Windows.Forms.Panel
		Me.Panel2 = New System.Windows.Forms.Panel
		Me.TabControl1 = New System.Windows.Forms.TabControl
		Me.TabPageDataSource = New System.Windows.Forms.TabPage
		Me.Label4 = New System.Windows.Forms.Label
		Me.BlinkData = New ucBlink.Blinker
		Me.lblConState = New System.Windows.Forms.Label
		Me.Label2 = New System.Windows.Forms.Label
		Me.btnLoadRes = New System.Windows.Forms.Button
		Me.Label17 = New System.Windows.Forms.Label
		Me.cboResourses = New System.Windows.Forms.ComboBox
		Me.GroupBox2 = New System.Windows.Forms.GroupBox
		Me.rbSubscription = New System.Windows.Forms.RadioButton
		Me.rbFullStream = New System.Windows.Forms.RadioButton
		Me.GroupBox1 = New System.Windows.Forms.GroupBox
		Me.rbParco = New System.Windows.Forms.RadioButton
		Me.rbLocalServer = New System.Windows.Forms.RadioButton
		Me.btnConnect = New System.Windows.Forms.Button
		Me.btnDisConnect = New System.Windows.Forms.Button
		Me.chkShowStats = New System.Windows.Forms.CheckBox
		Me.TabPageTags = New System.Windows.Forms.TabPage
		Me.btnTagTrigDel = New System.Windows.Forms.Button
		Me.btnTagTrigEdit = New System.Windows.Forms.Button
		Me.btnTagEdit = New System.Windows.Forms.Button
		Me.btnTagRem = New System.Windows.Forms.Button
		Me.btnTagAdd = New System.Windows.Forms.Button
		Me.lstTags = New System.Windows.Forms.ListBox
		Me.Label5 = New System.Windows.Forms.Label
		Me.TabPageTagTrig = New System.Windows.Forms.TabPage
		Me.btnTagTrigEdit2 = New System.Windows.Forms.Button
		Me.btnTagTrigDel2 = New System.Windows.Forms.Button
		Me.lstTagTrig = New System.Windows.Forms.ListBox
		Me.Label6 = New System.Windows.Forms.Label
		Me.TabPageTrigs = New System.Windows.Forms.TabPage
		Me.chkShowAreaTrigs = New System.Windows.Forms.CheckBox
		Me.btnTrigEdit = New System.Windows.Forms.Button
		Me.btnTrigDel = New System.Windows.Forms.Button
		Me.btnTrigAdd = New System.Windows.Forms.Button
		Me.lstTriggers = New System.Windows.Forms.ListBox
		Me.Label3 = New System.Windows.Forms.Label
		Me.TabPageTEvents = New System.Windows.Forms.TabPage
		Me.LinkLabelClearEvts = New System.Windows.Forms.LinkLabel
		Me.lstEvts = New System.Windows.Forms.ListBox
		Me.Label1 = New System.Windows.Forms.Label
		Me.Panel3 = New System.Windows.Forms.Panel
		Me.picTiltBackward = New System.Windows.Forms.PictureBox
		Me.picSpinRight = New System.Windows.Forms.PictureBox
		Me.picMoveBackward = New System.Windows.Forms.PictureBox
		Me.picSpinLeft = New System.Windows.Forms.PictureBox
		Me.picMoveDown = New System.Windows.Forms.PictureBox
		Me.picZoomOut = New System.Windows.Forms.PictureBox
		Me.picTiltForward = New System.Windows.Forms.PictureBox
		Me.picMoveRight = New System.Windows.Forms.PictureBox
		Me.picMoveForward = New System.Windows.Forms.PictureBox
		Me.picMoveLeft = New System.Windows.Forms.PictureBox
		Me.picMoveUp = New System.Windows.Forms.PictureBox
		Me.picZoomIn = New System.Windows.Forms.PictureBox
		Me.picLookPositiveZ = New System.Windows.Forms.PictureBox
		Me.picLookNegativeX = New System.Windows.Forms.PictureBox
		Me.picLookNegativeZ = New System.Windows.Forms.PictureBox
		Me.picLookPositiveX = New System.Windows.Forms.PictureBox
		Me.TextBox1 = New System.Windows.Forms.TextBox
		Me.Panel1.SuspendLayout()
		Me.Panel2.SuspendLayout()
		Me.TabControl1.SuspendLayout()
		Me.TabPageDataSource.SuspendLayout()
		Me.GroupBox2.SuspendLayout()
		Me.GroupBox1.SuspendLayout()
		Me.TabPageTags.SuspendLayout()
		Me.TabPageTagTrig.SuspendLayout()
		Me.TabPageTrigs.SuspendLayout()
		Me.TabPageTEvents.SuspendLayout()
		Me.Panel3.SuspendLayout()
		Me.SuspendLayout()
		'
		'mViewer
		'
		Me.mViewer.AccelerateMovement = False
		Me.mViewer.AccelerationMultiplier = 3.0!
		Me.mViewer.AllowAreaSelection = True
		Me.mViewer.AllowMultipleSelection = True
		Me.mViewer.AngularUnit = 0.03490658!
		Me.mViewer.AutoSelectOnClick = True
		Me.mViewer.CausesValidation = False
		Me.mViewer.Dock = System.Windows.Forms.DockStyle.Fill
		Me.mViewer.FarClipPlane = 4000.0!
		Me.mViewer.FieldOfView = 0.7853982!
		Me.mViewer.LinearUnit = 1.0!
		Me.mViewer.Location = New System.Drawing.Point(0, 0)
		Me.mViewer.MiniMap = Me.picWorld
		Me.mViewer.Name = "mViewer"
		Me.mViewer.NearClipPlane = 1.0!
		Me.mViewer.SelectionFloorColor = System.Drawing.Color.Empty
		Me.mViewer.SelectionFloorImageKey = Nothing
		Me.mViewer.SelectionLineColor = System.Drawing.Color.Black
		Me.mViewer.SelectionRoofColor = System.Drawing.Color.Empty
		Me.mViewer.SelectionRoofImageKey = Nothing
		Me.mViewer.SelectionWallBottom = 0.0!
		Me.mViewer.SelectionWallColor = System.Drawing.Color.Empty
		Me.mViewer.SelectionWallImageKey = Nothing
		Me.mViewer.SelectionWallTop = 3.0!
		Me.mViewer.ShowStatistics = False
		Me.mViewer.Size = New System.Drawing.Size(804, 334)
		Me.mViewer.TabIndex = 0
		Me.mViewer.TargetFrameRate = 20.0!
		Me.mViewer.Text = "mViewer"
		Me.mViewer.UnitsPerSecondMovement = 20.0!
		'
		'picWorld
		'
		Me.picWorld.CausesValidation = False
		Me.picWorld.Location = New System.Drawing.Point(40, 37)
		Me.picWorld.Name = "picWorld"
		Me.picWorld.ObjectColor = System.Drawing.Color.Navy
		Me.picWorld.ObjectSize = 3
		Me.picWorld.Size = New System.Drawing.Size(112, 96)
		Me.picWorld.TabIndex = 0
		Me.picWorld.UseTagUserColor = True
		Me.picWorld.ViewAreaColor = System.Drawing.Color.DarkRed
		Me.picWorld.ViewLineWidth = 2
		'
		'Panel1
		'
		Me.Panel1.Controls.Add(Me.mViewer)
		Me.Panel1.Dock = System.Windows.Forms.DockStyle.Fill
		Me.Panel1.Location = New System.Drawing.Point(0, 0)
		Me.Panel1.Name = "Panel1"
		Me.Panel1.Size = New System.Drawing.Size(804, 334)
		Me.Panel1.TabIndex = 2
		'
		'Panel2
		'
		Me.Panel2.Controls.Add(Me.TabControl1)
		Me.Panel2.Controls.Add(Me.Label1)
		Me.Panel2.Controls.Add(Me.Panel3)
		Me.Panel2.Controls.Add(Me.picLookPositiveZ)
		Me.Panel2.Controls.Add(Me.picLookNegativeX)
		Me.Panel2.Controls.Add(Me.picLookNegativeZ)
		Me.Panel2.Controls.Add(Me.picLookPositiveX)
		Me.Panel2.Controls.Add(Me.TextBox1)
		Me.Panel2.Controls.Add(Me.picWorld)
		Me.Panel2.Dock = System.Windows.Forms.DockStyle.Bottom
		Me.Panel2.Font = New System.Drawing.Font("Tahoma", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Panel2.Location = New System.Drawing.Point(0, 334)
		Me.Panel2.Name = "Panel2"
		Me.Panel2.Size = New System.Drawing.Size(804, 172)
		Me.Panel2.TabIndex = 0
		'
		'TabControl1
		'
		Me.TabControl1.Anchor = CType(((System.Windows.Forms.AnchorStyles.Bottom Or System.Windows.Forms.AnchorStyles.Left) _
					Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
		Me.TabControl1.Controls.Add(Me.TabPageDataSource)
		Me.TabControl1.Controls.Add(Me.TabPageTags)
		Me.TabControl1.Controls.Add(Me.TabPageTagTrig)
		Me.TabControl1.Controls.Add(Me.TabPageTrigs)
		Me.TabControl1.Controls.Add(Me.TabPageTEvents)
		Me.TabControl1.Location = New System.Drawing.Point(404, 4)
		Me.TabControl1.Name = "TabControl1"
		Me.TabControl1.SelectedIndex = 0
		Me.TabControl1.Size = New System.Drawing.Size(392, 164)
		Me.TabControl1.TabIndex = 9
		'
		'TabPageDataSource
		'
		Me.TabPageDataSource.Controls.Add(Me.Label4)
		Me.TabPageDataSource.Controls.Add(Me.BlinkData)
		Me.TabPageDataSource.Controls.Add(Me.lblConState)
		Me.TabPageDataSource.Controls.Add(Me.Label2)
		Me.TabPageDataSource.Controls.Add(Me.btnLoadRes)
		Me.TabPageDataSource.Controls.Add(Me.Label17)
		Me.TabPageDataSource.Controls.Add(Me.cboResourses)
		Me.TabPageDataSource.Controls.Add(Me.GroupBox2)
		Me.TabPageDataSource.Controls.Add(Me.GroupBox1)
		Me.TabPageDataSource.Controls.Add(Me.btnConnect)
		Me.TabPageDataSource.Controls.Add(Me.btnDisConnect)
		Me.TabPageDataSource.Controls.Add(Me.chkShowStats)
		Me.TabPageDataSource.Location = New System.Drawing.Point(4, 22)
		Me.TabPageDataSource.Name = "TabPageDataSource"
		Me.TabPageDataSource.Size = New System.Drawing.Size(384, 138)
		Me.TabPageDataSource.TabIndex = 0
		Me.TabPageDataSource.Text = "Data Source"
		'
		'Label4
		'
		Me.Label4.Location = New System.Drawing.Point(209, 102)
		Me.Label4.Name = "Label4"
		Me.Label4.Size = New System.Drawing.Size(80, 13)
		Me.Label4.TabIndex = 21
		Me.Label4.Text = "Data Activity:"
		Me.Label4.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'BlinkData
		'
		Me.BlinkData.BackColor = System.Drawing.Color.Gray
		Me.BlinkData.BlinkRate = 500
		Me.BlinkData.Location = New System.Drawing.Point(299, 102)
		Me.BlinkData.Name = "BlinkData"
		Me.BlinkData.Size = New System.Drawing.Size(24, 10)
		Me.BlinkData.TabIndex = 20
		'
		'lblConState
		'
		Me.lblConState.ForeColor = System.Drawing.Color.Red
		Me.lblConState.Location = New System.Drawing.Point(296, 81)
		Me.lblConState.Name = "lblConState"
		Me.lblConState.Size = New System.Drawing.Size(72, 8)
		Me.lblConState.TabIndex = 19
		Me.lblConState.Text = "Disconnected"
		Me.lblConState.TextAlign = System.Drawing.ContentAlignment.MiddleLeft
		'
		'Label2
		'
		Me.Label2.Location = New System.Drawing.Point(216, 81)
		Me.Label2.Name = "Label2"
		Me.Label2.Size = New System.Drawing.Size(64, 8)
		Me.Label2.TabIndex = 18
		Me.Label2.Text = "Connection:"
		Me.Label2.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'btnLoadRes
		'
		Me.btnLoadRes.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnLoadRes.Location = New System.Drawing.Point(316, 41)
		Me.btnLoadRes.Name = "btnLoadRes"
		Me.btnLoadRes.Size = New System.Drawing.Size(40, 20)
		Me.btnLoadRes.TabIndex = 17
		Me.btnLoadRes.Text = "Load"
		'
		'Label17
		'
		Me.Label17.Location = New System.Drawing.Point(119, 44)
		Me.Label17.Name = "Label17"
		Me.Label17.Size = New System.Drawing.Size(64, 14)
		Me.Label17.TabIndex = 16
		Me.Label17.Text = "Resources:"
		Me.Label17.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'cboResourses
		'
		Me.cboResourses.Location = New System.Drawing.Point(184, 41)
		Me.cboResourses.Name = "cboResourses"
		Me.cboResourses.Size = New System.Drawing.Size(128, 21)
		Me.cboResourses.TabIndex = 15
		'
		'GroupBox2
		'
		Me.GroupBox2.Controls.Add(Me.rbSubscription)
		Me.GroupBox2.Controls.Add(Me.rbFullStream)
		Me.GroupBox2.Location = New System.Drawing.Point(6, 69)
		Me.GroupBox2.Name = "GroupBox2"
		Me.GroupBox2.Size = New System.Drawing.Size(110, 60)
		Me.GroupBox2.TabIndex = 1
		Me.GroupBox2.TabStop = False
		Me.GroupBox2.Text = "Connection Style"
		'
		'rbSubscription
		'
		Me.rbSubscription.Location = New System.Drawing.Point(8, 36)
		Me.rbSubscription.Name = "rbSubscription"
		Me.rbSubscription.Size = New System.Drawing.Size(88, 16)
		Me.rbSubscription.TabIndex = 1
		Me.rbSubscription.Text = "Subscription"
		'
		'rbFullStream
		'
		Me.rbFullStream.Location = New System.Drawing.Point(8, 16)
		Me.rbFullStream.Name = "rbFullStream"
		Me.rbFullStream.Size = New System.Drawing.Size(88, 16)
		Me.rbFullStream.TabIndex = 0
		Me.rbFullStream.Text = "Full Stream"
		'
		'GroupBox1
		'
		Me.GroupBox1.Controls.Add(Me.rbParco)
		Me.GroupBox1.Controls.Add(Me.rbLocalServer)
		Me.GroupBox1.Location = New System.Drawing.Point(6, 7)
		Me.GroupBox1.Name = "GroupBox1"
		Me.GroupBox1.Size = New System.Drawing.Size(110, 60)
		Me.GroupBox1.TabIndex = 0
		Me.GroupBox1.TabStop = False
		Me.GroupBox1.Text = "Server Location"
		'
		'rbParco
		'
		Me.rbParco.Location = New System.Drawing.Point(8, 16)
		Me.rbParco.Name = "rbParco"
		Me.rbParco.Size = New System.Drawing.Size(88, 16)
		Me.rbParco.TabIndex = 2
		Me.rbParco.Text = "Parco Server"
		'
		'rbLocalServer
		'
		Me.rbLocalServer.Location = New System.Drawing.Point(8, 35)
		Me.rbLocalServer.Name = "rbLocalServer"
		Me.rbLocalServer.Size = New System.Drawing.Size(88, 16)
		Me.rbLocalServer.TabIndex = 3
		Me.rbLocalServer.Text = "Local Server"
		'
		'btnConnect
		'
		Me.btnConnect.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnConnect.Location = New System.Drawing.Point(126, 75)
		Me.btnConnect.Name = "btnConnect"
		Me.btnConnect.Size = New System.Drawing.Size(75, 20)
		Me.btnConnect.TabIndex = 0
		Me.btnConnect.Text = "Connect"
		'
		'btnDisConnect
		'
		Me.btnDisConnect.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnDisConnect.Location = New System.Drawing.Point(126, 99)
		Me.btnDisConnect.Name = "btnDisConnect"
		Me.btnDisConnect.Size = New System.Drawing.Size(75, 20)
		Me.btnDisConnect.TabIndex = 1
		Me.btnDisConnect.Text = "Disconnect"
		'
		'chkShowStats
		'
		Me.chkShowStats.Location = New System.Drawing.Point(184, 13)
		Me.chkShowStats.Name = "chkShowStats"
		Me.chkShowStats.Size = New System.Drawing.Size(152, 16)
		Me.chkShowStats.TabIndex = 10
		Me.chkShowStats.Text = "Display Viewer Statisitics"
		'
		'TabPageTags
		'
		Me.TabPageTags.Controls.Add(Me.btnTagTrigDel)
		Me.TabPageTags.Controls.Add(Me.btnTagTrigEdit)
		Me.TabPageTags.Controls.Add(Me.btnTagEdit)
		Me.TabPageTags.Controls.Add(Me.btnTagRem)
		Me.TabPageTags.Controls.Add(Me.btnTagAdd)
		Me.TabPageTags.Controls.Add(Me.lstTags)
		Me.TabPageTags.Controls.Add(Me.Label5)
		Me.TabPageTags.Location = New System.Drawing.Point(4, 22)
		Me.TabPageTags.Name = "TabPageTags"
		Me.TabPageTags.Size = New System.Drawing.Size(384, 138)
		Me.TabPageTags.TabIndex = 1
		Me.TabPageTags.Text = "Tags"
		'
		'btnTagTrigDel
		'
		Me.btnTagTrigDel.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnTagTrigDel.Location = New System.Drawing.Point(159, 87)
		Me.btnTagTrigDel.Name = "btnTagTrigDel"
		Me.btnTagTrigDel.Size = New System.Drawing.Size(65, 20)
		Me.btnTagTrigDel.TabIndex = 32
		Me.btnTagTrigDel.Text = "Trig Del"
		'
		'btnTagTrigEdit
		'
		Me.btnTagTrigEdit.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnTagTrigEdit.Location = New System.Drawing.Point(159, 63)
		Me.btnTagTrigEdit.Name = "btnTagTrigEdit"
		Me.btnTagTrigEdit.Size = New System.Drawing.Size(65, 20)
		Me.btnTagTrigEdit.TabIndex = 31
		Me.btnTagTrigEdit.Text = "Trigger..."
		'
		'btnTagEdit
		'
		Me.btnTagEdit.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnTagEdit.Location = New System.Drawing.Point(159, 39)
		Me.btnTagEdit.Name = "btnTagEdit"
		Me.btnTagEdit.Size = New System.Drawing.Size(65, 20)
		Me.btnTagEdit.TabIndex = 30
		Me.btnTagEdit.Text = "Edit..."
		'
		'btnTagRem
		'
		Me.btnTagRem.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnTagRem.Location = New System.Drawing.Point(159, 111)
		Me.btnTagRem.Name = "btnTagRem"
		Me.btnTagRem.Size = New System.Drawing.Size(65, 20)
		Me.btnTagRem.TabIndex = 33
		Me.btnTagRem.Text = "Delete"
		'
		'btnTagAdd
		'
		Me.btnTagAdd.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnTagAdd.Location = New System.Drawing.Point(159, 15)
		Me.btnTagAdd.Name = "btnTagAdd"
		Me.btnTagAdd.Size = New System.Drawing.Size(65, 20)
		Me.btnTagAdd.TabIndex = 29
		Me.btnTagAdd.Text = "Add..."
		'
		'lstTags
		'
		Me.lstTags.Location = New System.Drawing.Point(11, 15)
		Me.lstTags.Name = "lstTags"
		Me.lstTags.Size = New System.Drawing.Size(141, 121)
		Me.lstTags.TabIndex = 28
		'
		'Label5
		'
		Me.Label5.Location = New System.Drawing.Point(8, 2)
		Me.Label5.Name = "Label5"
		Me.Label5.Size = New System.Drawing.Size(96, 12)
		Me.Label5.TabIndex = 27
		Me.Label5.Text = "Configured Tags:"
		'
		'TabPageTagTrig
		'
		Me.TabPageTagTrig.Controls.Add(Me.btnTagTrigEdit2)
		Me.TabPageTagTrig.Controls.Add(Me.btnTagTrigDel2)
		Me.TabPageTagTrig.Controls.Add(Me.lstTagTrig)
		Me.TabPageTagTrig.Controls.Add(Me.Label6)
		Me.TabPageTagTrig.Location = New System.Drawing.Point(4, 22)
		Me.TabPageTagTrig.Name = "TabPageTagTrig"
		Me.TabPageTagTrig.Size = New System.Drawing.Size(384, 138)
		Me.TabPageTagTrig.TabIndex = 4
		Me.TabPageTagTrig.Text = "Tag Triggers"
		'
		'btnTagTrigEdit2
		'
		Me.btnTagTrigEdit2.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnTagTrigEdit2.Location = New System.Drawing.Point(159, 15)
		Me.btnTagTrigEdit2.Name = "btnTagTrigEdit2"
		Me.btnTagTrigEdit2.Size = New System.Drawing.Size(65, 20)
		Me.btnTagTrigEdit2.TabIndex = 42
		Me.btnTagTrigEdit2.Text = "Edit..."
		'
		'btnTagTrigDel2
		'
		Me.btnTagTrigDel2.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnTagTrigDel2.Location = New System.Drawing.Point(159, 39)
		Me.btnTagTrigDel2.Name = "btnTagTrigDel2"
		Me.btnTagTrigDel2.Size = New System.Drawing.Size(65, 20)
		Me.btnTagTrigDel2.TabIndex = 43
		Me.btnTagTrigDel2.Text = "Delete"
		'
		'lstTagTrig
		'
		Me.lstTagTrig.Location = New System.Drawing.Point(11, 15)
		Me.lstTagTrig.Name = "lstTagTrig"
		Me.lstTagTrig.Size = New System.Drawing.Size(141, 121)
		Me.lstTagTrig.TabIndex = 40
		'
		'Label6
		'
		Me.Label6.Location = New System.Drawing.Point(10, 2)
		Me.Label6.Name = "Label6"
		Me.Label6.Size = New System.Drawing.Size(96, 12)
		Me.Label6.TabIndex = 39
		Me.Label6.Text = "Tag Triggers:"
		'
		'TabPageTrigs
		'
		Me.TabPageTrigs.Controls.Add(Me.chkShowAreaTrigs)
		Me.TabPageTrigs.Controls.Add(Me.btnTrigEdit)
		Me.TabPageTrigs.Controls.Add(Me.btnTrigDel)
		Me.TabPageTrigs.Controls.Add(Me.btnTrigAdd)
		Me.TabPageTrigs.Controls.Add(Me.lstTriggers)
		Me.TabPageTrigs.Controls.Add(Me.Label3)
		Me.TabPageTrigs.Location = New System.Drawing.Point(4, 22)
		Me.TabPageTrigs.Name = "TabPageTrigs"
		Me.TabPageTrigs.Size = New System.Drawing.Size(384, 138)
		Me.TabPageTrigs.TabIndex = 3
		Me.TabPageTrigs.Text = "Area Triggers"
		'
		'chkShowAreaTrigs
		'
		Me.chkShowAreaTrigs.Location = New System.Drawing.Point(160, 88)
		Me.chkShowAreaTrigs.Name = "chkShowAreaTrigs"
		Me.chkShowAreaTrigs.Size = New System.Drawing.Size(160, 24)
		Me.chkShowAreaTrigs.TabIndex = 39
		Me.chkShowAreaTrigs.Text = "Show Triggers in Viewer"
		'
		'btnTrigEdit
		'
		Me.btnTrigEdit.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnTrigEdit.Location = New System.Drawing.Point(159, 39)
		Me.btnTrigEdit.Name = "btnTrigEdit"
		Me.btnTrigEdit.Size = New System.Drawing.Size(65, 20)
		Me.btnTrigEdit.TabIndex = 37
		Me.btnTrigEdit.Text = "Edit..."
		'
		'btnTrigDel
		'
		Me.btnTrigDel.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnTrigDel.Location = New System.Drawing.Point(159, 63)
		Me.btnTrigDel.Name = "btnTrigDel"
		Me.btnTrigDel.Size = New System.Drawing.Size(65, 20)
		Me.btnTrigDel.TabIndex = 38
		Me.btnTrigDel.Text = "Delete"
		'
		'btnTrigAdd
		'
		Me.btnTrigAdd.FlatStyle = System.Windows.Forms.FlatStyle.Flat
		Me.btnTrigAdd.Location = New System.Drawing.Point(159, 15)
		Me.btnTrigAdd.Name = "btnTrigAdd"
		Me.btnTrigAdd.Size = New System.Drawing.Size(65, 20)
		Me.btnTrigAdd.TabIndex = 36
		Me.btnTrigAdd.Text = "Add..."
		'
		'lstTriggers
		'
		Me.lstTriggers.Location = New System.Drawing.Point(11, 15)
		Me.lstTriggers.Name = "lstTriggers"
		Me.lstTriggers.Size = New System.Drawing.Size(141, 121)
		Me.lstTriggers.TabIndex = 35
		'
		'Label3
		'
		Me.Label3.Location = New System.Drawing.Point(8, 2)
		Me.Label3.Name = "Label3"
		Me.Label3.Size = New System.Drawing.Size(96, 12)
		Me.Label3.TabIndex = 34
		Me.Label3.Text = "Triggers:"
		'
		'TabPageTEvents
		'
		Me.TabPageTEvents.Controls.Add(Me.LinkLabelClearEvts)
		Me.TabPageTEvents.Controls.Add(Me.lstEvts)
		Me.TabPageTEvents.Location = New System.Drawing.Point(4, 22)
		Me.TabPageTEvents.Name = "TabPageTEvents"
		Me.TabPageTEvents.Size = New System.Drawing.Size(384, 138)
		Me.TabPageTEvents.TabIndex = 2
		Me.TabPageTEvents.Text = "Trigger Events"
		'
		'LinkLabelClearEvts
		'
		Me.LinkLabelClearEvts.Anchor = CType((System.Windows.Forms.AnchorStyles.Bottom Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
		Me.LinkLabelClearEvts.Location = New System.Drawing.Point(313, 120)
		Me.LinkLabelClearEvts.Name = "LinkLabelClearEvts"
		Me.LinkLabelClearEvts.Size = New System.Drawing.Size(64, 16)
		Me.LinkLabelClearEvts.TabIndex = 1
		Me.LinkLabelClearEvts.TabStop = True
		Me.LinkLabelClearEvts.Text = "Clear List"
		Me.LinkLabelClearEvts.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		Me.LinkLabelClearEvts.VisitedLinkColor = System.Drawing.Color.Blue
		'
		'lstEvts
		'
		Me.lstEvts.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
					Or System.Windows.Forms.AnchorStyles.Left) _
					Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
		Me.lstEvts.Location = New System.Drawing.Point(8, 8)
		Me.lstEvts.Name = "lstEvts"
		Me.lstEvts.Size = New System.Drawing.Size(368, 108)
		Me.lstEvts.TabIndex = 0
		'
		'Label1
		'
		Me.Label1.Font = New System.Drawing.Font("Tahoma", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label1.Location = New System.Drawing.Point(219, 92)
		Me.Label1.Name = "Label1"
		Me.Label1.Size = New System.Drawing.Size(120, 14)
		Me.Label1.TabIndex = 7
		Me.Label1.Text = "Keyboard Navigation:"
		'
		'Panel3
		'
		Me.Panel3.Controls.Add(Me.picTiltBackward)
		Me.Panel3.Controls.Add(Me.picSpinRight)
		Me.Panel3.Controls.Add(Me.picMoveBackward)
		Me.Panel3.Controls.Add(Me.picSpinLeft)
		Me.Panel3.Controls.Add(Me.picMoveDown)
		Me.Panel3.Controls.Add(Me.picZoomOut)
		Me.Panel3.Controls.Add(Me.picTiltForward)
		Me.Panel3.Controls.Add(Me.picMoveRight)
		Me.Panel3.Controls.Add(Me.picMoveForward)
		Me.Panel3.Controls.Add(Me.picMoveLeft)
		Me.Panel3.Controls.Add(Me.picMoveUp)
		Me.Panel3.Controls.Add(Me.picZoomIn)
		Me.Panel3.Location = New System.Drawing.Point(188, 13)
		Me.Panel3.Name = "Panel3"
		Me.Panel3.Size = New System.Drawing.Size(216, 84)
		Me.Panel3.TabIndex = 1
		'
		'picTiltBackward
		'
		Me.picTiltBackward.Anchor = System.Windows.Forms.AnchorStyles.None
		Me.picTiltBackward.Image = CType(resources.GetObject("picTiltBackward.Image"), System.Drawing.Image)
		Me.picTiltBackward.Location = New System.Drawing.Point(173, 44)
		Me.picTiltBackward.Name = "picTiltBackward"
		Me.picTiltBackward.Size = New System.Drawing.Size(28, 28)
		Me.picTiltBackward.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picTiltBackward.TabIndex = 30
		Me.picTiltBackward.TabStop = False
		'
		'picSpinRight
		'
		Me.picSpinRight.Anchor = System.Windows.Forms.AnchorStyles.None
		Me.picSpinRight.Image = CType(resources.GetObject("picSpinRight.Image"), System.Drawing.Image)
		Me.picSpinRight.Location = New System.Drawing.Point(141, 44)
		Me.picSpinRight.Name = "picSpinRight"
		Me.picSpinRight.Size = New System.Drawing.Size(28, 28)
		Me.picSpinRight.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picSpinRight.TabIndex = 29
		Me.picSpinRight.TabStop = False
		'
		'picMoveBackward
		'
		Me.picMoveBackward.Anchor = System.Windows.Forms.AnchorStyles.None
		Me.picMoveBackward.Image = CType(resources.GetObject("picMoveBackward.Image"), System.Drawing.Image)
		Me.picMoveBackward.Location = New System.Drawing.Point(110, 44)
		Me.picMoveBackward.Name = "picMoveBackward"
		Me.picMoveBackward.Size = New System.Drawing.Size(28, 28)
		Me.picMoveBackward.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picMoveBackward.TabIndex = 28
		Me.picMoveBackward.TabStop = False
		'
		'picSpinLeft
		'
		Me.picSpinLeft.Anchor = System.Windows.Forms.AnchorStyles.None
		Me.picSpinLeft.Image = CType(resources.GetObject("picSpinLeft.Image"), System.Drawing.Image)
		Me.picSpinLeft.Location = New System.Drawing.Point(79, 44)
		Me.picSpinLeft.Name = "picSpinLeft"
		Me.picSpinLeft.Size = New System.Drawing.Size(28, 28)
		Me.picSpinLeft.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picSpinLeft.TabIndex = 27
		Me.picSpinLeft.TabStop = False
		'
		'picMoveDown
		'
		Me.picMoveDown.Anchor = System.Windows.Forms.AnchorStyles.None
		Me.picMoveDown.Image = CType(resources.GetObject("picMoveDown.Image"), System.Drawing.Image)
		Me.picMoveDown.Location = New System.Drawing.Point(48, 44)
		Me.picMoveDown.Name = "picMoveDown"
		Me.picMoveDown.Size = New System.Drawing.Size(28, 28)
		Me.picMoveDown.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picMoveDown.TabIndex = 26
		Me.picMoveDown.TabStop = False
		'
		'picZoomOut
		'
		Me.picZoomOut.Anchor = System.Windows.Forms.AnchorStyles.None
		Me.picZoomOut.Image = CType(resources.GetObject("picZoomOut.Image"), System.Drawing.Image)
		Me.picZoomOut.Location = New System.Drawing.Point(16, 44)
		Me.picZoomOut.Name = "picZoomOut"
		Me.picZoomOut.Size = New System.Drawing.Size(28, 28)
		Me.picZoomOut.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picZoomOut.TabIndex = 25
		Me.picZoomOut.TabStop = False
		'
		'picTiltForward
		'
		Me.picTiltForward.Anchor = System.Windows.Forms.AnchorStyles.None
		Me.picTiltForward.Image = CType(resources.GetObject("picTiltForward.Image"), System.Drawing.Image)
		Me.picTiltForward.Location = New System.Drawing.Point(173, 12)
		Me.picTiltForward.Name = "picTiltForward"
		Me.picTiltForward.Size = New System.Drawing.Size(28, 28)
		Me.picTiltForward.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picTiltForward.TabIndex = 24
		Me.picTiltForward.TabStop = False
		'
		'picMoveRight
		'
		Me.picMoveRight.Anchor = System.Windows.Forms.AnchorStyles.None
		Me.picMoveRight.Image = CType(resources.GetObject("picMoveRight.Image"), System.Drawing.Image)
		Me.picMoveRight.Location = New System.Drawing.Point(141, 12)
		Me.picMoveRight.Name = "picMoveRight"
		Me.picMoveRight.Size = New System.Drawing.Size(28, 28)
		Me.picMoveRight.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picMoveRight.TabIndex = 23
		Me.picMoveRight.TabStop = False
		'
		'picMoveForward
		'
		Me.picMoveForward.Anchor = System.Windows.Forms.AnchorStyles.None
		Me.picMoveForward.Image = CType(resources.GetObject("picMoveForward.Image"), System.Drawing.Image)
		Me.picMoveForward.Location = New System.Drawing.Point(110, 12)
		Me.picMoveForward.Name = "picMoveForward"
		Me.picMoveForward.Size = New System.Drawing.Size(28, 28)
		Me.picMoveForward.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picMoveForward.TabIndex = 22
		Me.picMoveForward.TabStop = False
		'
		'picMoveLeft
		'
		Me.picMoveLeft.Anchor = System.Windows.Forms.AnchorStyles.None
		Me.picMoveLeft.Image = CType(resources.GetObject("picMoveLeft.Image"), System.Drawing.Image)
		Me.picMoveLeft.Location = New System.Drawing.Point(79, 12)
		Me.picMoveLeft.Name = "picMoveLeft"
		Me.picMoveLeft.Size = New System.Drawing.Size(28, 28)
		Me.picMoveLeft.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picMoveLeft.TabIndex = 21
		Me.picMoveLeft.TabStop = False
		'
		'picMoveUp
		'
		Me.picMoveUp.Anchor = System.Windows.Forms.AnchorStyles.None
		Me.picMoveUp.Image = CType(resources.GetObject("picMoveUp.Image"), System.Drawing.Image)
		Me.picMoveUp.Location = New System.Drawing.Point(48, 12)
		Me.picMoveUp.Name = "picMoveUp"
		Me.picMoveUp.Size = New System.Drawing.Size(28, 28)
		Me.picMoveUp.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picMoveUp.TabIndex = 20
		Me.picMoveUp.TabStop = False
		'
		'picZoomIn
		'
		Me.picZoomIn.Anchor = System.Windows.Forms.AnchorStyles.None
		Me.picZoomIn.Image = CType(resources.GetObject("picZoomIn.Image"), System.Drawing.Image)
		Me.picZoomIn.Location = New System.Drawing.Point(16, 12)
		Me.picZoomIn.Name = "picZoomIn"
		Me.picZoomIn.Size = New System.Drawing.Size(28, 28)
		Me.picZoomIn.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picZoomIn.TabIndex = 19
		Me.picZoomIn.TabStop = False
		'
		'picLookPositiveZ
		'
		Me.picLookPositiveZ.Image = CType(resources.GetObject("picLookPositiveZ.Image"), System.Drawing.Image)
		Me.picLookPositiveZ.Location = New System.Drawing.Point(83, 137)
		Me.picLookPositiveZ.Name = "picLookPositiveZ"
		Me.picLookPositiveZ.Size = New System.Drawing.Size(28, 28)
		Me.picLookPositiveZ.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picLookPositiveZ.TabIndex = 6
		Me.picLookPositiveZ.TabStop = False
		'
		'picLookNegativeX
		'
		Me.picLookNegativeX.Image = CType(resources.GetObject("picLookNegativeX.Image"), System.Drawing.Image)
		Me.picLookNegativeX.Location = New System.Drawing.Point(156, 70)
		Me.picLookNegativeX.Name = "picLookNegativeX"
		Me.picLookNegativeX.Size = New System.Drawing.Size(28, 28)
		Me.picLookNegativeX.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picLookNegativeX.TabIndex = 5
		Me.picLookNegativeX.TabStop = False
		'
		'picLookNegativeZ
		'
		Me.picLookNegativeZ.Image = CType(resources.GetObject("picLookNegativeZ.Image"), System.Drawing.Image)
		Me.picLookNegativeZ.Location = New System.Drawing.Point(83, 5)
		Me.picLookNegativeZ.Name = "picLookNegativeZ"
		Me.picLookNegativeZ.Size = New System.Drawing.Size(28, 28)
		Me.picLookNegativeZ.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picLookNegativeZ.TabIndex = 4
		Me.picLookNegativeZ.TabStop = False
		'
		'picLookPositiveX
		'
		Me.picLookPositiveX.Image = CType(resources.GetObject("picLookPositiveX.Image"), System.Drawing.Image)
		Me.picLookPositiveX.Location = New System.Drawing.Point(8, 70)
		Me.picLookPositiveX.Name = "picLookPositiveX"
		Me.picLookPositiveX.Size = New System.Drawing.Size(28, 28)
		Me.picLookPositiveX.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage
		Me.picLookPositiveX.TabIndex = 3
		Me.picLookPositiveX.TabStop = False
		'
		'TextBox1
		'
		Me.TextBox1.Anchor = CType((System.Windows.Forms.AnchorStyles.Bottom Or System.Windows.Forms.AnchorStyles.Left), System.Windows.Forms.AnchorStyles)
		Me.TextBox1.BackColor = System.Drawing.SystemColors.Control
		Me.TextBox1.BorderStyle = System.Windows.Forms.BorderStyle.None
		Me.TextBox1.Enabled = False
		Me.TextBox1.Font = New System.Drawing.Font("Tahoma", 6.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.TextBox1.Location = New System.Drawing.Point(189, 107)
		Me.TextBox1.Multiline = True
		Me.TextBox1.Name = "TextBox1"
		Me.TextBox1.Size = New System.Drawing.Size(211, 56)
		Me.TextBox1.TabIndex = 2
		Me.TextBox1.Text = "Forward=Home,  Backward=End,  In=<+>,  Out=<->,  TiltUp=PageUp,  TiltDown=PageDn," & _
		"  North=N,  South=S,  East=E,  West=W,  SpinLeft=<, SpinRight=>, Accelerate=<Spa" & _
		"ce>"
		'
		'Form1
		'
		Me.AutoScaleBaseSize = New System.Drawing.Size(5, 13)
		Me.ClientSize = New System.Drawing.Size(804, 506)
		Me.Controls.Add(Me.Panel1)
		Me.Controls.Add(Me.Panel2)
		Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
		Me.Name = "Form1"
		Me.Text = "Parco 3D Viewer"
		Me.Panel1.ResumeLayout(False)
		Me.Panel2.ResumeLayout(False)
		Me.TabControl1.ResumeLayout(False)
		Me.TabPageDataSource.ResumeLayout(False)
		Me.GroupBox2.ResumeLayout(False)
		Me.GroupBox1.ResumeLayout(False)
		Me.TabPageTags.ResumeLayout(False)
		Me.TabPageTagTrig.ResumeLayout(False)
		Me.TabPageTrigs.ResumeLayout(False)
		Me.TabPageTEvents.ResumeLayout(False)
		Me.Panel3.ResumeLayout(False)
		Me.ResumeLayout(False)

	End Sub

#End Region

    Private mappConfig As Configuration.AppSettingsReader
    Private bUseParcoData As Boolean = False

	Private WithEvents mStream As Parco.DataStream	'streaming data provider
	Private mData As Parco.Data	' the access to the RTLS database via the web service

	Private mbSceneInit As Boolean = False	'used for debug testing of Directx versions....

    Private msProviderIP As String
    Private msParcoWebSvc As String
    Private msLocalWebSvc As String

    Private mPort As Integer = 0

	Private mTagEventKey As MyMenuClickedArgs

    Private mViewerTrig As Hashtable 'used for temp holding of the rendering object if triggers are being displayed.
    Private mbFormIsLoading As Boolean = True

	Private mTriggers As New Parco.Triggers	' Custom collection of trigger areas 
	Private mTagTriggers As New Parco.Triggers	'Custom collection of triggers that are assigned to a device

	Private Delegate Sub ProcessChild(ByVal sVal As String)   'Delegate for jumping back into the main thread from a viewer clicked event
	Private Sub ProcessChildInMain(ByVal sVal As String)
		Try
			System.Diagnostics.Process.Start(sVal)
		Catch ex As Exception
			MessageBox.Show(ex.Message, "Process Start Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try

	End Sub

#Region "Tag/Trigger Serialization"
	Private Sub LoadTags()
		Dim sFile As String = Application.ExecutablePath & ".tags"

		Dim f As System.IO.File
		mViewerTrig = New Hashtable
		If f.Exists(sFile) = True Then
			If Not mViewer Is Nothing Then
				Dim fs As New FileStream(sFile, FileMode.Open)
				Dim fmtr As New Binary.BinaryFormatter
				Dim obj As Object
				obj = fmtr.Deserialize(fs)
				Dim h As Hashtable
				h = CType(obj, Hashtable)
				Dim tp As TagPlus
				Dim ts As TagSerial
				Dim key As Object
				Dim keyChild As Object
				For Each key In h.Keys
					ts = DirectCast(h.Item(key), TagSerial)
					tp = CreateFigure(ts.Image, ts.Width, ts.Height, ts.ID, ts.Name)
					'now position the tag at our real origin (the viewers is in the middle of the world)
					Dim p As Point3D = ToViewerCoord(0, 0, 0)
					tp.X = p.X
					tp.Y = p.Y
					tp.Z = p.Z
					For Each keyChild In ts.Children.Keys
						Dim tc As ChildSerial
						tc = DirectCast(ts.Children.Item(keyChild), ChildSerial)
						Dim child As New SIO3DViewer.TagChild(tc.Image.ToString, tc.Size, tc.Size)
						child.Data = tc.Data
						tp.Children.Add(child.ImageKey, child)
					Next
					mViewer.Tags.Add(tp.ID, tp)
				Next
				fs.Flush()
				fs.Close()
				LoadTagList()
			End If
		End If

	End Sub

	Private Sub LoadTagList()
		lstTags.Items.Clear()
		If Not mViewer Is Nothing Then
			If Not mViewer.Tags Is Nothing Then
				Dim t As SIO3DViewer.Tag
				Dim tp As TagPlus
				For Each t In mViewer.Tags
					tp = DirectCast(t, TagPlus)
					lstTags.Items.Add(tp)
				Next
			End If
		End If
	End Sub
	Private Sub SaveTags()
		Dim sFile As String = Application.ExecutablePath & ".tags"
		Dim h As Hashtable
		Dim t As SIO3DViewer.Tag
		Dim child As SIO3DViewer.TagChild
		Dim tp As TagPlus
		Dim ts As TagSerial
		If Not mViewer Is Nothing Then
			If mViewer.Tags.Count > 0 Then
				h = New Hashtable
				Dim fw, fh As Single
				For Each t In mViewer.Tags
					tp = DirectCast(t, TagPlus)
					ts = New TagSerial
					With ts
						.Image = tp.ImageEnum
						.Height = tp.ImageHeight
						.Width = tp.ImageWidth
						.ID = tp.ID
						.Name = tp.Name

					End With
					Dim tc As TagChild
					For Each tc In tp.Children

						Dim cs As New ChildSerial
						Select Case tc.Key.ToString
							Case TagImages.Thermometer.ToString
								cs.Image = TagImages.Thermometer
							Case TagImages.Heartbeat.ToString
								cs.Image = TagImages.Heartbeat
							Case TagImages.Xray.ToString
								cs.Image = TagImages.Xray
							Case TagImages.Globe.ToString
								cs.Image = TagImages.Globe
						End Select
						If Not tc.Data Is Nothing Then
							cs.Data = tc.Data.ToString
						End If
						cs.Size = GetChildSize(tc)
						ts.Children.Add(cs.Image, cs)
					Next
					h.Add(ts.ID, ts)
				Next
			End If
		End If
		If Not h Is Nothing Then
			Dim fs As New FileStream(sFile, FileMode.OpenOrCreate)
			Dim bf As New Binary.BinaryFormatter
			bf.Serialize(fs, h)
		End If
	End Sub

	Private Sub LoadTrigs()
		Dim sFile As String = Application.ExecutablePath & ".triggers"

		Dim f As System.IO.File
		'This code will need to be changed if the chkViewTriggers default is changed.
		If f.Exists(sFile) = True Then
			If Not mViewer Is Nothing Then
				Dim fs As New FileStream(sFile, FileMode.Open)
				Dim fmtr As New Binary.BinaryFormatter
				Dim obj As Object
				obj = fmtr.Deserialize(fs)
				Dim h As New Hashtable
				h = CType(obj, Hashtable)
				Dim ts As TrigSerial
				Dim t As Trigger
				Dim key As Object
				For Each key In h.Keys
					ts = CType(h.Item(key), TrigSerial)
					t = AreaTriggerCreate(ts.XMin, ts.YMin, ts.XMax, ts.YMax, ts.ZBottom, ts.ZTop, ts.Name, ts.Direction)
					mTriggers.AddItem(t, t.Name)
					AddHandler t.TriggerEvent, AddressOf TriggerEvent
					'now show the trigger in the viewer
					Dim pt As Point3D = ToViewerCoord(ts.XMin, ts.YMin, ts.ZBottom)
					Dim cp As SIO3DViewer.ColoredPlane = CreateViewerAreaTrig(t.Name, pt.X, pt.Y, pt.Z, ts.XMax - ts.XMin, ts.YMax - ts.YMin, ts.Color)
					If chkShowAreaTrigs.Checked Then
						mViewer.Objects.Add(t.Name, cp)
					Else
						mViewerTrig.Add(t.Name, cp)
					End If
				Next
				fs.Flush()
				fs.Close()
				LoadTrigList()
			End If
		End If

	End Sub

	Private Sub LoadTrigList()
		lstTriggers.Items.Clear()
		Dim t As Trigger
		For Each t In mTriggers
			lstTriggers.Items.Add(t.Name)
		Next

	End Sub
	Private Sub SaveTrigs()
		Dim sFile As String = Application.ExecutablePath & ".triggers"
		Dim fs As New FileStream(sFile, FileMode.OpenOrCreate)
		Dim bf As New Binary.BinaryFormatter
		'microsoft.visualbasic.collection is not serializable - drat!
		Dim ht As New Hashtable
		Dim t As Trigger
		Dim ts As TrigSerial
		Dim clr As System.Drawing.Color = System.Drawing.Color.Red

		For Each t In mTriggers
			With t.Regions.Item(1)
				'try to find our trigger in the 3viewer objects collection
				Dim cp As SIO3DViewer.ColoredPlane
				If chkShowAreaTrigs.Checked Then
					Dim o3d As SIO3DViewer.Obj3D = mViewer.Objects.Item(t.Name)
					If Not o3d Is Nothing Then
						cp = DirectCast(o3d, SIO3DViewer.ColoredPlane)
						'I am storing the color in the data property
						clr = CType(cp.Data, System.Drawing.Color)
					End If
					ts = New TrigSerial(t.Name, t.ID.ToString, .XMax, .Xmin, .YMax, .Ymin, .ZTop, .ZBottom, t.Direction, clr)
				Else
					'the things to save should be in the hash
					If Not mViewerTrig Is Nothing Then
						cp = DirectCast(mViewerTrig.Item(t.Name), SIO3DViewer.ColoredPlane)
						clr = CType(cp.Data, System.Drawing.Color)
					End If
					ts = New TrigSerial(t.Name, t.ID.ToString, .XMax, .Xmin, .YMax, .Ymin, .ZTop, .ZBottom, t.Direction, clr)
				End If


			End With
			ht.Add(ts.Name, ts)
		Next
		bf.Serialize(fs, ht)

	End Sub

	Private Sub ClearNonConfigTags()
		'Need to remove all viewer tags that at not in lstTags

		Dim t As SIO3DViewer.Tag
		Dim tp As TagPlus
		Dim hRemove As New Hashtable
		For Each t In mViewer.Tags
			tp = DirectCast(t, TagPlus)
			If lstTags.Items.Contains(tp) = False Then
				hRemove.Add(tp.ID, tp.ID)
			End If
		Next
		Dim key As Object
		For Each key In hRemove.Keys
			mViewer.Tags.Remove(key)
		Next
	End Sub
#End Region

#Region "Form Load and Closing events"

	Private Sub Form1_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
		Try
			Me.Cursor = Cursors.WaitCursor

			Me.ContextMenu1.MenuItems.Add("Add/Edit Trigger", AddressOf MenuTrig_Click)
			Me.ContextMenu1.MenuItems.Add("Delete Trigger", AddressOf MenuTrigDel_Click)
			Me.ContextMenu1.MenuItems.Add("Show Info", AddressOf MenuInfo_Click)

			mappConfig = New Configuration.AppSettingsReader

			'set our button defaults - data tab
			btnDisConnect.Enabled = False
			btnConnect.Enabled = False
			'tag tab
			btnTagTrigDel.Enabled = False
			btnTagTrigEdit.Enabled = False
			btnTagEdit.Enabled = False
			btnTagRem.Enabled = False
			'trigger tab
			btnTrigDel.Enabled = False
			btnTrigEdit.Enabled = False
			chkShowAreaTrigs.Checked = False		 ' set to false to make it DirectX 9.0.c safe
			'tag trigger tab
			btnTagTrigEdit2.Enabled = False
			btnTagTrigDel2.Enabled = False

			bUseParcoData = CType(mappConfig.GetValue("UseParcoData", GetType(Boolean)), Boolean)
			If bUseParcoData Then
				rbParco.Checked = True
			Else
				rbLocalServer.Checked = True
			End If
			msParcoWebSvc = mappConfig.GetValue("ParcoWebServiceURL", GetType(String)).ToString
			msLocalWebSvc = mappConfig.GetValue("LocalWebServiceURL", GetType(String)).ToString

			rbFullStream.Checked = True
			'set up lstTag to bind our TagPlus instances to
			lstTags.DisplayMember = "Name"

			Me.KeyPreview = True
			Me.InitializeScene()
			mViewer.StartRender()

			gTagHieghtDefault = CType(mappConfig.GetValue("DefaultTagHeight", GetType(Single)), Single)
			gTagWidthDefault = CType(mappConfig.GetValue("DefaultTagWidth", GetType(Single)), Single)
			'load the tags after initializescene as this is where the floor and offsets get set
			LoadTags()
			LoadTrigs()

			mbFormIsLoading = False

		Catch ex As Exception
			bUseParcoData = False
			MessageBox.Show(ex.ToString, "Form Load Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
		Finally
			Me.Cursor = Cursors.Default
		End Try
	End Sub
	Private Sub Form1_Activated(ByVal sender As Object, ByVal e As System.EventArgs) Handles MyBase.Activated
		Try
			'this is here for debugging DirectX compatibility errors.
			'Errors were not always begin displayed in the form load event.
			'dont reinit if we have already done so, this event fires each time the form receives focus.
			If mbSceneInit = False Then
				'Me.Cursor = Cursors.WaitCursor
				'Me.InitializeScene()
				'mViewer.StartRender()
				'mbSceneInit = True
			End If
		Catch ex As Exception
			MessageBox.Show(ex.ToString & ControlChars.CrLf & ControlChars.CrLf & "This is a severe error.", "Form Activated Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
			mbSceneInit = True
		Finally
			Me.Cursor = Cursors.Default
		End Try
	End Sub

	Private Sub Form1_Closing(ByVal sender As Object, ByVal e As System.ComponentModel.CancelEventArgs) Handles MyBase.Closing
		Try
			mViewer.StopRender()
			CloseStream()
			SaveTags()
			SaveTrigs()

		Catch ex As Exception
			MessageBox.Show(ex.ToString, "Form Close Error")
		End Try
	End Sub

#End Region

#Region "Viewer Events and Code"

	Private Sub InitializeScene()
		Dim floorWidth As Single = 200
		Dim floorDepth As Single = 200
		Dim sFloorImage As String = "grid_box.bmp"
		'Dim numTags As Integer = 2

		Dim bUseDefaultMap As Boolean = CType(mappConfig.GetValue("UseDefaultMap", GetType(Boolean)), Boolean)
		If bUseDefaultMap = False Then
			sFloorImage = mappConfig.GetValue("MapImage", GetType(String)).ToString
			floorWidth = CType(mappConfig.GetValue("MapX", GetType(Single)), Single)
			floorDepth = CType(mappConfig.GetValue("MapY", GetType(Single)), Single)
			'scale and move our minimap (aka picWorld)
			'keep hieght the same and scale the width to match the Hieght to Width ratio
			With picWorld
				Dim centerX As Integer = CType(.Left + (.Width / 2), Integer)
				'Dim centerY As Integer = CType(.Top + (.Height / 2), Integer)

				.Width = CType((.Height / floorDepth) * floorWidth, Integer)
				'.Height = CType(floorDepth, Integer)
				.Left = centerX - CType(.Width / 2, Integer)
				'.Top = centerY - CType(.Height / 2, Integer)

			End With

		End If
		' add all of the images that we will be using
		'If you add an image, add it to the TagImages enumerated values.
		mViewer.Images.Add("Patient", "figure1.dds")
		mViewer.Images.Add("floor unselected", "ring_yellow.dds")
		mViewer.Images.Add("floor selected", "circle_yellow.dds")
		mViewer.Images.Add("floorgrid", sFloorImage)
		mViewer.Images.Add("Globe", "mipac.bmp")
		mViewer.Images.Add("selectionTexture", "pix.dds")
		mViewer.Images.Add("Doctor", "doctor.dds")
		mViewer.Images.Add("Nurse", "nurse.dds")
		mViewer.Images.Add("Xray", "xray.bmp")
		mViewer.Images.Add("IV", "iv.dds")
		mViewer.Images.Add("Redcross", "redcross.bmp")
		mViewer.Images.Add("Microscope", "microscope.dds")
		mViewer.Images.Add("Wheelchair", "wheelchair.dds")
		mViewer.Images.Add("Monitor", "monitor.dds")
		mViewer.Images.Add("Heartbeat", "heartbeat.bmp")
		mViewer.Images.Add("Thermometer", "thermometer.bmp")

		mViewer.SetSkyBoxMeshFile("SkyBox2.x")
		'mViewer.SetFloor("floorgrid", floorWidth, floorDepth, 0, -0.1, 0)
		mViewer.SetFloor("floorgrid", floorWidth, floorDepth, -floorWidth / 2, -0.1, -floorDepth / 2)

		'the minimap and viewer assume 0,0 is the middle of the floor, so calculate our offsets to make
		'the lower left corner appear to be 0,0. The offsets need to be applied to the device positions in the
		'RTLS Stream Events - this is a known bug in the viewer minimap that will be fixed in the future.

		gXOffset = -floorWidth / 2
		gYOffset = -floorDepth / 2

		mViewer.SetDrawingFont("Arial", FontStyle.Bold)
		mViewer.SelectionLineColor = Color.DarkRed
		mViewer.SelectionWallBottom = 0
		mViewer.SelectionWallTop = 1.5
		mViewer.SelectionWallImageKey = "selectionTexture"
		mViewer.SelectionRoofImageKey = ""
		mViewer.ShowStatistics = False
		mViewer.AutoSelectOnClick = True
		mViewer.AllowAreaSelection = True
		'
		' setup our limits...
		mViewer.Camera.LookAtRangeX = New Range(-floorWidth / 2, floorWidth / 2)
		mViewer.Camera.LookAtRangeZ = New Range(-floorDepth / 2, floorDepth / 2)
		mViewer.Camera.LookAtRangeY = New Range(10, 100)		  'was 20
		mViewer.Camera.DistanceToLookAtRange = New Range(10, 500)
		mViewer.Camera.AscentionAngleRange = New Range(Math.PI * 2.5 / 180, Math.PI * 89 / 180)
		'
		' Set the initial camera position
		mViewer.Camera.Position = New Vector3(0, 10, -10)
		mViewer.Camera.LookAt = New Vector3(0, 0, 10)

		'Code to show simulated tags if no data is available
		'If Not bUseParcoData Then
		'    '
		'    ' add our tags...
		'    Dim rand As New System.Random
		'    ' Initialize the Tag data
		'    Dim i As Integer

		'    For i = 0 To numTags - 1
		'        ' Position the Tags randomly
		'        Dim fig As SIO3DViewer.Tag = CreateFigure()
		'        Dim fTheta As Single = 2.0F * CSng(Math.PI) * CSng(rand.NextDouble())
		'        Dim fRadius As Single = 25.0F + 55.0F * CSng(rand.NextDouble())
		'        fig.X = fRadius * CSng(Math.Sin(fTheta))
		'        fig.Z = fRadius * CSng(Math.Cos(fTheta))

		'        Dim childWidth As Single
		'        Dim childHeight As Single
		'        fig.GetChildDimensions(childWidth, childHeight)
		'        Dim nChildren As Integer = rand.Next(0, 6)
		'        While nChildren > 0
		'            nChildren -= 1
		'            Dim tc As New TagChild("tagchild", childWidth, childHeight)
		'            fig.Children.Add(nChildren, tc)
		'        End While

		'        mViewer.Tags.Add(i, fig)
		'    Next i
		'End If
	End Sub

	Private Sub mViewer_BeforeRender(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles mViewer.BeforeRender
		'
		' update the camera position
		mViewer.Camera.MoveCameraCloser(mMoveDeltaLOS * mViewer.Accelerator * mViewer.LinearUnit)
		mViewer.Camera.MoveRight(mMoveDeltaX * mViewer.Accelerator * mViewer.LinearUnit)
		mViewer.Camera.MoveUp(mMoveDeltaY * mViewer.Accelerator * mViewer.LinearUnit)
		mViewer.Camera.MoveForward(mMoveDeltaZ * mViewer.Accelerator * mViewer.LinearUnit)
		mViewer.Camera.RotateCameraDownAboutLookAt(mTiltDelta * mViewer.Accelerator * mViewer.AngularUnit)
		mViewer.Camera.RotateCameraLeftAboutLookat(mSpinDelta * mViewer.Accelerator * mViewer.AngularUnit)


	End Sub


	'Private Sub mViewer_BeginSelection(ByVal sender As Object, ByVal e As SIO3DViewer.SelectionEventArgs) Handles mViewer.BeginSelection
	'	mSelectedList.Clear()
	'End Sub

	'Private Sub mViewer_ContinueSelection(ByVal sender As Object, ByVal e As SIO3DViewer.SelectionEventArgs) Handles mViewer.ContinueSelection
	'	Dim key As Object
	'	For Each key In mSelectedList.Keys
	'		Dim t As TagPlus = CType(mViewer.Tags.Item(key), TagPlus)
	'		t.UserColor = CType(mSelectedList(key), Color)
	'	Next
	'	mSelectedList.Clear()
	'	For Each key In e.TagKeys
	'		Dim t As TagPlus = CType(mViewer.Tags.Item(key), TagPlus)
	'		mSelectedList.Add(key, t.UserColor)
	'	Next
	'End Sub

	Private Sub mViewer_EndSelection(ByVal sender As Object, ByVal e As SIO3DViewer.SelectionEventArgs) Handles mViewer.EndSelection
		Try
			Dim key As Object
			'see if the  user has the right mouse button down, if so ask them if want a trigger
			If e.Button = MouseButtons.Right Then
				Microsoft.VisualBasic.Beep()
				Dim r As DialogResult = MessageBox.Show("Do you wish to create a trigger using the selected area?", "Create Trigger?", MessageBoxButtons.YesNo, MessageBoxIcon.Question)
				If r = DialogResult.Yes Then
					Dim f As New frmTrigger
					'use a default z-coords (real - not viewer)
					'frmTrigger uses real coordinates, not viewer coordinates, so convert them here
					f.txtName.Text = "Name Me"
					f.txtZTop.Text = "10.0"
					f.txtZBottom.Text = "-1.0"
					Dim fYmin As Single = 0
					Dim fYmax As Single = 0
					Dim fXmin As Single = 0
					Dim fXmax As Single = 0
					Dim i As Integer
					Dim v3 As Vector3

					For i = 0 To e.Area.Points.Length - 1
						v3 = e.Area.Points(i)
						Dim p As Point3D = ToRealCoord(v3.X, v3.Y, v3.Z)
						'find the min/max values in real coordinates
						If i = 0 Then
							fXmin = p.X
							fXmax = p.X
							fYmin = p.Y
							fYmax = p.Y
						Else
							If p.X >= fXmax Then
								fXmax = p.X
							ElseIf p.X < fXmin Then
								fXmin = p.X
							End If
							If p.Y >= fYmax Then
								fYmax = p.Y
							Else
								fYmin = p.Y
							End If
						End If
					Next
					f.txtXMax.Text = Microsoft.VisualBasic.Format(fXmax, "#0.0")
					f.txtXmin.Text = Microsoft.VisualBasic.Format(fXmin, "#0.0")
					f.txtYMax.Text = Microsoft.VisualBasic.Format(fYmax, "#0.0")
					f.txtYmin.Text = Microsoft.VisualBasic.Format(fYmin, "#0.0")
					f.ShowDialog()
					If f.IsValid Then
						'see if we have one by the same name
						If Not mTriggers.Item(f.txtName.Text) Is Nothing Then
							MessageBox.Show("A trigger with that name already exists.", "Invalid Trigger", MessageBoxButtons.OK, MessageBoxIcon.Information)
						Else
							Dim t As Trigger = f.Trig
							mTriggers.AddItem(t, t.Name)
							AddHandler t.TriggerEvent, AddressOf TriggerEvent
							lstTriggers.Items.Add(t.Name)

							'create a colored plane representing the trigger
							Dim cp As SIO3DViewer.ColoredPlane
							Dim pt As Point3D = ToViewerCoord(t.Regions.Item(1).Xmin, t.Regions.Item(1).Ymin, 0.1)
							'our pt is in viewer coords, the trigger Y is what we want to use for Z
							cp = CreateViewerAreaTrig(t.Name, pt.X, pt.Y, pt.Z, t.Regions.Item(1).XMax - t.Regions.Item(1).Xmin, t.Regions.Item(1).YMax - t.Regions.Item(1).Ymin, Color.FromName(f.cboTrigColor.SelectedItem.ToString))
							If chkShowAreaTrigs.Checked Then
								mViewer.Objects.Add(t.Name, cp)
							Else
								mViewerTrig.Add(t.Name, cp)
							End If
						End If				   'mTriggers.Item(f.txtName.Text)

					End If					 'f.IsValid
					e.SetSelection = False
				End If			 'r = DialogResult.Yes
			Else
				'the user is selecting something
				e.SetSelection = True
			End If

		Catch ex As Exception
			MessageBox.Show(ex.Message, "End Selection Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub

	Private Sub mViewer_TagSelectedChanged(ByVal sender As Object, ByVal e As SIO3DViewer.TagEventArgs) Handles mViewer.TagSelectedChanged
		Dim t As SIO3DViewer.Tag = mViewer.Tags.Item(e.TagKey)
		If t.Selected Then
			t.FloorImageKey = "floor selected"
			'change selected items to red in the mini-map
			t.UserColor = Color.Red
		Else
			t.FloorImageKey = "floor unselected"
			t.UserColor = Color.Navy
		End If
	End Sub
	Private Sub mViewer_TagDoubleClicked(ByVal sender As Object, ByVal e As SIO3DViewer.TagClickEventArgs) Handles mViewer.TagDoubleClicked
		Try
			Dim t As TagPlus = DirectCast(mViewer.Tags.Item(e.TagKey), TagPlus)
			ShowInfoForm(t)
		Catch ex As Exception
			MessageBox.Show(ex.Message, "Tag Info Failed", MessageBoxButtons.OK, MessageBoxIcon.Information)

		End Try

	End Sub

	Private Sub mViewer_TagChildDoubleClicked(ByVal sender As Object, ByVal e As SIO3DViewer.TagChildClickEventArgs) Handles mViewer.TagChildDoubleClicked
		Try
			Dim t As TagPlus = DirectCast(mViewer.Tags.Item(e.TagKey), TagPlus)
			Dim tc As TagChild = t.Children.Item(e.ChildKey)
			If tc.ImageKey.ToString = TagImages.Globe.ToString AndAlso Not tc.Data Is Nothing Then
				'see if we have url or file data to try
				e.Handled = True
				Dim d As ProcessChild
				d = AddressOf ProcessChildInMain
				d.Invoke(tc.Data.ToString)
			Else
				Dim fInfo As New frmTagInfo
				fInfo.TagPlus = t
				fInfo.TagChild = tc
				fInfo.Show()
				e.Handled = True
			End If

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Tag Info Failed", MessageBoxButtons.OK, MessageBoxIcon.Information)

		End Try

	End Sub

	Private Sub ShowInfoForm(ByVal t As TagPlus)
		Dim fInfo As New frmTagInfo
		fInfo.TagPlus = t
		fInfo.StartPosition = FormStartPosition.CenterScreen
		fInfo.Show()
	End Sub
	Private Sub mViewer_ViewerMouseDown(ByVal sender As Object, ByVal e As SIO3DViewer.ViewerMouseEventArgs) Handles mViewer.ViewerMouseDown
		Try
			If e.Button = MouseButtons.Right Then
				Dim t As SIO3DViewer.Tag = mViewer.Tags.Item(e.TagKey)
				If Not t Is Nothing Then
					'the user right clicked on a Tag
					Dim p As New System.Drawing.Point(e.X, e.Y)
					mTagEventKey = New MyMenuClickedArgs
					mTagEventKey.TagKey = e.TagKey
					ContextMenu1.Show(Me.mViewer, p)

				End If
			End If
		Catch ex As Exception
			MessageBox.Show(ex.Message, "Tag Click Error", MessageBoxButtons.OK, MessageBoxIcon.Information)
		End Try
	End Sub

#End Region

#Region "RTLS Data and Connection events"

	Private Sub mStream_Connection(ByVal sender As Object, ByVal State As Parco.DataStream.ConnectionState) Handles mStream.Connection
		Try
			If State = DataStream.ConnectionState.Connected Then
				btnConnect.Enabled = False
				btnDisConnect.Enabled = True
				lblConState.Text = "Connected"
				lblConState.ForeColor = System.Drawing.Color.Green
			ElseIf State = DataStream.ConnectionState.Disconnected Then

				btnConnect.Enabled = True
				btnDisConnect.Enabled = False
				'now kill all of our dear little tags (that are not configured)
				ClearNonConfigTags()


				lblConState.Text = "Disconnected"
				lblConState.ForeColor = System.Drawing.Color.Red
			End If
		Catch ex As Exception
			MessageBox.Show(ex.ToString, "Stream Connection Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
		End Try
	End Sub


	Private Sub mStream_Response(ByVal sender As Object, ByVal oResponse As Parco.ParcoMsg.Response) Handles mStream.Response
		Try
			If oResponse.Message <> String.Empty Then
				'the resource had a problem with the request, we may have a fullstream/subscription mismatch
				MessageBox.Show("Request " & oResponse.ReqID & " denied:" & oResponse.Message, "Stream Response Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
			Else
				If oResponse.ResponseType = ParcoMsg.ResponseType.BeginStream Then
					'txtMsg.Text = "Receiving all available data..."
				ElseIf oResponse.ResponseType = ParcoMsg.ResponseType.EndStream Then
					'txtMsg.Text = "Data stream ended."
				End If
			End If
		Catch ex As Exception
			MessageBox.Show(ex.ToString, "Stream Response Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
		End Try
	End Sub

	Private Sub mStream_Stream(ByVal sender As Object, ByVal oDevice As Parco.Device) Handles mStream.Stream
		Try
			'show that we received data. Each call causes the control to blink on and them off. If the blink
			'method is called repeatedly before the cycle completes, the control will simply blink on and off at
			'the prorgramed rate (in milliseconds). Small ,lightweight, and thread safe.
			BlinkData.Blink()

			Dim t As TagPlus = CType(mViewer.Tags.Item(oDevice.ID), TagPlus)
			If t Is Nothing AndAlso rbFullStream.Checked Then
				'if we are running in subscription mode, ignore all data
				'that is not in our tags collection
				t = CreateFigure(TagImages.Patient, gTagWidthDefault, gTagHieghtDefault, oDevice.ID)
				t.Name = "Unknown"
				t.ID = oDevice.ID
				'Dim tc As New SIO3DViewer.TagChild("tagchild",  0.5, 0.5)
				't.Children.Add(0, tc)
				't.Children.Visible = True
				mViewer.Tags.Add(oDevice.ID, t)

			End If
			'Here is where we make the transition from the parco RTLS system coordinate system to the 3D programming coordinate system.
			'In the 3D programming world X is the same, Y is up and Z is into the monitor.
			'We also need to add the X and Y offsets to compensate for the viewer's 0,0 ref being the middle of the floor.
			'Helper functions in Module1 perform the translation
			If Not t Is Nothing Then

				'Do we need to translate any Tag triggers?
				If mTagTriggers.Count > 0 Then
					Dim dt As Trigger
					dt = mTagTriggers.Item(oDevice.ID)
					If Not dt Is Nothing Then
						'our tag triggers have only 1 region and are centered in the bounding box
						'We can use this to calulate the current centroid used for determining
						'the distance to translate the trigger
						'the regions are 1 based...
						With dt.Regions.Item(1)
							'for this app, we are not moving trigger in vertical direction!
							'Calculate the centroid of our region and use to translate
							dt.Translate(oDevice.X - ((.XMax + .Xmin) / 2), oDevice.Y - ((.YMax + .Ymin) / 2), 0)
						End With
					End If
				End If

				'Update the position of the tag
				Dim p As Point3D = ToViewerCoord(oDevice.X, oDevice.Y, oDevice.Z)
				t.X = p.X
				t.Y = p.Y
				t.Z = p.Z

				Dim trg As Trigger
				If mTagTriggers.Count > 0 Then
					'I am using the trigger.id property to correlate the Device Trigger to a Device.
					For Each trg In mTagTriggers
						'do not check a tag against it's own trigger....
						If oDevice.ID <> trg.ID.ToString Then
							trg.CheckTrigger(oDevice)
						End If
					Next
				End If

				'Check the device against all of our stationary triggers.
				If mTriggers.Count > 0 Then
					For Each trg In mTriggers
						trg.CheckTrigger(oDevice)
					Next
				End If

			End If
		Catch ex As Exception
			MessageBox.Show(ex.ToString, "Stream Event Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
		End Try
	End Sub

	Private Sub CloseStream()
		'check for streaming data and cleanup if we are receiving it.
		If Not mStream Is Nothing Then
			If mStream.IsConnected Then
				'send an end stream request to the resouce
				Dim req As New Parco.ParcoMsg.Request(ParcoMsg.RequestType.EndStream, "x3x3")
				mStream.SendRequest(req)
				'The end stream request will cause the manager to send the end stream request and then close the connection
				'so dont do it here....
			End If
		End If
	End Sub
#End Region

#Region "Navigation"

	Private Const keySlideLeft As Keys = Keys.Left
	Private Const keySlideRight As Keys = Keys.Right
	Private Const keySlideForward As Keys = Keys.Home
	Private Const keySlideBackward As Keys = Keys.End
	Private Const keySlideUp As Keys = Keys.Up
	Private Const keySlideDown As Keys = Keys.Down
	Private Const keySlideIn As Keys = Keys.Add
	Private Const keySlideOut As Keys = Keys.Subtract
	Private Const keyRotateUp As Keys = Keys.PageUp
	Private Const keyRotateDown As Keys = Keys.PageDown
	Private Const keyAccelerator As Keys = Keys.Space
	Private Const keyNorth As Keys = Keys.N
	Private Const keySouth As Keys = Keys.S
	Private Const keyEast As Keys = Keys.E
	Private Const keyWest As Keys = Keys.W
	Private Const keyAddChild As Keys = Keys.Insert
	Private Const keyDelChild As Keys = Keys.Delete
	Private Const keySpinLeft As Keys = Keys.Oemcomma
	Private Const keySpinRight As Keys = Keys.OemPeriod

	Private mSpinDelta As Single = 0
	Private mMoveDeltaLOS As Single = 0
	Private mMoveDeltaX As Single = 0
	Private mMoveDeltaY As Single = 0
	Private mMoveDeltaZ As Single = 0
	Private mTiltDelta As Single = 0

	Protected Overrides Sub OnKeyDown(ByVal e As System.Windows.Forms.KeyEventArgs)
		Select Case e.KeyCode
			Case keyAddChild
				Dim key As Object
				Dim childWidth As Single
				Dim childHeight As Single
				For Each key In mViewer.SelectedTags
					Dim t As SIO3DViewer.Tag = mViewer.Tags.Item(key)
					t.GetChildDimensions(childWidth, childHeight)
					t.Children.Add(t.Children.Count, New TagChild("tagchild", childWidth, childHeight))
				Next
			Case keyDelChild
				Dim key As Object
				For Each key In mViewer.SelectedTags
					Dim t As SIO3DViewer.Tag = mViewer.Tags.Item(key)
					t.Children.Remove(t.Children.Count - 1)
				Next
			Case keyNorth
				'
				' look towards the north (positive Z)
				mViewer.Camera.LookTowardsPositiveZ()
			Case keySouth
				'
				' look towards the south (negative Z)
				mViewer.Camera.LookTowardsNegativeZ()
			Case keyEast
				'
				' look towards the east
				mViewer.Camera.LookTowardsPositiveX()
			Case keyWest
				'
				' look towards the west
				mViewer.Camera.LookTowardsNegativeX()
			Case keySpinLeft
				mSpinDelta = -1
			Case keySpinRight
				mSpinDelta = 1
			Case keyAccelerator
				mViewer.AccelerateMovement = True
			Case keySlideLeft
				mMoveDeltaX = -1
			Case keySlideRight
				mMoveDeltaX = 1
			Case keySlideForward
				mMoveDeltaZ = 1
			Case keySlideBackward
				mMoveDeltaZ = -1
			Case keySlideUp
				mMoveDeltaY = 1
			Case keySlideDown
				mMoveDeltaY = -1
			Case keySlideIn
				mMoveDeltaLOS = 1
			Case keySlideOut
				mMoveDeltaLOS = -1
			Case keyRotateUp
				mTiltDelta = -1
			Case keyRotateDown
				mTiltDelta = 1
		End Select
		MyBase.OnKeyDown(e)
	End Sub

	Protected Overrides Sub OnKeyUp(ByVal e As System.Windows.Forms.KeyEventArgs)
		Select Case e.KeyCode
			Case keyAccelerator
				mViewer.AccelerateMovement = False
			Case keySpinLeft
				mSpinDelta = 0
			Case keySpinRight
				mSpinDelta = 0
			Case keySlideLeft
				mMoveDeltaX = 0
			Case keySlideRight
				mMoveDeltaX = 0
			Case keySlideForward
				mMoveDeltaZ = 0
			Case keySlideBackward
				mMoveDeltaZ = 0
			Case keySlideUp
				mMoveDeltaY = 0
			Case keySlideDown
				mMoveDeltaY = 0
			Case keySlideIn
				mMoveDeltaLOS = 0
			Case keySlideOut
				mMoveDeltaLOS = 0
			Case keyRotateUp
				mTiltDelta = 0
			Case keyRotateDown
				mTiltDelta = 0
		End Select
		MyBase.OnKeyUp(e)
	End Sub

	Private Sub picLookNegativeZ_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles picLookNegativeZ.Click
		mViewer.Camera.LookTowardsNegativeZ()
	End Sub

	Private Sub picLookPositiveZ_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles picLookPositiveZ.Click
		mViewer.Camera.LookTowardsPositiveZ()
	End Sub

	Private Sub picLookPositiveX_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles picLookPositiveX.Click
		mViewer.Camera.LookTowardsPositiveX()
	End Sub

	Private Sub picLookNegativeX_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles picLookNegativeX.Click
		mViewer.Camera.LookTowardsNegativeX()
	End Sub

	Private Sub picMove_MouseDown(ByVal sender As Object, ByVal e As System.Windows.Forms.MouseEventArgs) Handles _
	picMoveBackward.MouseDown, _
	picMoveDown.MouseDown, _
	picMoveForward.MouseDown, _
	picMoveLeft.MouseDown, _
	picMoveRight.MouseDown, _
	picMoveUp.MouseDown, _
	picSpinLeft.MouseDown, _
	picSpinRight.MouseDown, _
	picTiltBackward.MouseDown, _
	picTiltForward.MouseDown, _
	picZoomIn.MouseDown, _
	picZoomOut.MouseDown

		Dim ctl As PictureBox = CType(sender, PictureBox)
		ctl.Capture = True

		Select Case True
			Case sender Is picMoveForward
				mMoveDeltaZ = 1
			Case sender Is picMoveBackward
				mMoveDeltaZ = -1
			Case sender Is picMoveLeft
				mMoveDeltaX = -1
			Case sender Is picMoveRight
				mMoveDeltaX = 1
			Case sender Is picMoveUp
				mMoveDeltaY = 1
			Case sender Is picMoveDown
				mMoveDeltaY = -1
			Case sender Is picSpinLeft
				mSpinDelta = -1
			Case sender Is picSpinRight
				mSpinDelta = 1
			Case sender Is picTiltForward
				mTiltDelta = 1
			Case sender Is picTiltBackward
				mTiltDelta = -1
			Case sender Is picZoomIn
				mMoveDeltaLOS = 1
			Case sender Is picZoomOut
				mMoveDeltaLOS = -1
		End Select

	End Sub

	Private Sub picMove_MouseUp(ByVal sender As Object, ByVal e As System.Windows.Forms.MouseEventArgs) Handles _
	picMoveBackward.MouseUp, _
	picMoveDown.MouseUp, _
	picMoveForward.MouseUp, _
	picMoveLeft.MouseUp, _
	picMoveRight.MouseUp, _
	picMoveUp.MouseUp, _
	picSpinLeft.MouseUp, _
	picSpinRight.MouseUp, _
	picTiltBackward.MouseUp, _
	picTiltForward.MouseUp, _
	picZoomIn.MouseUp, _
	picZoomOut.MouseUp

		Dim ctl As PictureBox = CType(sender, PictureBox)
		ctl.Capture = False

		Select Case True
			Case sender Is picMoveForward
				mMoveDeltaZ = 0
			Case sender Is picMoveBackward
				mMoveDeltaZ = 0
			Case sender Is picMoveLeft
				mMoveDeltaX = 0
			Case sender Is picMoveRight
				mMoveDeltaX = 0
			Case sender Is picMoveUp
				mMoveDeltaY = 0
			Case sender Is picMoveDown
				mMoveDeltaY = 0
			Case sender Is picSpinLeft
				mSpinDelta = 0
			Case sender Is picSpinRight
				mSpinDelta = 0
			Case sender Is picTiltForward
				mTiltDelta = 0
			Case sender Is picTiltBackward
				mTiltDelta = 0
			Case sender Is picZoomIn
				mMoveDeltaLOS = 0
			Case sender Is picZoomOut
				mMoveDeltaLOS = 0
		End Select

	End Sub

#End Region

#Region "Form button event handlers"

	Private Sub chkShowStats_CheckedChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles chkShowStats.CheckedChanged
		Try
			mViewer.ShowStatistics = chkShowStats.Checked
		Catch ex As Exception
			MessageBox.Show(ex.Message, "Show Stats Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub
	Private Sub btnConnect_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnConnect.Click
		Try
			If rbParco.Checked Then
				mData = New Parco.Data(msParcoWebSvc)
			Else
				mData = New Parco.Data(msLocalWebSvc)
			End If

			'Get an IP and port to connect to a resource 
			Dim ds As DataSet = mData.ResourceSelect(CType(cboResourses.SelectedValue, Integer))
			With ds.Tables(0).Rows(0)
				msProviderIP = .Item("X_IP").ToString
				mPort = CType(.Item("I_PRT"), Integer)
			End With
			mStream = New Parco.DataStream(msProviderIP, mPort)


			'create the begin stream request for the fullstream resource in the Stream connected event
			Dim req As New Parco.ParcoMsg.Request(ParcoMsg.RequestType.BeginStream, "xx34")
			If rbSubscription.Checked Then
				'we need to add 1 or more devices to the begin stream request to stay connected to the source
				If lstTags.Items.Count = 0 Then
					Throw New ApplicationException("One or more tags are required for subscription based resources. " & ControlChars.CrLf & ControlChars.CrLf & _
					"Please add one or more tags on the Tags tab.")
				Else
					Dim tag As SIO3DViewer.Tag
					Dim d As Parco.Device
					For Each tag In lstTags.Items
						d = New Parco.Device(tag.Key.ToString)
						req.Devices.AddItem(d, d.ID)
					Next
				End If
			End If
			mStream.Connect()
			mStream.SendRequest(req)

			'now all that is left to do is check for a response from the stream, it is done in the Response event.
		Catch exa As ApplicationException
			MessageBox.Show(exa.Message, "Tags Required", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
			TabControl1.SelectedTab = TabControl1.TabPages(1)

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Connect Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub

	Private Sub btnDisconnect_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnDisConnect.Click
		Try
			CloseStream()
		Catch ex As Exception
			MessageBox.Show(ex.ToString, "Disconnect Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub

	Private Sub btnLoadRes_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnLoadRes.Click
		Try
			'Load the resource list for the selected server
			'Resources give us the IP and Port to connect to
			Me.Cursor = Cursors.WaitCursor
			Dim d As Parco.Data
			If rbParco.Checked Then
				d = New Parco.Data(msParcoWebSvc)
			Else
				d = New Parco.Data(msLocalWebSvc)
			End If

			Dim ds As DataSet = d.ResourceTypeList()
			cboResourses.ValueMember = "I_TYP_RES"
			cboResourses.DisplayMember = "X_DSC_RES"
			cboResourses.DataSource = ds.Tables(0)

			d = Nothing
			btnConnect.Enabled = True
			btnLoadRes.Enabled = False
			rbParco.Enabled = False
			rbLocalServer.Enabled = False

		Catch ex As Exception
			MessageBox.Show(ex.ToString, "Load Resources Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
		Finally
			Me.Cursor = Cursors.Default
		End Try

	End Sub

	Private Sub btnTagAdd_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTagAdd.Click
		Dim f As New frmTag
		f.StartPosition = FormStartPosition.CenterScreen
		f.ShowDialog()
		If f.Valid Then
			Dim tp As TagPlus
			tp = f.TagPlus
			lstTags.Items.Add(tp)
			'check for an existing tag and replace it....
			Dim t As SIO3DViewer.Tag = mViewer.Tags.Item(tp.ID)
			If Not t Is Nothing Then
				mViewer.Tags.Remove(tp.ID)
			End If
			mViewer.Tags.Add(tp.ID, tp)
		End If

	End Sub

	Private Sub btnTagEdit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTagEdit.Click
		Try
			Dim s As String
			Select Case True
				Case lstTags.Items.Count = 0
					s = "No tags to edit"
				Case lstTags.SelectedIndex = -1
					s = "No item selected"
			End Select
			If s = String.Empty Then
				Dim t As TagPlus = CType(lstTags.SelectedItem, TagPlus)
				Dim sOrigKey As String = t.ID
				Dim f As New frmTag
				f.TagPlus = t
				f.StartPosition = FormStartPosition.CenterScreen
				f.ShowDialog()
				If f.Valid Then
					t = f.TagPlus
					Dim i As Integer = lstTags.SelectedIndex
					lstTags.Items.RemoveAt(i)
					lstTags.Items.Insert(i, t)
					lstTags.SelectedIndex = i
					'the key is the tag.key or id, I am using an inherited version here with ID and Name properties for list Binding
					mViewer.Tags.Remove(sOrigKey)
					mViewer.Tags.Add(t.ID, t)
					If sOrigKey <> t.ID Then
						'remove /readd the tag trigger with appropriate key
						Dim trg As Trigger = mTagTriggers.Item(sOrigKey)
						If Not trg Is Nothing Then
							mTagTriggers.RemoveItem(sOrigKey)
							mTagTriggers.AddItem(trg, t.ID)
						End If
						'if we are subscription based, then remove and add the new device
						If rbFullStream.Checked = False AndAlso Not mStream Is Nothing Then
							If mStream.IsConnected Then
								Dim rq As New Parco.ParcoMsg.Request(ParcoMsg.RequestType.RemoveDevice, sOrigKey, sOrigKey)
								mStream.SendRequest(rq)
								Dim re As New ParcoMsg.Request(ParcoMsg.RequestType.AddDevice, t.ID, t.ID)
								mStream.SendRequest(rq)
							End If
						End If
					End If
				End If
			Else
				MessageBox.Show(s, "Edit Failed", MessageBoxButtons.OK, MessageBoxIcon.Information)
			End If
		Catch ex As Exception
			MessageBox.Show(ex.Message, "Edit Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub

	Private Sub btnTagTrigEdit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTagTrigEdit.Click
		Try
			Dim s As String
			Select Case True
				Case lstTags.Items.Count = 0
					s = "No tags to edit"
				Case lstTags.SelectedIndex = -1
					s = "No item selected"
			End Select
			If s = String.Empty Then
				Dim t As TagPlus = CType(lstTags.SelectedItem, TagPlus)
				Dim eKey As New MyMenuClickedArgs
				eKey.TagKey = t.ID
				MenuTrig_Click(Me, eKey)
			Else
				MessageBox.Show(s, "Tag Trigger Edit Failed", MessageBoxButtons.OK, MessageBoxIcon.Information)
			End If
		Catch ex As Exception
			MessageBox.Show(ex.Message, "Tag Trigger Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub

	Private Sub btnTagRem_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTagRem.Click
		Try
			Dim s As String
			Select Case True
				Case lstTags.Items.Count = 0
					s = "No tags to delete"
				Case lstTags.SelectedIndex = -1
					s = "No item selected"
			End Select
			If s = String.Empty Then
				'need to remove the tag from the viewers collection too.
				Dim t As TagPlus = CType(lstTags.SelectedItem, TagPlus)
				'We could also use the t.key property here as well, but use our extended property for consistancy
				mViewer.Tags.Remove(t.ID)
				Dim i As Integer = lstTags.SelectedIndex
				lstTags.Items.RemoveAt(i)

				'check for any tag triggers
				Dim trg As Trigger = mTagTriggers.Item(t.ID)

				If Not trg Is Nothing Then
					'we found it
					mTagTriggers.RemoveItem(t.ID)
					'TODO: In the viewer remove the Obj3D item if we are rendering tag triggers
					'mViewer.Tags.Remove(t.ID & ".trig")
				End If
				'if we are subscription based, remove the tag from our subscription
				If rbFullStream.Checked = False AndAlso Not mStream Is Nothing Then
					If mStream.IsConnected Then
						Dim req As New ParcoMsg.Request(ParcoMsg.RequestType.RemoveDevice, t.ID, t.ID)
					End If
				End If
			Else
				MessageBox.Show(s, "Delete Failed", MessageBoxButtons.OK, MessageBoxIcon.Information)
			End If
		Catch ex As Exception
			MessageBox.Show(ex.Message, "Delete Failed", MessageBoxButtons.OK, MessageBoxIcon.Information)
		End Try
	End Sub
	Private Sub btnTagTrigDel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTagTrigDel.Click
		Try
			Dim t As TagPlus = CType(lstTags.SelectedItem, TagPlus)
			Dim eKey As New MyMenuClickedArgs
			eKey.TagKey = t.ID
			MenuTrigDel_Click(Me, eKey)
			btnTagTrigDel.Enabled = False

			'TODO: in the viewer, remove the tag trigger
		Catch ex As Exception
			MessageBox.Show(ex.Message, "Trigger Delete Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub

	Private Sub lstTags_SelectedIndexChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles lstTags.SelectedIndexChanged
		Try
			If lstTags.SelectedIndex = -1 Then
				btnTagEdit.Enabled = False
				btnTagRem.Enabled = False
				btnTagTrigDel.Enabled = False
				btnTagTrigEdit.Enabled = False
			Else
				btnTagEdit.Enabled = True
				btnTagRem.Enabled = True
				btnTagTrigDel.Enabled = False
				btnTagTrigEdit.Enabled = True
				'check for an associated trigger tag.
				Dim t As TagPlus = DirectCast(lstTags.SelectedItem, TagPlus)
				If Not mTagTriggers.Item(t.ID) Is Nothing Then
					btnTagTrigDel.Enabled = True
				End If
			End If
		Catch ex As Exception
			MessageBox.Show(ex.Message, "Tag List Select Failed", MessageBoxButtons.OK, MessageBoxIcon.Information)
		End Try
	End Sub
#End Region

#Region "context menu event handlers"

	Private Sub MenuTrig_Click(ByVal sender As System.Object, ByVal e As System.EventArgs)
		Try
			Dim eKey As MyMenuClickedArgs
			If TypeOf (e) Is MyMenuClickedArgs Then
				eKey = DirectCast(e, MyMenuClickedArgs)
			Else
				eKey = mTagEventKey
			End If
			If Not eKey Is Nothing Then
				Dim t As SIO3DViewer.Tag = mViewer.Tags.Item(eKey.TagKey)
				If Not t Is Nothing Then
					Dim tp As TagPlus = DirectCast(t, TagPlus)
					Dim trg As Trigger = mTagTriggers.Item(tp.ID)
					Dim bAdd As Boolean = False
					If trg Is Nothing Then
						'we have an add
						bAdd = True
					End If
					'either way the form will know if it is an add or not
					'because a null trigger instance will be an add
					Dim f As New frmTagTrigger
					Dim pOrig As Point3D = ToRealCoord(t.X, t.Y, t.Z)
					f.TagPlus = tp
					f.Trigger = trg
					f.StartPosition = FormStartPosition.CenterScreen
					f.ShowDialog()
					If f.IsValid Then
						'Make sure the trigger location matches the
						'the tag location since the tag may have moved on us.
						'This could cause a seperation isssue, I may have to go back and look at this situation....
						trg = f.Trigger
						Dim pnew As Point3D = ToRealCoord(t.X, t.Y, t.Z)
						If Not pnew.Equals(pOrig) Then
							'for this app, we are not moving trigger in vertical direction!
							trg.Translate(pnew.X - pOrig.X, pnew.Y - pOrig.Y, 0)
						End If
						If bAdd Then
							mTagTriggers.AddItem(trg, tp.ID)
							'add it to the list
							lstTagTrig.Items.Add(tp.ID)
						Else
							'it is already in the list so remove/add it to our hash
							mTagTriggers.RemoveItem(tp.ID)
							mTagTriggers.Item(tp.ID) = trg
						End If
						'hook up the event handler (the edit form always gives us a new trigger instance)
						AddHandler trg.TriggerEvent, AddressOf TriggerEvent
						'cause our buttons to update
						lstTagTrig_SelectedIndexChanged(Me, Nothing)
						lstTags_SelectedIndexChanged(Me, Nothing)

						'TODO: In the viewer, redraw the trigger
						'this requires us to tranlate real coords to viewer coords
						'Note: the region collections are 1 based
						'Dim mt As New MeshTag("TagTrig.x", trg.Regions.Item(1).XMax - trg.Regions.Item(1).Xmin, trg.Regions.Item(1).ZTop - trg.Regions.Item(1).ZBottom)
						'mt.Visible = True
						'mt.TagColor = System.Drawing.Color.Red
						'mt.X = t.X
						'mt.Y = t.Y
						'mt.Z = t.Z
						'mViewer.Tags.Add(t.Key.ToString & ".trig", mt)
						''mViewer.Objects.Add(trg.ID, mt)
					End If
				End If
			End If
		Catch ex As Exception
			MessageBox.Show(ex.Message, "Menu Info Failed", MessageBoxButtons.OK, MessageBoxIcon.Information)
		Finally
			mTagEventKey = Nothing
		End Try
	End Sub

	Private Sub MenuTrigDel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs)
		Try
			Dim eKey As MyMenuClickedArgs
			If TypeOf (e) Is MyMenuClickedArgs Then
				eKey = DirectCast(e, MyMenuClickedArgs)
			Else
				eKey = mTagEventKey
			End If
			If Not eKey Is Nothing Then
				Dim t As SIO3DViewer.Tag = mViewer.Tags.Item(eKey.TagKey)
				If Not t Is Nothing Then
					Dim tp As TagPlus = DirectCast(t, TagPlus)
					'the item key for a tag trigger is the tag.ID
					Dim trg As Parco.Trigger = mTagTriggers.Item(tp.ID)
					If Not trg Is Nothing Then
						'we found it
						mTagTriggers.RemoveItem(tp.ID)
						lstTagTrig.Items.Remove(tp.ID)
						trg = Nothing
						'now update our buttons
						lstTagTrig_SelectedIndexChanged(Me, Nothing)
						lstTags_SelectedIndexChanged(Me, Nothing)

						'TODO: remove the Obj3D item from the screen
						'mViewer.Tags.Remove(tp.ID & ".trig")

					End If
				End If
			End If
		Catch ex As Exception
			MessageBox.Show(ex.Message, "Menu Info Failed", MessageBoxButtons.OK, MessageBoxIcon.Information)
		Finally
			mTagEventKey = Nothing
		End Try
	End Sub
	Private Sub MenuInfo_Click(ByVal sender As System.Object, ByVal e As System.EventArgs)
		Try
			Dim eKey As MyMenuClickedArgs
			If TypeOf (e) Is MyMenuClickedArgs Then
				eKey = DirectCast(e, MyMenuClickedArgs)
			Else
				eKey = mTagEventKey
			End If
			If Not eKey Is Nothing Then
				Dim t As SIO3DViewer.Tag = mViewer.Tags.Item(eKey.TagKey)
				If Not t Is Nothing Then
					Dim tp As TagPlus = DirectCast(t, TagPlus)
					ShowInfoForm(tp)
				End If
			End If
		Catch ex As Exception
			MessageBox.Show(ex.Message, "Menu Info Failed", MessageBoxButtons.OK, MessageBoxIcon.Information)
		Finally
			mTagEventKey = Nothing
		End Try
	End Sub

#End Region

#Region "Trigger Events and Event List Maint"

	Private Sub TriggerEvent(ByVal sender As Object, ByVal oDevice As Parco.Device)
		Try
			Dim t As Trigger = DirectCast(sender, Trigger)
			Dim sb As New System.Text.StringBuilder
			With sb
				.Append("Trig ")
				.Append(t.Name)
				.Append(" reports ")
				.Append(t.Direction.ToString)
				.Append(" for Tag ID ")
				.Append(oDevice.ID)
				.Append(" @ ")
				.Append(Date.Now.ToShortTimeString)
			End With
			lstEvts.Items.Insert(0, sb.ToString)

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Trigger Event Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub
	Private Sub LinkLabelClearEvts_LinkClicked(ByVal sender As System.Object, ByVal e As System.Windows.Forms.LinkLabelLinkClickedEventArgs) Handles LinkLabelClearEvts.LinkClicked
		Try
			lstEvts.Items.Clear()
		Catch ex As Exception
			MessageBox.Show(ex.Message, "List Clear Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)

		End Try
	End Sub
#End Region

#Region "Area Triggers Maint"

	Private Sub lstTriggers_SelectedIndexChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles lstTriggers.SelectedIndexChanged
		Try
			If lstTriggers.SelectedIndex = -1 Then
				btnTrigDel.Enabled = False
				btnTrigEdit.Enabled = False
			Else
				btnTrigDel.Enabled = True
				btnTrigEdit.Enabled = True
			End If
		Catch ex As Exception
			MessageBox.Show(ex.Message, "Trigger Select Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub
	Private Sub chkShowAreaTrigs_CheckedChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles chkShowAreaTrigs.CheckedChanged
		Try
			If mbFormIsLoading = False Then
				If chkShowAreaTrigs.Checked Then
					'move our hash instances to the viewer
					Dim cp As SIO3DViewer.ColoredPlane
					Dim t As Trigger
					Dim key As Object
					For Each key In mViewerTrig.Keys
						cp = DirectCast(mViewerTrig.Item(key), SIO3DViewer.ColoredPlane)
						mViewer.Objects.Add(key, cp)
					Next
					'now set our hash to nothing
					mViewerTrig = Nothing
				Else
					'move the instances from the viewer to the hash
					mViewerTrig = New Hashtable

					Dim cp As SIO3DViewer.ColoredPlane
					Dim t As Trigger
					For Each t In mTriggers
						cp = DirectCast(mViewer.Objects.Item(t.Name), SIO3DViewer.ColoredPlane)
						mViewerTrig.Add(t.Name, cp)
						mViewer.Objects.Remove(t.Name)
					Next
				End If
			End If

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Trigger Show Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub

	Private Sub btnTrigAdd_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTrigAdd.Click
		Try
			Dim ft As New frmTrigger
			ft.ShowDialog()
			If ft.IsValid Then
				Dim t As Trigger = ft.Trig
				mTriggers.AddItem(t, t.Name)
				'if we make it to here (unique name, add the event handler
				AddHandler t.TriggerEvent, AddressOf TriggerEvent
				lstTriggers.Items.Add(t.Name)

				'create a colored plane representing the trigger
				Dim cp As SIO3DViewer.ColoredPlane
				Dim pt As Point3D = ToViewerCoord(t.Regions.Item(1).Xmin, t.Regions.Item(1).Ymin, 0.1)
				'our pt is in viewer coords, the trigger Y is what we want to use for Z
				cp = CreateViewerAreaTrig(t.Name, pt.X, pt.Y, pt.Z, t.Regions.Item(1).XMax - t.Regions.Item(1).Xmin, t.Regions.Item(1).YMax - t.Regions.Item(1).Ymin, Color.FromName(ft.cboTrigColor.SelectedItem.ToString))
				If chkShowAreaTrigs.Checked Then
					mViewer.Objects.Add(t.Name, cp)
				Else
					mViewerTrig.Add(t.Name, cp)
				End If
			End If

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Trigger Add Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub



	Private Sub btnTrigEdit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTrigEdit.Click
		Try
			Dim sName As String = lstTriggers.SelectedItem.ToString
			Dim t As Trigger = mTriggers.Item(sName)
			Dim ft As New frmTrigger
			ft.Trig = t
			'now set the forms trigger color
			Dim ocp As SIO3DViewer.ColoredPlane
			If chkShowAreaTrigs.Checked Then
				ocp = CType(mViewer.Objects.Item(t.Name), ColoredPlane)
			Else
				ocp = CType(mViewerTrig.Item(t.Name), ColoredPlane)
			End If
			'we are stroing the triggers color in the data property
			Dim c As System.Drawing.Color = CType(ocp.Data, System.Drawing.Color)
			ft.TrigColor = c
			ft.ShowDialog()
			If ft.IsValid Then
				t = ft.Trig
				mTriggers.RemoveItem(sName)
				mTriggers.AddItem(t, t.Name)
				'if we make it here then we had a unique name,so add the event handler
				AddHandler t.TriggerEvent, AddressOf TriggerEvent
				If sName <> t.Name Then
					lstTriggers.Items.Remove(sName)
					lstTriggers.Items.Add(t.Name)
				End If

				'create a colored plane representing the trigger
				Dim cp As SIO3DViewer.ColoredPlane
				Dim pt As Point3D = ToViewerCoord(t.Regions.Item(1).Xmin, t.Regions.Item(1).Ymin, 0.1)
				'our pt is in viewer coords, the trigger Y is what we want to use for Z
				cp = CreateViewerAreaTrig(t.Name, pt.X, pt.Y, pt.Z, t.Regions.Item(1).XMax - t.Regions.Item(1).Xmin, t.Regions.Item(1).YMax - t.Regions.Item(1).Ymin, Color.FromName(ft.cboTrigColor.SelectedItem.ToString))
				If chkShowAreaTrigs.Checked Then
					'Remove the old trigger and show the newly configure trigger (the name may have changed, hence the add remove vice replace)
					mViewer.Objects.Remove(sName)
					mViewer.Objects.Add(t.Name, cp)
				Else
					mViewerTrig.Remove(sName)
					mViewerTrig.Add(t.Name, cp)
				End If

			End If

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Trigger Edit Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub

	Private Sub btnTrigDel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTrigDel.Click
		Try
			Dim sKey As String = lstTriggers.SelectedItem.ToString
			If Not mTriggers Is Nothing AndAlso Not mTriggers.Item(sKey) Is Nothing Then
				mTriggers.RemoveItem(sKey)

				lstTriggers.Items.Remove(sKey)
				lstTriggers.SelectedIndex = -1
				'Remove our colored plane representation of the trigger
				If chkShowAreaTrigs.Checked Then
					mViewer.Objects.Remove(sKey)
				Else
					mViewerTrig.Remove(sKey)
				End If
			End If
		Catch ex As Exception
			MessageBox.Show(ex.Message, "Trigger Delete Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub

#End Region

#Region "Tag Triggers Maint"
	Private Sub btnTagTrigEdit2_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTagTrigEdit2.Click
		Try
			Dim eKey As New MyMenuClickedArgs
			eKey.TagKey = lstTagTrig.SelectedItem.ToString
			MenuTrig_Click(Me, eKey)

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Tag Trigger Edit Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub

	Private Sub btnTagTrigDel2_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTagTrigDel2.Click
		Try
			Dim eKey As New MyMenuClickedArgs
			eKey.TagKey = lstTagTrig.SelectedItem.ToString
			MenuTrigDel_Click(Me, eKey)

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Tag Trigger Edit Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub
	Private Sub lstTagTrig_SelectedIndexChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles lstTagTrig.SelectedIndexChanged
		Try
			If lstTagTrig.SelectedIndex = -1 Then
				btnTagTrigDel2.Enabled = False
				btnTagTrigEdit2.Enabled = False
			Else
				btnTagTrigDel2.Enabled = True
				btnTagTrigEdit2.Enabled = True
			End If

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Tag Trigger Select Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
		End Try
	End Sub
#End Region


	Private Sub Button1_Click(ByVal sender As System.Object, ByVal e As System.EventArgs)
		Try
			Dim o As New SIO3DViewer.ColoredPlane(0, 0.1, 0, 10.0, 10.0, System.Drawing.Color.Red)
			'o.WireFrameOnly = True
			o.AlphaBlendingEnabled = True
			Dim fnt As System.Drawing.Font = Me.mViewer.Font
			Dim t As New SIO3DViewer.TextObject("Da Trigga", fnt, 0.1, 0.1, System.Drawing.Color.Black, 1)
			t.OrientationTransform.RotateX(0.9)
			t.OrientationTransform.Translate(0, 0.2, 10)
			o.Children.Add("text", t)


			mViewer.Objects.Add("Plane", o)
			'mViewer.Objects.Add("text", t)
		Catch ex As Exception
			MessageBox.Show(ex.ToString, "Oh shit")
		End Try
	End Sub



End Class
