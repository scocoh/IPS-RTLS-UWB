'##### CONFIDENTIAL - CONFIDENTIAL - CONFIDENTIAL ######
'		                    Parco RTLS™ System
'All information and source code contained herein is confidential and proprietary.
'Copying or modifying this source code is strictly prohibited unless under license of Parco Wireless.
'Copyright © 2001-2005 Parco Merged Media Inc. / Parco Wireless
'All rights reserved.
'##### CONFIDENTIAL - CONFIDENTIAL - CONFIDENTIAL ######
'Author:     Mike Farnsworth, Standard I-O Inc.
'Version:   1.0
'Date:      5/28/2004

'Modification/Author/Date:
'4/1/2005 MWF - Changes made to allow the application to work with the new PAL 651 system and tags.
'the tags are now non numeric, changed the Trigger tags hashtable to use the trigger name as the key
'and not the ID. The ID property of a trigger is for storing the Auto Number Key from the RTLS Database
'if the trigger is persisted there.
'12/1/2005 MWF - Completed changes to work with the Production SDK. Added the History tab as a demo for
'how to impliment the Parco History Player (virtual vcr).


Imports Parco
Imports System.Drawing


Public Class Form1
	Inherits System.Windows.Forms.Form

	Private WithEvents mTimer As System.Timers.Timer
	Private mbNeedsUpdate As Boolean = False

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
    Friend WithEvents picFloor As System.Windows.Forms.PictureBox
    Friend WithEvents Label2 As System.Windows.Forms.Label
    Friend WithEvents rbLocalServer As System.Windows.Forms.RadioButton
    Friend WithEvents rbParco As System.Windows.Forms.RadioButton
    Friend WithEvents btnDisConnect As System.Windows.Forms.Button
    Friend WithEvents btnConnect As System.Windows.Forms.Button
    Friend WithEvents lstData As System.Windows.Forms.ListBox
    Friend WithEvents lstEvt As System.Windows.Forms.ListBox
    Friend WithEvents lstTriggers As System.Windows.Forms.ListBox
    Friend WithEvents btnTrigNew As System.Windows.Forms.Button
    Friend WithEvents btnTrigDel As System.Windows.Forms.Button
    Friend WithEvents txtTrigName As System.Windows.Forms.TextBox
    Friend WithEvents Label1 As System.Windows.Forms.Label
    Friend WithEvents cboTrigDir As System.Windows.Forms.ComboBox
    Friend WithEvents Label3 As System.Windows.Forms.Label
    Friend WithEvents txtInstruction As System.Windows.Forms.TextBox
    Friend WithEvents Label4 As System.Windows.Forms.Label
    Friend WithEvents cboTagSize As System.Windows.Forms.ComboBox
    Friend WithEvents cboTagColor As System.Windows.Forms.ComboBox
    Friend WithEvents Label5 As System.Windows.Forms.Label
    Friend WithEvents txtPos As System.Windows.Forms.TextBox
    Friend WithEvents Label7 As System.Windows.Forms.Label
    Friend WithEvents cboTags As System.Windows.Forms.ComboBox
    Friend WithEvents Label8 As System.Windows.Forms.Label
    Friend WithEvents btnTagTrigDelete As System.Windows.Forms.Button
    Friend WithEvents btnTagTrigger As System.Windows.Forms.Button
    Friend WithEvents cboRadius As System.Windows.Forms.ComboBox
    Friend WithEvents tbTriggers As System.Windows.Forms.TabControl
    Friend WithEvents tabTrigs As System.Windows.Forms.TabPage
    Friend WithEvents tabDevices As System.Windows.Forms.TabPage
    Friend WithEvents tabEvents As System.Windows.Forms.TabPage
    Friend WithEvents linkClear As System.Windows.Forms.LinkLabel
    Friend WithEvents Label6 As System.Windows.Forms.Label
    Friend WithEvents tabTagData As System.Windows.Forms.TabPage
    Friend WithEvents Label9 As System.Windows.Forms.Label
    Friend WithEvents Label10 As System.Windows.Forms.Label
    Friend WithEvents Label11 As System.Windows.Forms.Label
    Friend WithEvents cboTagDir As System.Windows.Forms.ComboBox
    Friend WithEvents txtMsg As System.Windows.Forms.Label
    Friend WithEvents Label12 As System.Windows.Forms.Label
    Friend WithEvents txtTrigBottom As System.Windows.Forms.TextBox
    Friend WithEvents Label13 As System.Windows.Forms.Label
    Friend WithEvents txtTrigTop As System.Windows.Forms.TextBox
    Friend WithEvents Label14 As System.Windows.Forms.Label
    Friend WithEvents txtTagBottom As System.Windows.Forms.TextBox
    Friend WithEvents Label15 As System.Windows.Forms.Label
    Friend WithEvents txtTagTop As System.Windows.Forms.TextBox
    Friend WithEvents cboTrigColor As System.Windows.Forms.ComboBox
    Friend WithEvents Label16 As System.Windows.Forms.Label
    Friend WithEvents pnlMap As System.Windows.Forms.Panel
    Friend WithEvents cboResourses As System.Windows.Forms.ComboBox
    Friend WithEvents Label17 As System.Windows.Forms.Label
    Friend WithEvents btnLoadRes As System.Windows.Forms.Button
	Friend WithEvents tabHistory As System.Windows.Forms.TabPage
	Friend WithEvents dtpStart As System.Windows.Forms.DateTimePicker
	Friend WithEvents txtDevID As System.Windows.Forms.TextBox
	Friend WithEvents Label18 As System.Windows.Forms.Label
	Friend WithEvents Label19 As System.Windows.Forms.Label
	Friend WithEvents Label20 As System.Windows.Forms.Label
	Friend WithEvents btnPlay As System.Windows.Forms.Button
	Friend WithEvents cboRate As System.Windows.Forms.ComboBox
	Friend WithEvents btnPause As System.Windows.Forms.Button
	Friend WithEvents btnStop As System.Windows.Forms.Button
	Friend WithEvents btnLoad As System.Windows.Forms.Button
	Friend WithEvents Label21 As System.Windows.Forms.Label
	Friend WithEvents lstHist As System.Windows.Forms.ListBox
	Friend WithEvents dtpEnd As System.Windows.Forms.DateTimePicker
	Friend WithEvents Label22 As System.Windows.Forms.Label
	Friend WithEvents LinkLabel1 As System.Windows.Forms.LinkLabel
    Friend WithEvents ContextMenu1 As System.Windows.Forms.ContextMenu
    Friend WithEvents mnuCopyTag As System.Windows.Forms.MenuItem
    <System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
        Dim resources As System.Resources.ResourceManager = New System.Resources.ResourceManager(GetType(Form1))
        Me.picFloor = New System.Windows.Forms.PictureBox
        Me.lstData = New System.Windows.Forms.ListBox
        Me.Label2 = New System.Windows.Forms.Label
        Me.rbLocalServer = New System.Windows.Forms.RadioButton
        Me.rbParco = New System.Windows.Forms.RadioButton
        Me.btnDisConnect = New System.Windows.Forms.Button
        Me.btnConnect = New System.Windows.Forms.Button
        Me.lstEvt = New System.Windows.Forms.ListBox
        Me.lstTriggers = New System.Windows.Forms.ListBox
        Me.txtInstruction = New System.Windows.Forms.TextBox
        Me.Label3 = New System.Windows.Forms.Label
        Me.cboTrigDir = New System.Windows.Forms.ComboBox
        Me.Label1 = New System.Windows.Forms.Label
        Me.txtTrigName = New System.Windows.Forms.TextBox
        Me.btnTrigDel = New System.Windows.Forms.Button
        Me.btnTrigNew = New System.Windows.Forms.Button
        Me.Label4 = New System.Windows.Forms.Label
        Me.cboTagSize = New System.Windows.Forms.ComboBox
        Me.cboTagColor = New System.Windows.Forms.ComboBox
        Me.Label5 = New System.Windows.Forms.Label
        Me.txtPos = New System.Windows.Forms.TextBox
        Me.Label7 = New System.Windows.Forms.Label
        Me.cboTags = New System.Windows.Forms.ComboBox
        Me.Label8 = New System.Windows.Forms.Label
        Me.btnTagTrigDelete = New System.Windows.Forms.Button
        Me.btnTagTrigger = New System.Windows.Forms.Button
        Me.cboRadius = New System.Windows.Forms.ComboBox
        Me.tbTriggers = New System.Windows.Forms.TabControl
        Me.tabTrigs = New System.Windows.Forms.TabPage
        Me.cboTrigColor = New System.Windows.Forms.ComboBox
        Me.Label16 = New System.Windows.Forms.Label
        Me.Label12 = New System.Windows.Forms.Label
        Me.txtTrigBottom = New System.Windows.Forms.TextBox
        Me.Label13 = New System.Windows.Forms.Label
        Me.txtTrigTop = New System.Windows.Forms.TextBox
        Me.tabTagData = New System.Windows.Forms.TabPage
        Me.btnLoadRes = New System.Windows.Forms.Button
        Me.Label17 = New System.Windows.Forms.Label
        Me.cboResourses = New System.Windows.Forms.ComboBox
        Me.txtMsg = New System.Windows.Forms.Label
        Me.tabDevices = New System.Windows.Forms.TabPage
        Me.Label14 = New System.Windows.Forms.Label
        Me.txtTagBottom = New System.Windows.Forms.TextBox
        Me.Label15 = New System.Windows.Forms.Label
        Me.txtTagTop = New System.Windows.Forms.TextBox
        Me.Label11 = New System.Windows.Forms.Label
        Me.cboTagDir = New System.Windows.Forms.ComboBox
        Me.Label10 = New System.Windows.Forms.Label
        Me.Label9 = New System.Windows.Forms.Label
        Me.tabEvents = New System.Windows.Forms.TabPage
        Me.Label6 = New System.Windows.Forms.Label
        Me.linkClear = New System.Windows.Forms.LinkLabel
        Me.tabHistory = New System.Windows.Forms.TabPage
        Me.LinkLabel1 = New System.Windows.Forms.LinkLabel
        Me.Label22 = New System.Windows.Forms.Label
        Me.lstHist = New System.Windows.Forms.ListBox
        Me.Label21 = New System.Windows.Forms.Label
        Me.btnLoad = New System.Windows.Forms.Button
        Me.btnStop = New System.Windows.Forms.Button
        Me.btnPause = New System.Windows.Forms.Button
        Me.cboRate = New System.Windows.Forms.ComboBox
        Me.btnPlay = New System.Windows.Forms.Button
        Me.Label20 = New System.Windows.Forms.Label
        Me.Label19 = New System.Windows.Forms.Label
        Me.Label18 = New System.Windows.Forms.Label
        Me.txtDevID = New System.Windows.Forms.TextBox
        Me.dtpEnd = New System.Windows.Forms.DateTimePicker
        Me.dtpStart = New System.Windows.Forms.DateTimePicker
        Me.pnlMap = New System.Windows.Forms.Panel
        Me.ContextMenu1 = New System.Windows.Forms.ContextMenu
        Me.mnuCopyTag = New System.Windows.Forms.MenuItem
        Me.tbTriggers.SuspendLayout()
        Me.tabTrigs.SuspendLayout()
        Me.tabTagData.SuspendLayout()
        Me.tabDevices.SuspendLayout()
        Me.tabEvents.SuspendLayout()
        Me.tabHistory.SuspendLayout()
        Me.pnlMap.SuspendLayout()
        Me.SuspendLayout()
        '
        'picFloor
        '
        Me.picFloor.Location = New System.Drawing.Point(8, 8)
        Me.picFloor.Name = "picFloor"
        Me.picFloor.Size = New System.Drawing.Size(248, 464)
        Me.picFloor.TabIndex = 0
        Me.picFloor.TabStop = False
        '
        'lstData
        '
        Me.lstData.ContextMenu = Me.ContextMenu1
        Me.lstData.Location = New System.Drawing.Point(8, 143)
        Me.lstData.Name = "lstData"
        Me.lstData.Size = New System.Drawing.Size(280, 121)
        Me.lstData.TabIndex = 6
        '
        'Label2
        '
        Me.Label2.Location = New System.Drawing.Point(36, 91)
        Me.Label2.Name = "Label2"
        Me.Label2.Size = New System.Drawing.Size(191, 14)
        Me.Label2.TabIndex = 5
        Me.Label2.Text = "Connection Status:"
        '
        'rbLocalServer
        '
        Me.rbLocalServer.Location = New System.Drawing.Point(190, 8)
        Me.rbLocalServer.Name = "rbLocalServer"
        Me.rbLocalServer.Size = New System.Drawing.Size(88, 16)
        Me.rbLocalServer.TabIndex = 1
        Me.rbLocalServer.Text = "Local Server"
        '
        'rbParco
        '
        Me.rbParco.Location = New System.Drawing.Point(96, 8)
        Me.rbParco.Name = "rbParco"
        Me.rbParco.Size = New System.Drawing.Size(88, 16)
        Me.rbParco.TabIndex = 0
        Me.rbParco.Text = "Parco Server"
        '
        'btnDisConnect
        '
        Me.btnDisConnect.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnDisConnect.Location = New System.Drawing.Point(180, 54)
        Me.btnDisConnect.Name = "btnDisConnect"
        Me.btnDisConnect.Size = New System.Drawing.Size(75, 20)
        Me.btnDisConnect.TabIndex = 5
        Me.btnDisConnect.Text = "Disconnect"
        '
        'btnConnect
        '
        Me.btnConnect.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnConnect.Location = New System.Drawing.Point(98, 54)
        Me.btnConnect.Name = "btnConnect"
        Me.btnConnect.Size = New System.Drawing.Size(75, 20)
        Me.btnConnect.TabIndex = 4
        Me.btnConnect.Text = "Connect"
        '
        'lstEvt
        '
        Me.lstEvt.Location = New System.Drawing.Point(8, 24)
        Me.lstEvt.Name = "lstEvt"
        Me.lstEvt.Size = New System.Drawing.Size(280, 290)
        Me.lstEvt.TabIndex = 10
        '
        'lstTriggers
        '
        Me.lstTriggers.Location = New System.Drawing.Point(45, 8)
        Me.lstTriggers.Name = "lstTriggers"
        Me.lstTriggers.Size = New System.Drawing.Size(202, 69)
        Me.lstTriggers.TabIndex = 11
        '
        'txtInstruction
        '
        Me.txtInstruction.BackColor = System.Drawing.SystemColors.Control
        Me.txtInstruction.BorderStyle = System.Windows.Forms.BorderStyle.None
        Me.txtInstruction.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.txtInstruction.ForeColor = System.Drawing.Color.DarkBlue
        Me.txtInstruction.Location = New System.Drawing.Point(59, 246)
        Me.txtInstruction.Multiline = True
        Me.txtInstruction.Name = "txtInstruction"
        Me.txtInstruction.ReadOnly = True
        Me.txtInstruction.Size = New System.Drawing.Size(152, 26)
        Me.txtInstruction.TabIndex = 18
        Me.txtInstruction.Text = ""
        '
        'Label3
        '
        Me.Label3.Location = New System.Drawing.Point(58, 144)
        Me.Label3.Name = "Label3"
        Me.Label3.Size = New System.Drawing.Size(64, 16)
        Me.Label3.TabIndex = 17
        Me.Label3.Text = "Direction:"
        Me.Label3.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'cboTrigDir
        '
        Me.cboTrigDir.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
        Me.cboTrigDir.Items.AddRange(New Object() {"While In", "While Out", "On Cross", "On Enter", "On Exit"})
        Me.cboTrigDir.Location = New System.Drawing.Point(126, 142)
        Me.cboTrigDir.Name = "cboTrigDir"
        Me.cboTrigDir.Size = New System.Drawing.Size(102, 21)
        Me.cboTrigDir.TabIndex = 16
        '
        'Label1
        '
        Me.Label1.Location = New System.Drawing.Point(72, 121)
        Me.Label1.Name = "Label1"
        Me.Label1.Size = New System.Drawing.Size(48, 8)
        Me.Label1.TabIndex = 15
        Me.Label1.Text = "Name:"
        Me.Label1.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'txtTrigName
        '
        Me.txtTrigName.Location = New System.Drawing.Point(125, 115)
        Me.txtTrigName.Name = "txtTrigName"
        Me.txtTrigName.Size = New System.Drawing.Size(102, 20)
        Me.txtTrigName.TabIndex = 14
        Me.txtTrigName.Text = ""
        '
        'btnTrigDel
        '
        Me.btnTrigDel.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnTrigDel.Location = New System.Drawing.Point(152, 83)
        Me.btnTrigDel.Name = "btnTrigDel"
        Me.btnTrigDel.Size = New System.Drawing.Size(75, 25)
        Me.btnTrigDel.TabIndex = 13
        Me.btnTrigDel.Text = "Delete"
        '
        'btnTrigNew
        '
        Me.btnTrigNew.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnTrigNew.Location = New System.Drawing.Point(72, 83)
        Me.btnTrigNew.Name = "btnTrigNew"
        Me.btnTrigNew.Size = New System.Drawing.Size(75, 25)
        Me.btnTrigNew.TabIndex = 12
        Me.btnTrigNew.Text = "Begin Drag"
        '
        'Label4
        '
        Me.Label4.Location = New System.Drawing.Point(86, 275)
        Me.Label4.Name = "Label4"
        Me.Label4.Size = New System.Drawing.Size(74, 16)
        Me.Label4.TabIndex = 7
        Me.Label4.Text = "Tag Size (px):"
        Me.Label4.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'cboTagSize
        '
        Me.cboTagSize.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
        Me.cboTagSize.Items.AddRange(New Object() {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10"})
        Me.cboTagSize.Location = New System.Drawing.Point(160, 272)
        Me.cboTagSize.Name = "cboTagSize"
        Me.cboTagSize.Size = New System.Drawing.Size(64, 21)
        Me.cboTagSize.TabIndex = 7
        '
        'cboTagColor
        '
        Me.cboTagColor.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
        Me.cboTagColor.Location = New System.Drawing.Point(88, 299)
        Me.cboTagColor.Name = "cboTagColor"
        Me.cboTagColor.Size = New System.Drawing.Size(137, 21)
        Me.cboTagColor.TabIndex = 8
        '
        'Label5
        '
        Me.Label5.Location = New System.Drawing.Point(30, 301)
        Me.Label5.Name = "Label5"
        Me.Label5.Size = New System.Drawing.Size(59, 16)
        Me.Label5.TabIndex = 10
        Me.Label5.Text = "Tag Color:"
        Me.Label5.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'txtPos
        '
        Me.txtPos.BackColor = System.Drawing.SystemColors.Control
        Me.txtPos.ForeColor = System.Drawing.Color.Navy
        Me.txtPos.Location = New System.Drawing.Point(136, 274)
        Me.txtPos.Name = "txtPos"
        Me.txtPos.Size = New System.Drawing.Size(88, 20)
        Me.txtPos.TabIndex = 14
        Me.txtPos.Text = ""
        '
        'Label7
        '
        Me.Label7.Location = New System.Drawing.Point(24, 277)
        Me.Label7.Name = "Label7"
        Me.Label7.Size = New System.Drawing.Size(112, 16)
        Me.Label7.TabIndex = 19
        Me.Label7.Text = "Mouse Coordinates:"
        Me.Label7.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'cboTags
        '
        Me.cboTags.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
        Me.cboTags.Location = New System.Drawing.Point(113, 22)
        Me.cboTags.Name = "cboTags"
        Me.cboTags.Size = New System.Drawing.Size(106, 21)
        Me.cboTags.TabIndex = 12
        '
        'Label8
        '
        Me.Label8.Location = New System.Drawing.Point(54, 24)
        Me.Label8.Name = "Label8"
        Me.Label8.Size = New System.Drawing.Size(51, 16)
        Me.Label8.TabIndex = 11
        Me.Label8.Text = "Tag ID:"
        Me.Label8.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'btnTagTrigDelete
        '
        Me.btnTagTrigDelete.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnTagTrigDelete.Location = New System.Drawing.Point(151, 157)
        Me.btnTagTrigDelete.Name = "btnTagTrigDelete"
        Me.btnTagTrigDelete.Size = New System.Drawing.Size(75, 24)
        Me.btnTagTrigDelete.TabIndex = 14
        Me.btnTagTrigDelete.Text = "Delete"
        '
        'btnTagTrigger
        '
        Me.btnTagTrigger.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnTagTrigger.Location = New System.Drawing.Point(63, 157)
        Me.btnTagTrigger.Name = "btnTagTrigger"
        Me.btnTagTrigger.Size = New System.Drawing.Size(75, 24)
        Me.btnTagTrigger.TabIndex = 13
        Me.btnTagTrigger.Text = "Make Trig"
        '
        'cboRadius
        '
        Me.cboRadius.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
        Me.cboRadius.Items.AddRange(New Object() {"1.0", "1.5", "2.0", "2.5", "3.0", "3.5", "4.0", "4.5", "5.0", "5.5", "6.0"})
        Me.cboRadius.Location = New System.Drawing.Point(164, 48)
        Me.cboRadius.Name = "cboRadius"
        Me.cboRadius.Size = New System.Drawing.Size(56, 21)
        Me.cboRadius.TabIndex = 15
        '
        'tbTriggers
        '
        Me.tbTriggers.Anchor = CType((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
        Me.tbTriggers.Controls.Add(Me.tabTrigs)
        Me.tbTriggers.Controls.Add(Me.tabTagData)
        Me.tbTriggers.Controls.Add(Me.tabDevices)
        Me.tbTriggers.Controls.Add(Me.tabEvents)
        Me.tbTriggers.Controls.Add(Me.tabHistory)
        Me.tbTriggers.Location = New System.Drawing.Point(472, 8)
        Me.tbTriggers.Name = "tbTriggers"
        Me.tbTriggers.SelectedIndex = 0
        Me.tbTriggers.Size = New System.Drawing.Size(304, 368)
        Me.tbTriggers.TabIndex = 14
        '
        'tabTrigs
        '
        Me.tabTrigs.Controls.Add(Me.cboTrigColor)
        Me.tabTrigs.Controls.Add(Me.Label16)
        Me.tabTrigs.Controls.Add(Me.Label12)
        Me.tabTrigs.Controls.Add(Me.txtTrigBottom)
        Me.tabTrigs.Controls.Add(Me.lstTriggers)
        Me.tabTrigs.Controls.Add(Me.txtInstruction)
        Me.tabTrigs.Controls.Add(Me.Label3)
        Me.tabTrigs.Controls.Add(Me.cboTrigDir)
        Me.tabTrigs.Controls.Add(Me.Label1)
        Me.tabTrigs.Controls.Add(Me.txtTrigName)
        Me.tabTrigs.Controls.Add(Me.btnTrigDel)
        Me.tabTrigs.Controls.Add(Me.btnTrigNew)
        Me.tabTrigs.Controls.Add(Me.txtPos)
        Me.tabTrigs.Controls.Add(Me.Label7)
        Me.tabTrigs.Controls.Add(Me.Label13)
        Me.tabTrigs.Controls.Add(Me.txtTrigTop)
        Me.tabTrigs.Location = New System.Drawing.Point(4, 22)
        Me.tabTrigs.Name = "tabTrigs"
        Me.tabTrigs.Size = New System.Drawing.Size(296, 342)
        Me.tabTrigs.TabIndex = 0
        Me.tabTrigs.Text = "Triggers"
        '
        'cboTrigColor
        '
        Me.cboTrigColor.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
        Me.cboTrigColor.Location = New System.Drawing.Point(125, 223)
        Me.cboTrigColor.Name = "cboTrigColor"
        Me.cboTrigColor.Size = New System.Drawing.Size(137, 21)
        Me.cboTrigColor.TabIndex = 24
        '
        'Label16
        '
        Me.Label16.Location = New System.Drawing.Point(67, 225)
        Me.Label16.Name = "Label16"
        Me.Label16.Size = New System.Drawing.Size(59, 16)
        Me.Label16.TabIndex = 25
        Me.Label16.Text = "Trig Color:"
        Me.Label16.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'Label12
        '
        Me.Label12.Location = New System.Drawing.Point(45, 198)
        Me.Label12.Name = "Label12"
        Me.Label12.Size = New System.Drawing.Size(80, 16)
        Me.Label12.TabIndex = 21
        Me.Label12.Text = "Bottom Elev:"
        Me.Label12.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'txtTrigBottom
        '
        Me.txtTrigBottom.Location = New System.Drawing.Point(125, 196)
        Me.txtTrigBottom.Name = "txtTrigBottom"
        Me.txtTrigBottom.Size = New System.Drawing.Size(102, 20)
        Me.txtTrigBottom.TabIndex = 20
        Me.txtTrigBottom.Text = "-1"
        '
        'Label13
        '
        Me.Label13.Location = New System.Drawing.Point(42, 170)
        Me.Label13.Name = "Label13"
        Me.Label13.Size = New System.Drawing.Size(80, 16)
        Me.Label13.TabIndex = 23
        Me.Label13.Text = "Top Elev:"
        Me.Label13.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'txtTrigTop
        '
        Me.txtTrigTop.Location = New System.Drawing.Point(125, 169)
        Me.txtTrigTop.Name = "txtTrigTop"
        Me.txtTrigTop.Size = New System.Drawing.Size(102, 20)
        Me.txtTrigTop.TabIndex = 22
        Me.txtTrigTop.Text = "8"
        '
        'tabTagData
        '
        Me.tabTagData.Controls.Add(Me.btnLoadRes)
        Me.tabTagData.Controls.Add(Me.Label17)
        Me.tabTagData.Controls.Add(Me.cboResourses)
        Me.tabTagData.Controls.Add(Me.txtMsg)
        Me.tabTagData.Controls.Add(Me.lstData)
        Me.tabTagData.Controls.Add(Me.Label2)
        Me.tabTagData.Controls.Add(Me.rbLocalServer)
        Me.tabTagData.Controls.Add(Me.rbParco)
        Me.tabTagData.Controls.Add(Me.btnDisConnect)
        Me.tabTagData.Controls.Add(Me.btnConnect)
        Me.tabTagData.Controls.Add(Me.Label4)
        Me.tabTagData.Controls.Add(Me.cboTagSize)
        Me.tabTagData.Controls.Add(Me.cboTagColor)
        Me.tabTagData.Controls.Add(Me.Label5)
        Me.tabTagData.Location = New System.Drawing.Point(4, 22)
        Me.tabTagData.Name = "tabTagData"
        Me.tabTagData.Size = New System.Drawing.Size(296, 342)
        Me.tabTagData.TabIndex = 3
        Me.tabTagData.Text = "Tag Data"
        '
        'btnLoadRes
        '
        Me.btnLoadRes.FlatStyle = System.Windows.Forms.FlatStyle.Flat
        Me.btnLoadRes.Location = New System.Drawing.Point(246, 27)
        Me.btnLoadRes.Name = "btnLoadRes"
        Me.btnLoadRes.Size = New System.Drawing.Size(40, 20)
        Me.btnLoadRes.TabIndex = 3
        Me.btnLoadRes.Text = "Load"
        '
        'Label17
        '
        Me.Label17.Location = New System.Drawing.Point(8, 31)
        Me.Label17.Name = "Label17"
        Me.Label17.Size = New System.Drawing.Size(88, 14)
        Me.Label17.TabIndex = 13
        Me.Label17.Text = "Resource Type"
        Me.Label17.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'cboResourses
        '
        Me.cboResourses.Location = New System.Drawing.Point(96, 27)
        Me.cboResourses.Name = "cboResourses"
        Me.cboResourses.Size = New System.Drawing.Size(144, 21)
        Me.cboResourses.TabIndex = 2
        '
        'txtMsg
        '
        Me.txtMsg.ForeColor = System.Drawing.Color.Navy
        Me.txtMsg.Location = New System.Drawing.Point(39, 112)
        Me.txtMsg.Name = "txtMsg"
        Me.txtMsg.Size = New System.Drawing.Size(210, 25)
        Me.txtMsg.TabIndex = 11
        '
        'tabDevices
        '
        Me.tabDevices.Controls.Add(Me.Label14)
        Me.tabDevices.Controls.Add(Me.txtTagBottom)
        Me.tabDevices.Controls.Add(Me.Label15)
        Me.tabDevices.Controls.Add(Me.txtTagTop)
        Me.tabDevices.Controls.Add(Me.Label11)
        Me.tabDevices.Controls.Add(Me.cboTagDir)
        Me.tabDevices.Controls.Add(Me.Label10)
        Me.tabDevices.Controls.Add(Me.Label9)
        Me.tabDevices.Controls.Add(Me.cboRadius)
        Me.tabDevices.Controls.Add(Me.btnTagTrigger)
        Me.tabDevices.Controls.Add(Me.btnTagTrigDelete)
        Me.tabDevices.Controls.Add(Me.Label8)
        Me.tabDevices.Controls.Add(Me.cboTags)
        Me.tabDevices.Location = New System.Drawing.Point(4, 22)
        Me.tabDevices.Name = "tabDevices"
        Me.tabDevices.Size = New System.Drawing.Size(296, 342)
        Me.tabDevices.TabIndex = 1
        Me.tabDevices.Text = "Tag Triggers"
        '
        'Label14
        '
        Me.Label14.Location = New System.Drawing.Point(32, 131)
        Me.Label14.Name = "Label14"
        Me.Label14.Size = New System.Drawing.Size(80, 16)
        Me.Label14.TabIndex = 25
        Me.Label14.Text = "Bottom Elev:"
        Me.Label14.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'txtTagBottom
        '
        Me.txtTagBottom.Location = New System.Drawing.Point(113, 128)
        Me.txtTagBottom.Name = "txtTagBottom"
        Me.txtTagBottom.Size = New System.Drawing.Size(106, 20)
        Me.txtTagBottom.TabIndex = 24
        Me.txtTagBottom.Text = "-1"
        '
        'Label15
        '
        Me.Label15.Location = New System.Drawing.Point(29, 103)
        Me.Label15.Name = "Label15"
        Me.Label15.Size = New System.Drawing.Size(80, 16)
        Me.Label15.TabIndex = 27
        Me.Label15.Text = "Top Elev:"
        Me.Label15.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'txtTagTop
        '
        Me.txtTagTop.Location = New System.Drawing.Point(113, 102)
        Me.txtTagTop.Name = "txtTagTop"
        Me.txtTagTop.Size = New System.Drawing.Size(106, 20)
        Me.txtTagTop.TabIndex = 26
        Me.txtTagTop.Text = "8"
        '
        'Label11
        '
        Me.Label11.Location = New System.Drawing.Point(47, 78)
        Me.Label11.Name = "Label11"
        Me.Label11.Size = New System.Drawing.Size(64, 16)
        Me.Label11.TabIndex = 19
        Me.Label11.Text = "Direction:"
        Me.Label11.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'cboTagDir
        '
        Me.cboTagDir.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
        Me.cboTagDir.Items.AddRange(New Object() {"While In", "While Out", "On Cross", "On Enter", "On Exit"})
        Me.cboTagDir.Location = New System.Drawing.Point(113, 75)
        Me.cboTagDir.Name = "cboTagDir"
        Me.cboTagDir.Size = New System.Drawing.Size(107, 21)
        Me.cboTagDir.TabIndex = 18
        '
        'Label10
        '
        Me.Label10.Location = New System.Drawing.Point(65, 192)
        Me.Label10.Name = "Label10"
        Me.Label10.Size = New System.Drawing.Size(160, 96)
        Me.Label10.TabIndex = 17
        Me.Label10.Text = "We are creating an octagonal shaped trigger with the tag as the centroid. The tri" & _
        "gger is moved each time the device moves, creating a portable trigger."
        '
        'Label9
        '
        Me.Label9.Location = New System.Drawing.Point(45, 52)
        Me.Label9.Name = "Label9"
        Me.Label9.Size = New System.Drawing.Size(104, 16)
        Me.Label9.TabIndex = 16
        Me.Label9.Text = "Octogon Radius:"
        Me.Label9.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'tabEvents
        '
        Me.tabEvents.Controls.Add(Me.Label6)
        Me.tabEvents.Controls.Add(Me.linkClear)
        Me.tabEvents.Controls.Add(Me.lstEvt)
        Me.tabEvents.Location = New System.Drawing.Point(4, 22)
        Me.tabEvents.Name = "tabEvents"
        Me.tabEvents.Size = New System.Drawing.Size(296, 342)
        Me.tabEvents.TabIndex = 2
        Me.tabEvents.Text = "Events"
        '
        'Label6
        '
        Me.Label6.Location = New System.Drawing.Point(9, 8)
        Me.Label6.Name = "Label6"
        Me.Label6.Size = New System.Drawing.Size(160, 16)
        Me.Label6.TabIndex = 12
        Me.Label6.Text = "Trigger Event Notifications:"
        '
        'linkClear
        '
        Me.linkClear.Location = New System.Drawing.Point(232, 320)
        Me.linkClear.Name = "linkClear"
        Me.linkClear.Size = New System.Drawing.Size(56, 16)
        Me.linkClear.TabIndex = 11
        Me.linkClear.TabStop = True
        Me.linkClear.Text = "Clear List"
        '
        'tabHistory
        '
        Me.tabHistory.Controls.Add(Me.LinkLabel1)
        Me.tabHistory.Controls.Add(Me.Label22)
        Me.tabHistory.Controls.Add(Me.lstHist)
        Me.tabHistory.Controls.Add(Me.Label21)
        Me.tabHistory.Controls.Add(Me.btnLoad)
        Me.tabHistory.Controls.Add(Me.btnStop)
        Me.tabHistory.Controls.Add(Me.btnPause)
        Me.tabHistory.Controls.Add(Me.cboRate)
        Me.tabHistory.Controls.Add(Me.btnPlay)
        Me.tabHistory.Controls.Add(Me.Label20)
        Me.tabHistory.Controls.Add(Me.Label19)
        Me.tabHistory.Controls.Add(Me.Label18)
        Me.tabHistory.Controls.Add(Me.txtDevID)
        Me.tabHistory.Controls.Add(Me.dtpEnd)
        Me.tabHistory.Controls.Add(Me.dtpStart)
        Me.tabHistory.Location = New System.Drawing.Point(4, 22)
        Me.tabHistory.Name = "tabHistory"
        Me.tabHistory.Size = New System.Drawing.Size(296, 342)
        Me.tabHistory.TabIndex = 4
        Me.tabHistory.Text = "History"
        '
        'LinkLabel1
        '
        Me.LinkLabel1.Location = New System.Drawing.Point(13, 160)
        Me.LinkLabel1.Name = "LinkLabel1"
        Me.LinkLabel1.Size = New System.Drawing.Size(100, 15)
        Me.LinkLabel1.TabIndex = 14
        Me.LinkLabel1.TabStop = True
        Me.LinkLabel1.Text = "Clear Messages"
        '
        'Label22
        '
        Me.Label22.Location = New System.Drawing.Point(16, 104)
        Me.Label22.Name = "Label22"
        Me.Label22.Size = New System.Drawing.Size(262, 31)
        Me.Label22.TabIndex = 13
        Me.Label22.Text = "Enter one tag like 00000709 or a comma seperated list of tags."
        '
        'lstHist
        '
        Me.lstHist.Location = New System.Drawing.Point(10, 185)
        Me.lstHist.Name = "lstHist"
        Me.lstHist.Size = New System.Drawing.Size(277, 82)
        Me.lstHist.TabIndex = 12
        '
        'Label21
        '
        Me.Label21.Location = New System.Drawing.Point(37, 272)
        Me.Label21.Name = "Label21"
        Me.Label21.Size = New System.Drawing.Size(68, 23)
        Me.Label21.TabIndex = 11
        Me.Label21.Text = "Play Rate:"
        Me.Label21.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'btnLoad
        '
        Me.btnLoad.Location = New System.Drawing.Point(212, 152)
        Me.btnLoad.Name = "btnLoad"
        Me.btnLoad.TabIndex = 10
        Me.btnLoad.Text = "Load"
        '
        'btnStop
        '
        Me.btnStop.Enabled = False
        Me.btnStop.Location = New System.Drawing.Point(202, 312)
        Me.btnStop.Name = "btnStop"
        Me.btnStop.TabIndex = 9
        Me.btnStop.Text = "Stop"
        '
        'btnPause
        '
        Me.btnPause.Enabled = False
        Me.btnPause.Location = New System.Drawing.Point(118, 312)
        Me.btnPause.Name = "btnPause"
        Me.btnPause.TabIndex = 8
        Me.btnPause.Text = "Pause"
        '
        'cboRate
        '
        Me.cboRate.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList
        Me.cboRate.Items.AddRange(New Object() {"0.5", "1", "2", "5", "10", "20", "50", "100", "1000"})
        Me.cboRate.Location = New System.Drawing.Point(118, 280)
        Me.cboRate.Name = "cboRate"
        Me.cboRate.Size = New System.Drawing.Size(121, 21)
        Me.cboRate.TabIndex = 7
        '
        'btnPlay
        '
        Me.btnPlay.Enabled = False
        Me.btnPlay.Location = New System.Drawing.Point(33, 312)
        Me.btnPlay.Name = "btnPlay"
        Me.btnPlay.TabIndex = 6
        Me.btnPlay.Text = "Play"
        '
        'Label20
        '
        Me.Label20.Location = New System.Drawing.Point(16, 72)
        Me.Label20.Name = "Label20"
        Me.Label20.Size = New System.Drawing.Size(68, 23)
        Me.Label20.TabIndex = 5
        Me.Label20.Text = "For Tag(s):"
        Me.Label20.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'Label19
        '
        Me.Label19.Location = New System.Drawing.Point(16, 48)
        Me.Label19.Name = "Label19"
        Me.Label19.Size = New System.Drawing.Size(68, 23)
        Me.Label19.TabIndex = 4
        Me.Label19.Text = "End Date:"
        Me.Label19.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'Label18
        '
        Me.Label18.Location = New System.Drawing.Point(16, 16)
        Me.Label18.Name = "Label18"
        Me.Label18.Size = New System.Drawing.Size(63, 23)
        Me.Label18.TabIndex = 3
        Me.Label18.Text = "Begin Date:"
        Me.Label18.TextAlign = System.Drawing.ContentAlignment.MiddleRight
        '
        'txtDevID
        '
        Me.txtDevID.Location = New System.Drawing.Point(94, 80)
        Me.txtDevID.Name = "txtDevID"
        Me.txtDevID.Size = New System.Drawing.Size(192, 20)
        Me.txtDevID.TabIndex = 2
        Me.txtDevID.Text = ""
        '
        'dtpEnd
        '
        Me.dtpEnd.Format = System.Windows.Forms.DateTimePickerFormat.Time
        Me.dtpEnd.Location = New System.Drawing.Point(93, 48)
        Me.dtpEnd.Name = "dtpEnd"
        Me.dtpEnd.TabIndex = 1
        '
        'dtpStart
        '
        Me.dtpStart.Format = System.Windows.Forms.DateTimePickerFormat.Time
        Me.dtpStart.Location = New System.Drawing.Point(93, 16)
        Me.dtpStart.Name = "dtpStart"
        Me.dtpStart.TabIndex = 0
        '
        'pnlMap
        '
        Me.pnlMap.AutoScroll = True
        Me.pnlMap.Controls.Add(Me.picFloor)
        Me.pnlMap.Location = New System.Drawing.Point(0, 0)
        Me.pnlMap.Name = "pnlMap"
        Me.pnlMap.Size = New System.Drawing.Size(464, 480)
        Me.pnlMap.TabIndex = 16
        '
        'ContextMenu1
        '
        Me.ContextMenu1.MenuItems.AddRange(New System.Windows.Forms.MenuItem() {Me.mnuCopyTag})
        '
        'mnuCopyTag
        '
        Me.mnuCopyTag.Index = 0
        Me.mnuCopyTag.Text = "Copy Tag ID"
        '
        'Form1
        '
        Me.AutoScaleBaseSize = New System.Drawing.Size(5, 13)
        Me.ClientSize = New System.Drawing.Size(784, 478)
        Me.Controls.Add(Me.tbTriggers)
        Me.Controls.Add(Me.pnlMap)
        Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
        Me.Name = "Form1"
        Me.Text = "Parco Trigger Demonstration"
        Me.tbTriggers.ResumeLayout(False)
        Me.tabTrigs.ResumeLayout(False)
        Me.tabTagData.ResumeLayout(False)
        Me.tabDevices.ResumeLayout(False)
        Me.tabEvents.ResumeLayout(False)
        Me.tabHistory.ResumeLayout(False)
        Me.pnlMap.ResumeLayout(False)
        Me.ResumeLayout(False)

    End Sub

#End Region

    Private mappConfig As New System.Configuration.AppSettingsReader
    Private mbUseParcoData As Boolean

    Private msParcoWebSvc As String
    Private msLocalWebSvc As String
    Private msProviderIP As String
    Private mPort As Integer = 0
    Private WithEvents mStream As Parco.DataStream
	Private mData As Parco.Data
	Private WithEvents mHistory As Parco.History

    Private mXScale As Single 'used for proportioning the pixels width of the the picture box to real X coordinates
    Private mYScale As Single  'used for proportioning the pixels width of the the picture box to real Y coordinates

    'Triggers
	Private mTriggers As New Parco.TriggerCollection	' Custom collection of trigger areas 
    'tags
	Private mTags As New Parco.TagCollection	 'Custom collection of devices(Tags)
    'Moveable Tag Triggers
	Private mTagTriggers As New Parco.TriggerCollection	'Custom collection of triggers that are assigned to a device

    Private mSynchLock As String = "Notbusy"

    'Mouse_OnDown varibles
    Private mXStart As Single
    Private mYStart As Single

    'triggers and trigger addition variables
    Private mbAddingTrigger As Boolean
    Private msNewMsg As String = "Enter a name and direction, then click Begin Drag."

    'GDI+ drawing objects....
    Private mFont As New Font("Tahoma", 8)           'used for drawing text
    Private mBrush As New SolidBrush(Color.Navy)    'used for drawing text
    Private mTagBrush As New SolidBrush(Color.Red)
    Private mTagFont As New Font("Tahoma", 5, FontStyle.Bold)
    Private mTagPen As New Pen(Color.Red, 1)
    Private mnTagSize As Single = 6.0F
    Private mTagColor As Color = Color.Blue
    Private mTrigPen As New Pen(Color.Red)


#Region "Form Load and app intialization"

    Private Sub Form1_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles MyBase.Load
        Dim bUseDefaultMap As Boolean
        Dim x, y As Single
        Dim img As Image
        Try

            mappConfig = New Configuration.AppSettingsReader
            btnDisConnect.Enabled = False

            mbUseParcoData = CType(mappConfig.GetValue("UseParcoData", GetType(Boolean)), Boolean)
            If mbUseParcoData Then
                rbParco.Checked = True
            Else
                rbLocalServer.Checked = True
            End If

            msParcoWebSvc = mappConfig.GetValue("ParcoWebServiceURL", GetType(String)).ToString
            msLocalWebSvc = mappConfig.GetValue("LocalWebServiceURL", GetType(String)).ToString
            bUseDefaultMap = CType(mappConfig.GetValue("UseDefaultMap", GetType(Boolean)), Boolean)

            If bUseDefaultMap = True Then
                x = 60
                y = 50
                img = picFloor.Image.FromFile(Application.StartupPath & "\grid_box.bmp")

            Else
                x = CType(mappConfig.GetValue("MapX", GetType(String)).ToString, Single)
                y = CType(mappConfig.GetValue("MapY", GetType(String)).ToString, Single)
                img = picFloor.Image.FromFile(Application.StartupPath & "\" & mappConfig.GetValue("MapImage", GetType(String)).ToString)
            End If
            picFloor.Image = img
            'keep the picture box's height and proportionally adjust its width
            picFloor.Width = CType((x / y) * picFloor.Height, Integer)
            picFloor.SizeMode = PictureBoxSizeMode.StretchImage

            'size the form and panel for the image.
            pnlMap.AutoScroll = True
            pnlMap.Height = picFloor.Height + 30
            Me.Width = pnlMap.Width + tbTriggers.Width + 20
            Me.Height = pnlMap.Height + 35
            'and now anchor the panel on all 4 sides to create the automatic scrolling
            pnlMap.Anchor = AnchorStyles.Top Or AnchorStyles.Left Or AnchorStyles.Right Or AnchorStyles.Bottom


            'set our proportioning constants for relating the RTLS coordinates to the picture boxes pixel dimensions
            mXScale = x / picFloor.Width
            mYScale = y / picFloor.Height


            'initialize the form's controls
            btnTrigDel.Enabled = False
            txtInstruction.Text = msNewMsg
            cboTagSize.SelectedItem = "6"
            LoadColors()
            cboTagColor.SelectedItem = "Blue"
            cboTrigDir.SelectedIndex = 0
            cboTagDir.SelectedIndex = 0

            tbTriggers.SelectedIndex = 1
            'enable it after resource list is populated
            btnConnect.Enabled = False

			'history player
			cboRate.SelectedIndex = 2
			mTimer = New System.Timers.Timer
			mTimer.Interval = 500
			mTimer.AutoReset = False
			mTimer.Enabled = True



        Catch ex As Exception
            MessageBox.Show(ex.Message, "Form Load Error")
        End Try
    End Sub

    Private Sub LoadColors()
        Dim en As System.Enum = New KnownColor
        Dim aColorName As String 'set a flag for when the system colors end.
        Dim blnStart As Boolean = False
        For Each aColorName In en.GetNames(en.GetType)
            If blnStart Then
                cboTagColor.Items.Add(aColorName) 'end of the system colors. 
                cboTrigColor.Items.Add(aColorName)
            End If
            If aColorName = "Transparent" Then
                blnStart = True
            End If
        Next
        cboTagColor.SelectedItem = "Blue"
        cboTrigColor.SelectedItem = "Red"

    End Sub
#End Region

#Region "RTLS Tag Data and Events"

	Private Sub mStream_Connection(ByVal sender As Object, ByVal e As Parco.StreamConnectionEventArgs) Handles mStream.Connection
		Try
			If e.State = ConnectionState.Connected Then
				btnConnect.Enabled = False
				btnDisConnect.Enabled = True
			ElseIf e.State = ConnectionState.Disconnected Then

				Reset()

			End If
			txtMsg.Text = "Data Stream is " & e.State.ToString

			'MessageBox.Show("Stream is " & State.ToString, "Stream Connection Event", MessageBoxButtons.OK, MessageBoxIcon.Information)
		Catch ex As Exception
			MessageBox.Show(ex.ToString, "Stream Connection Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
		End Try
	End Sub

	Private Sub Reset()
		btnConnect.Enabled = True
		btnDisConnect.Enabled = False
		'now kill all of our dear little tags
		mTags = New Parco.TagCollection

		cboTags.Items.Clear()
		cboTags.SelectedIndex = -1
		mTagTriggers = New Parco.TriggerCollection
		'now redraw the floor with no tags
		picFloor.Invalidate()
		btnLoadRes.Enabled = True

	End Sub

	Private Sub mStream_Response(ByVal sender As Object, ByVal e As Parco.StreamResponseEventArgs) Handles mStream.Response
		Try
			If e.Response.Message <> String.Empty Then
				'the resource had a problem with the request, it may not be a full stream resource
				MessageBox.Show("Request " & e.Response.ReqID & "denied:" & e.Response.Message, "Stream Response Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
			Else
				If e.Response.ResponseType = ParcoMsg.ResponseType.BeginStream Then
					txtMsg.Text = "Receiving Fullstream data..."
				ElseIf e.Response.ResponseType = ParcoMsg.ResponseType.EndStream Then
					txtMsg.Text = "Tag stream closed."
				End If
			End If
		Catch ex As Exception
			MessageBox.Show(ex.ToString, "Stream Response Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
		End Try
	End Sub

	Private Sub mStream_Stream(ByVal sender As Object, ByVal e As Parco.StreamDataEventArgs) Handles mStream.Stream
		Try
			'Since we are running in full stream mode, we need to see if our Tags collection
			'has this tag in it. If not then add it so it will be drawn.
			If mTags.ContainsKey(e.Tag.ID) = False Then
				mTags.Add(e.Tag.ID, e.Tag)
				'and add it to the combobox
				cboTags.Items.Add(e.Tag.ID.ToString)
			End If

			'Do we need to move any Tag triggers to the new tag position?
			If mTagTriggers.Count > 0 Then
				Dim dt As Trigger
				If mTagTriggers.ContainsKey(e.Tag.ID) Then
					dt = mTagTriggers.Item(e.Tag.ID)
					'dt.MoveTo(oTag.X, oTag.Y, oTag.Z)
					dt.Regions.Item(0).MoveTo(e.Tag.X, e.Tag.Y, e.Tag.Z)
				End If
			End If

			'now update the position of the device in our collection so that it may be drawn in the new spot.
			With mTags.Item(e.Tag.ID)
				.X = e.Tag.X
				.Y = e.Tag.Y
				.Z = e.Tag.Z
			End With

			'Check the all of the Tag Triggers
			If mTagTriggers.Count > 0 Then
				Dim t As Trigger
				Dim td As Trigger
				'I am using the trigger.id property to correlate the Device Trigger to a Device.

				For Each t In mTagTriggers
					'do not check a tag against it's own trigger....
					If e.Tag.ID = t.Name Then
						'8.2.2005 if our device trigger has moved then check it against all other devices
						td = t
					Else
						t.CheckTrigger(e.Tag)
					End If
				Next
				If Not td Is Nothing Then
					'8.2.2005 our device trigger may have moved into another device
					Dim tg As Parco.Tag
					For Each tg In mTags
						If tg.ID <> td.Name Then
							td.CheckTrigger(tg)
						End If
					Next
				End If
			End If

			'Check the device against all of our stationary triggers.
			If mTriggers.Count > 0 Then
				Dim t As Trigger
				For Each t In mTriggers
					t.CheckTrigger(e.Tag)
				Next
			End If
			'Show the incoming data in a listbox
			WriteToList(e.Tag)
			'let the GUI update timer know that we need to update the picture
			mbNeedsUpdate = True

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

	Private Overloads Sub WriteToList(ByVal tag As Parco.Tag)
		'lstData.BeginUpdate()
		If tbTriggers.SelectedTab.Name = "tabTagData" Then
			If lstData.Items.Count >= 8 Then
				lstData.Items.RemoveAt(7)
				lstData.Items.Insert(0, "Tag " & tag.ID & " " & tag.Point3D.ToString)
			Else
				lstData.Items.Insert(0, "Tag " & tag.ID & " " & tag.Point3D.ToString)

			End If
		End If
		' lstData.EndUpdate()
	End Sub

	Private Overloads Sub WriteToList(ByVal hb As Parco.ParcoMsg.HeartBeat)
		If tbTriggers.SelectedTab.Name = "tabTagData" Then
			If lstData.Items.Count >= 8 Then
				lstData.Items.RemoveAt(7)
				lstData.Items.Insert(0, "HeartBeat " & hb.Ticks.ToString)
			Else
				lstData.Items.Insert(0, "HeartBeat " & hb.Ticks.ToString)

			End If
		End If
	End Sub
#End Region

#Region "Drawing and Mouse Events"

    Private Sub picFloor_Paint(ByVal sender As Object, ByVal e As System.Windows.Forms.PaintEventArgs) Handles picFloor.Paint
		Try
			Dim pMin As Point3D
			Dim pMax As Point3D
			Dim x, y, width, height As Single
			Dim tag As Parco.Tag
			Dim sb As New System.Text.StringBuilder
			'Here we are using GDI+ to draw our triggers and tags on top of the picture box containing the map
			'This event is raised when the picture boxes invalidate method is called for any reason(by us or the OS)
			If mTriggers.Count > 0 Then
				Dim t As Trigger
				Dim r As Region3D

				'draw any stationary trigger outlines
				For Each t In mTriggers
					sb.Remove(0, sb.Length)
					r = t.Regions.Item(0)
					pMin = ToPixels(r.Xmin, r.Ymin, picFloor.Height)
					pMax = ToPixels(r.XMax, r.YMax, picFloor.Height)
					'we need to swap the y's here because pixels are inverted from our lowerleft coordinate system.
					x = pMin.X
					y = pMax.Y
					width = pMax.X - pMin.X
					height = pMin.Y - pMax.Y
					e.Graphics.DrawRectangle(mTrigPen, x, y, width, height)
					With sb
						.Append(t.Name)
						.Append(" (Top,Btm)=")
						.Append(r.ZTop)
						.Append(",")
						.Append(r.ZBottom)
					End With
					e.Graphics.DrawString(sb.ToString, mFont, mBrush, x + 2, y + 2)
				Next
			End If


			If mTags.Count > 0 Then
				'draw any tags and their id stamps
				e.Graphics.SmoothingMode = Drawing2D.SmoothingMode.HighQuality
				mTagPen.Color = mTagColor
				mTagBrush.Color = mTagColor
				For Each tag In mTags
					'reuse a Parco.point3D instance instead of instantiating a new one..
					pMin = ToPixels(tag.X, tag.Y, picFloor.Height)
					e.Graphics.DrawString(tag.ID.ToString, mFont, mTagBrush, pMin.X + (mnTagSize / 2), pMin.Y - 7)
					'for rectangular tags use the next line.
					'e.Graphics.FillRectangle(mTagBrush, pMin.X - (mnTagSize / 2), pMin.Y - (mnTagSize / 2), mnTagSize, mnTagSize)
					e.Graphics.FillEllipse(mTagBrush, pMin.X - (mnTagSize / 2), pMin.Y - (mnTagSize / 2), mnTagSize, mnTagSize)
				Next

				'Since we have tags, now check for tag triggers
				If mTagTriggers.Count > 0 Then
					Dim dt As Trigger
					Dim rg As Region3D
					Dim verts() As Point3D
					Dim i As Integer
					Dim pt As Point3D
					'each trigger is an octogon with 8 vertices (0 - 7)
					Dim points(7) As System.Drawing.PointF
					For Each dt In mTagTriggers
						'I added the each tag trigger region to collection with a key of 0
						rg = dt.Regions.Item(0)
						verts = rg.Vertices3D
						For i = 0 To 7
							'convert from real coordinates to drawing(pixel) coordinates
							pt = ToPixels(verts(i).X, verts(i).Y, picFloor.Height)
							points(i) = New PointF(pt.X, pt.Y)
						Next
						e.Graphics.DrawPolygon(Pens.Red, points)
					Next
				End If
			End If
			sb = Nothing

		Catch ex As Exception
			MessageBox.Show(ex.ToString, "Map Paint Error", MessageBoxButtons.OK)
		End Try
    End Sub



    Private Sub picFloor_MouseDown(ByVal sender As Object, ByVal e As System.Windows.Forms.MouseEventArgs) Handles picFloor.MouseDown
        mXStart = e.X
        mYStart = e.Y
        'lstEvt.Items.Add("Pixels " & e.X.ToString & ", " & e.Y.ToString)
        'Dim p As Point2D = ToReal(e.X, e.Y, picFloor.Height)
        'lstEvt.Items.Add("MouseDown " & p.ToString)
        'Dim p2 As Point2D = ToPixels(p.X, p.Y, picFloor.Height)
        'lstEvt.Items.Add("CalcPixels = :" & p2.ToString)
    End Sub

    Private Sub picFloor_MouseUp(ByVal sender As Object, ByVal e As System.Windows.Forms.MouseEventArgs) Handles picFloor.MouseUp
        ' lstEvt.Items.Add("MouseUp " & e.X.ToString & ", " & e.Y.ToString)
        Try

            If mbAddingTrigger Then
                SyncLock mSynchLock
                    Dim t As Trigger = MouseDragTrigger(mXStart, mYStart, e.X, e.Y, picFloor.Height)
					'use the index of the triggerlist for the id....
                    If Not t Is Nothing Then
						t.I_TRG = lstTriggers.Items.Add(t.Name)
						mTriggers.Add(t.I_TRG, t)
                        AddHandler t.TriggerEvent, AddressOf Trigger_TriggerEvent
                    End If

                    btnTrigDel.Enabled = True
                    mbAddingTrigger = False
                End SyncLock
                picFloor.Invalidate()
            End If

        Catch ex As Exception
            MessageBox.Show(ex.ToString, "Mouse up error", MessageBoxButtons.OK)
            mbAddingTrigger = False
        End Try

    End Sub

    Private Sub picFloor_MouseMove(ByVal sender As Object, ByVal e As System.Windows.Forms.MouseEventArgs) Handles picFloor.MouseMove
        Try
            If mbAddingTrigger Then
                Dim p3d As Point3D = ToReal(e.X, e.Y, picFloor.Height)
                txtPos.Text = p3d.X.ToString & ", " & p3d.Y.ToString
                p3d = Nothing
            End If
        Catch ex As Exception
            MessageBox.Show(ex.Message, "Mouse Move Error")
        End Try
    End Sub

    Private Sub picFloor_MouseLeave(ByVal sender As Object, ByVal e As System.EventArgs) Handles picFloor.MouseLeave
        txtPos.Text = String.Empty
    End Sub
#End Region

#Region "Trigger creation and helper methods"


    Private Function ToReal(ByVal Xpixels As Single, ByVal Ypixels As Single, ByVal picHieght As Integer) As Point3D
        'apply scaling factors
        'x is ok, y needs to be 'inverted' by subtracting its value from the pictureboxes height 
        Dim x As Single = CType(Math.Round(Xpixels * mXScale, 1), Single)
        Dim y As Single = CType(Math.Round((picHieght - Ypixels) * mYScale, 1), Single)
        Dim p As New Parco.Point3D(x, y, 0)
        Return p
    End Function

    Private Function ToPixels(ByVal Xreal As Single, ByVal Yreal As Single, ByVal picHieght As Integer) As Point3D
        'x is ok, y need to 'univerted' by subtracting the pixel value from the pictureboxes height
        Dim x As Single = CType(Math.Round(Xreal / mXScale, 1), Single)
        Dim y As Single = CType(Math.Round(picHieght - (Yreal / mYScale), 1), Single)

        Dim p As New Parco.Point3D(x, y, 0)
        Return p
    End Function

    Private Function MouseDragTrigger(ByVal xStart As Single, ByVal yStart As Single, ByVal xEnd As Single, ByVal yEnd As Single, ByVal PixelHeight As Integer) As Trigger
        Dim x As Single
        Dim x2 As Single
        Dim y As Single
        Dim y2 As Single
        Dim h As Integer = PixelHeight
        'check for a drag that does not produce a rectangular area
        Select Case True
            Case xStart = xEnd
                Return Nothing
            Case yStart = yEnd
                Return Nothing
        End Select

        If xStart < xEnd Then
            x = xStart
            x2 = xEnd
        Else
            x2 = xStart
            x = xEnd
        End If
        'remember, y is inverse here, we will correct it in a sec....
        If yStart > yEnd Then
            y = yStart
            y2 = yEnd
        Else
            y2 = yStart
            y = yEnd
        End If
        Debug.WriteLine("params:x=" & x.ToString & " x2=" & x2.ToString & " y=" & y.ToString & " y2=" & y2.ToString)

        'points x,y then x,y2 then x2,y2 then x2,y to define the shape
        Dim verts() As Parco.Point3D = New Point3D(3) {}

        verts(0) = ToReal(x, y, h)
		verts(0).N_ORD = 0
        'Debug.WriteLine("verts(0)=" & verts(0).ToString)
        verts(1) = ToReal(x, y2, h)
		verts(1).N_ORD = 1
        'Debug.WriteLine("verts(1)=" & verts(1).ToString)
        verts(2) = ToReal(x2, y2, h)
		verts(2).N_ORD = 2
        'Debug.WriteLine("verts(2)=" & verts(2).ToString)
        verts(3) = ToReal(x2, y, h)
		verts(3).N_ORD = 3
        'Debug.WriteLine("verts(3)=" & verts(3).ToString)

		Dim r As New Region3D
		'give the region id a value of zero since it did not originate from the database
		r.I_RGN = 0
        r.Vertices3D = verts
        'set our trigger Elevations
        r.ZBottom = CType(txtTrigBottom.Text, Single)
        r.ZTop = CType(txtTrigTop.Text, Single)

        'Quick and dirty- our trigger directions are a value of 1 + the selected index of the combobox. 
        Dim enm As Trigger.Directions
        enm = CType(CType(cboTrigDir.SelectedIndex, Integer) + 1, Trigger.Directions)
		Dim t As New Trigger(-1, txtTrigName.Text, enm)
		t.RaiseEventOnFirstEncounter = False

        'add the region to the trigger's region collection
		t.Regions.Add(r.I_RGN, r)
		t.Validate()
        txtInstruction.Text = msNewMsg
        Return t

    End Function

	Private Function TagTrigger(ByVal t As Tag, ByVal radius As Single) As Trigger
		Dim r As Double = CType(radius, Double)
		Dim nLeg As Single = CType(Math.Sqrt(r * r / 2), Single)

		Dim pt As Point3D

		'check for a drag that produces something more than a point
		Select Case True
			Case radius <= 0
				Return Nothing
		End Select


		'create an octogon with the vertices on 90 and 45....
		Dim verts() As Parco.Point3D = New Point3D(7) {}

		verts(0) = New Point3D(t.X, t.Y - radius, 0)
		verts(0).N_ORD = 0

		verts(1) = New Point3D(t.X - nLeg, t.Y - nLeg, 0)
		verts(1).N_ORD = 1
		'Debug.WriteLine("verts(1)=" & verts(1).ToString)
		verts(2) = New Point3D(t.X - radius, t.Y, 0)
		verts(2).N_ORD = 2
		'Debug.WriteLine("verts(2)=" & verts(2).ToString)
		verts(3) = New Point3D(t.X - nLeg, t.Y + nLeg, 0)
		verts(3).N_ORD = 3
		'Debug.WriteLine("verts(3)=" & verts(3).ToString)

		verts(4) = New Point3D(t.X, t.Y + radius, 0)
		verts(4).N_ORD = 4

		verts(5) = New Point3D(t.X + nLeg, t.Y + nLeg, 0)
		verts(5).N_ORD = 5

		verts(6) = New Point3D(t.X + radius, t.Y, 0)
		verts(6).N_ORD = 6

		verts(7) = New Point3D(t.X + nLeg, t.Y - nLeg, 0)
		verts(7).N_ORD = 7


		Dim rg As New Region3D
		'I am arbitrarily seting the region id to 0 and using it as the regioncollection key
		rg.I_RGN = 0
		rg.Vertices3D = verts
		'set the top and bottom elevations for the trigger
		rg.ZBottom = CType(txtTagBottom.Text, Single)
		rg.ZTop = CType(txtTagTop.Text, Single)

		'Quick and dirty: our trigger directions are a value of 1 + the selected index. 
		Dim enm As Trigger.Directions
		enm = CType(CType(cboTagDir.SelectedIndex, Integer) + 1, Trigger.Directions)
		'The ID corresponds to the AutoNumber id generated by the Parco RTLS database, use -1 here
		'and use the name property for the "key" in our hashtable
		Dim trg As New Trigger(-1, t.ID, enm)

		'add the region to the trigger's region collection
		trg.Regions.Add(rg.I_RGN, rg)
		trg.Validate()
		'txtInstruction.Text = msNewMsg
		Return trg

	End Function


#End Region

#Region "Trigger Events"


	Private Sub Trigger_TriggerEvent(ByVal sender As Object, ByVal e As StreamDataEventArgs)
		Try
			Dim t As Trigger = CType(sender, Trigger)
			'remove old items from the trigger event list.
			If lstEvt.Items.Count >= 18 Then
				lstEvt.Items.RemoveAt(17)
			End If
			'create our message to add to the list.
			Dim sb As New System.Text.StringBuilder
			With sb
				.Append(t.Name)
				.Append(" reports ")
				.Append(t.Direction.ToString)
				.Append(": Tag ")
				.Append(e.Tag.ID)
				.Append(" @ ")
				.Append(Date.Now.ToLongTimeString)
			End With
			'Insert a new item to list
			lstEvt.Items.Insert(0, sb.ToString)
			sb = Nothing

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Trig Event Error")
		End Try
	End Sub
#End Region

#Region "Form button and control handlers"

    Private Sub btnConnect_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnConnect.Click
        Try
            If rbParco.Checked Then
                mData = New Parco.Data(msParcoWebSvc)
            Else
                mData = New Parco.Data(msLocalWebSvc)
            End If
            txtMsg.Text = "Retreiving IP and Port ...."
            'Get an IP and port to connect to a full stream resource ( type 1 as shipped in the database)
            Dim ds As DataSet = mData.ResourceSelect(CType(cboResourses.SelectedValue, Integer))
            With ds.Tables(0).Rows(0)
                msProviderIP = .Item("X_IP").ToString
                mPort = CType(.Item("I_PRT"), Integer)
            End With
            'create our connection and get data. This code is for connection to a full stream resource
            'i.e. all device available device data is returned
			mStream = New Parco.DataStream(msProviderIP, mPort)
			'mStream = New Parco.DataStream("216.204.151.91", 10005)
            txtMsg.Text = "Connecting to the Manager ...."
            mStream.Connect()
            'create the begin stream request for the fullstream resource in the Stream connected event
            Dim req As New Parco.ParcoMsg.Request(ParcoMsg.RequestType.BeginStream, "myReqID")
            txtMsg.Text = "Sending the BeginStream request ...."
            mStream.SendRequest(req)

            'now all that is left to do is wait for a response from the stream in its Response event.

        Catch ex As Exception
            MessageBox.Show(ex.ToString, "Connect Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
            txtMsg.Text = "Server Connection Failed."
        End Try
    End Sub

    Private Sub btnDisconnect_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnDisConnect.Click
        Try
            CloseStream()
        Catch ex As Exception
            MessageBox.Show(ex.ToString, "Disconnect Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub


    Private Sub btnTrigNew_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTrigNew.Click
        Try
            If txtTrigName.Text = String.Empty Then
                MessageBox.Show("Please enter a trigger name.", "Name Required", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
                txtTrigName.Focus()
                Return
            End If
            If cboTrigDir.SelectedIndex = -1 Then
                MessageBox.Show("Please select a trigger direction.", "Direction Required", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
                cboTrigDir.Focus()
                Return
            End If
            If IsNumeric(txtTrigTop.Text) = False Then
                MessageBox.Show("Please enter a numeric Top Elevation.", "Top Elevation Required", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
                txtTrigTop.Focus()
                Return
            End If
            If IsNumeric(txtTrigBottom.Text) = False Then
                MessageBox.Show("Please enter a numeric Bottom Elevation.", "Bottom Elevation Required", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
                txtTrigBottom.Focus()
                Return
            End If
            If CType(txtTrigTop.Text, Single) <= CType(txtTrigBottom.Text, Single) Then
                MessageBox.Show("The Top Elevation must be greater then the Bottom Elevation.", "Invalid Elevations", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
                txtTrigTop.Focus()
                Return
            End If

            mbAddingTrigger = True
            txtInstruction.Text = "Now click and drag on the floor plan.."

        Catch ex As Exception
            MessageBox.Show(ex.Message, "Trig New Error")
        End Try
    End Sub
    Private Sub btnTrigDel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTrigDel.Click
        Try
            If lstTriggers.SelectedIndex <> -1 Then
                Dim id As Integer = lstTriggers.SelectedIndex
				mTriggers.Remove(id)
                lstTriggers.Items.RemoveAt(id)
				mbNeedsUpdate = True
            End If
        Catch ex As Exception
            MessageBox.Show(ex.Message, "Trig Delete Error")
        End Try
    End Sub



    Private Sub cboTagSize_SelectedIndexChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles cboTagSize.SelectedIndexChanged
        Try
            If cboTagSize.SelectedIndex <> -1 Then
				mnTagSize = CType(cboTagSize.SelectedItem, Single)
				mbNeedsUpdate = True
            End If
        Catch ex As Exception
            MessageBox.Show(ex.Message, "Tag Resize Error")
        End Try
    End Sub

    Private Sub cboTagColor_SelectedIndexChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles cboTagColor.SelectedIndexChanged
        Try
            If cboTagColor.SelectedIndex <> -1 Then
				mTagColor = Color.FromName(cboTagColor.SelectedItem.ToString)
				mbNeedsUpdate = True
            End If

        Catch ex As Exception
            MessageBox.Show(ex.Message, "Tag Color Error")
        End Try
    End Sub

    Private Sub cboTrigColor_SelectedIndexChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles cboTrigColor.SelectedIndexChanged
        Try
            If cboTrigColor.SelectedIndex <> -1 Then
                mTrigPen.Color = Color.FromName(cboTrigColor.SelectedItem.ToString)
                mBrush.Color = Color.FromName(cboTrigColor.SelectedItem.ToString)
				mbNeedsUpdate = True
            End If

        Catch ex As Exception
            MessageBox.Show(ex.Message, "Tirgger Color Error")
        End Try
    End Sub

    Private Sub btnTagTrigger_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTagTrigger.Click
        Dim t As Trigger
        Dim msg As String
        Dim ctl As Control
        Try
            Select Case True
                Case cboTags.SelectedIndex = -1
                    msg = "Please select a Tag."
                    ctl = cboTags
                Case cboRadius.SelectedIndex = -1
                    msg = "Please select a Radius."
                    ctl = cboRadius
                Case cboTagDir.SelectedIndex = -1
                    msg = "Please select a direction."
                    ctl = cboTagDir
                Case IsNumeric(txtTagTop.Text) = False
                    msg = "Please enter a numeric Top Elevation."
                    ctl = txtTagTop
                Case IsNumeric(txtTagBottom.Text) = False
                    msg = "Please enter a numeric Bottom Elevation."
                    ctl = txtTagBottom
                Case CType(txtTagTop.Text, Single) <= CType(txtTagBottom.Text, Single)
                    msg = "The Top Elevation must be greater then the Bottom Elevation"
                    ctl = txtTagTop
            End Select
            If msg <> String.Empty Then
                MessageBox.Show(msg, "Invalid Tag Trigger Parameter", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
                ctl.Focus()
                Return
            Else
				'lets see if we already have a trigger for the tag since we only want one per device for this demo.....
				If mTagTriggers.ContainsKey(cboTags.SelectedItem.ToString) = False Then
					'create a new trigger
					t = TagTrigger(mTags.Item(cboTags.SelectedItem.ToString), CType(cboRadius.SelectedItem, Single))
					If Not t Is Nothing Then
						'hook up our event handler
						AddHandler t.TriggerEvent, AddressOf Trigger_TriggerEvent
						'and add it to our collection
						'use the tag.ID as the key for the trigger's key
						mTagTriggers.Add(cboTags.SelectedItem.ToString, t)
					End If
				End If
            End If

			mbNeedsUpdate = True


        Catch ex As Exception
            MessageBox.Show(ex.Message, "Tag Trigger Error")
        End Try
    End Sub

    Private Sub btnTagTrigDelete_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTagTrigDelete.Click
        Try
            If cboTags.SelectedIndex <> -1 Then
				mTagTriggers.Remove(cboTags.SelectedItem.ToString)
				mbNeedsUpdate = True
            End If
        Catch ex As Exception
            'MessageBox.Show(ex.Message, "Tag Delete Trigger Error")
        End Try
    End Sub

    Private Sub linkClear_LinkClicked(ByVal sender As System.Object, ByVal e As System.Windows.Forms.LinkLabelLinkClickedEventArgs) Handles linkClear.LinkClicked
        lstEvt.Items.Clear()
    End Sub

#End Region


	Private Sub btnLoadRes_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnLoadRes.Click
		Try
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

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Load Resources Error")
		End Try

	End Sub

#Region "History Player"


	Private Sub btnLoad_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnLoad.Click
		Try
			mHistory = New Parco.History
			mHistory.BeginDateUTC = dtpStart.Value.ToUniversalTime
			mHistory.EndDateUTC = dtpEnd.Value.ToUniversalTime
			mHistory.PlayRate = CType(cboRate.SelectedItem.ToString, Single)

			If rbParco.Checked Then
				mHistory.Data = New Parco.Data(msParcoWebSvc)
			Else
				mHistory.Data = New Parco.Data(msLocalWebSvc)
			End If

			If txtDevID.Text <> String.Empty Then
				Dim delim As String = ","
				Dim s() As String = txtDevID.Text.Split(delim.ToCharArray())
				Dim i As Integer = 0
				Dim tgs As New Parco.TagCollection

				For i = 0 To s.Length - 1
					Dim t As New Parco.Tag(s(i))
					tgs.Add(t.ID, t)
				Next

				mHistory.Tags = tgs
				mHistory.Load()
			Else
				MessageBox.Show("At least one tag required." & vbCrLf & vbCrLf & "Enter one tag like 00000EEC or a comma delimited list", "Tag Required", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
			End If

		Catch ex As Exception
			MessageBox.Show(ex.Message, "Load History Error")
		End Try
	End Sub

	Private Sub mHistory_Done(ByVal sender As Object, ByVal e As System.EventArgs) Handles mHistory.Done
		Dim i As Integer = lstHist.Items.Add("History Player Done")
		lstHist.SelectedIndex = i

		cboRate.Enabled = True
		btnPlay.Enabled = False
		btnPause.Enabled = False
		btnStop.Enabled = False

	End Sub

	Private Sub mHistory_HistoryData(ByVal sender As Object, ByVal e As Parco.StreamDataEventArgs) Handles mHistory.HistoryData
		'Use the code in our stream event handler to display the history records
		' - or add a handler to the event. If we did this we would need to check to see
		'who the sender is and then update our history list in the stream event.
		mStream_Stream(mHistory, e)
		'and add some info to the listbox for user feedback
		Dim i As Integer = lstHist.Items.Add("tag id=" & e.Tag.ID & " time=" & e.Tag.TimeStampUTC.ToLocalTime.ToString)
		lstHist.SelectedIndex = i

	End Sub

	Private Sub mHistory_OnLoad(ByVal sender As Object, ByVal e As Parco.HistoryOnLoadEventArgs) Handles mHistory.OnLoad
		'this event fires after the Load sub is called. It is called Asynchronusly
		'when the history player instance receives the data from the database.
		Dim i As Integer = lstHist.Items.Add("History Player Loaded with " & e.RecordCount.ToString & " records")
		lstHist.SelectedIndex = i

		'if we have records, let the user use the play button
		If e.RecordCount >= 0 Then
			btnPlay.Enabled = True
			btnPause.Enabled = False
			btnStop.Enabled = False
		End If
	End Sub

	Private Sub btnPlay_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnPlay.Click
		Try
			mHistory.PlayRate = CType(cboRate.SelectedItem.ToString, Single)
			mHistory.Play()
			btnPlay.Enabled = False
			btnPause.Enabled = True
			btnStop.Enabled = True
			cboRate.Enabled = False
			Dim i As Integer = lstHist.Items.Add("Playing...")
			lstHist.SelectedIndex = i



		Catch ex As Exception
			MessageBox.Show(ex.Message, "History Play Error")
		End Try
	End Sub

	Private Sub btnPause_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnPause.Click
		Try
			mHistory.Pause()
			btnPlay.Enabled = True
			btnPause.Enabled = False
			Dim i As Integer = lstHist.Items.Add("Paused...")
			lstHist.SelectedIndex = i

		Catch ex As Exception
			MessageBox.Show(ex.Message, "History Pause Error")
		End Try
	End Sub

	Private Sub btnStop_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnStop.Click
		Try
			mHistory.Quit()
			btnPlay.Enabled = True
			btnPause.Enabled = False
			btnStop.Enabled = False
			cboRate.Enabled = True

		Catch ex As Exception
			MessageBox.Show(ex.Message, "History Pause Error")
		End Try
	End Sub
#End Region

	Private Sub cboRate_SelectedIndexChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles cboRate.SelectedIndexChanged

	End Sub

	Private Sub LinkLabel1_LinkClicked(ByVal sender As System.Object, ByVal e As System.Windows.Forms.LinkLabelLinkClickedEventArgs) Handles LinkLabel1.LinkClicked
		lstHist.Items.Clear()
	End Sub

	Private Sub mTimer_Elapsed(ByVal sender As Object, ByVal e As System.Timers.ElapsedEventArgs) Handles mTimer.Elapsed
		Try
			'now redraw our picture box by invalidating it....
			If mbNeedsUpdate Then
				picFloor.Invalidate()
			End If
		Finally
			mbNeedsUpdate = False
			mTimer.Interval = 500
		End Try
	End Sub

	Private Sub mStream_HeartBeat(ByVal sender As Object, ByVal e As Parco.StreamHeartbeatEventArgs) Handles mStream.HeartBeat
		Try
			WriteToList(e.HeartBeat)
		Catch ex As Exception

		End Try
	End Sub

    Private Sub ContextMenu1_Popup(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ContextMenu1.Popup
        Try
            If lstData.SelectedItem Is Nothing Then
                mnuCopyTag.Enabled = False
            Else
                mnuCopyTag.Enabled = True
            End If
        Catch ex As Exception
            MessageBox.Show(ex.ToString, "Context Popup", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)

        End Try
    End Sub

    Private Sub mnuCopyTag_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles mnuCopyTag.Click
        Try
            If Not lstData.SelectedItem Is Nothing Then
                Dim s As String = lstData.SelectedItem.ToString
                Dim iStart, iEnd As Integer
                iStart = s.IndexOf(" ")
                iEnd = s.IndexOf("(")
                Dim t As String = s.Substring(iStart + 1, iEnd - iStart - 2)
                Clipboard.SetDataObject(t)

                'tag 000005678 (x,y,z)
            End If
        Catch ex As Exception
            MessageBox.Show(ex.ToString, "Copy Tag Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
        End Try
    End Sub
End Class
