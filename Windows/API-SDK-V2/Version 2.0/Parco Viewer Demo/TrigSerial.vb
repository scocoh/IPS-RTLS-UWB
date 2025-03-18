'##### CONFIDENTIAL - CONFIDENTIAL - CONFIDENTIAL ######
'		                    Parco RTLS™ System
'All information and source code contained herein is confidential and proprietary.
'Copying or modifying this source code is strictly prohibited unless under license of Parco Wireless.
'Copyright © 2001-2005 Parco Merged Media Inc. / Parco Wireless
'All rights reserved.
'##### CONFIDENTIAL - CONFIDENTIAL - CONFIDENTIAL ######
'Author:     Michael Farnsworth, Standard I-O Inc.
'Version:   1.0
'Date:       2/01/2005
'
'Modification/Author/Date:

'Hold the values necessary to recreate a tag
<Serializable()> _
Public Class TrigSerial
	Private mDir As Parco.Trigger.Directions
	Private mXmax As Single
	Private mXmin As Single
	Private mYMax As Single
	Private mYMin As Single
	Private mZTop As Single
	Private mZBot As Single
	Private mID As String
	Private mName As String
	Private mColor As System.Drawing.Color
	Sub New()

	End Sub
	Sub New(ByVal sName As String, ByVal sID As String, ByVal fXmax As Single, ByVal fXMin As Single, ByVal fYMax As Single, ByVal fYMin As Single, ByVal fZtop As Single, ByVal fZBot As Single, ByVal eDir As Parco.Trigger.Directions, ByVal clr As System.Drawing.Color)
		mName = sName
		mID = sID
		mXmax = fXmax
		mXmin = fXMin
		mYMax = fYMax
		mYMin = fYMin
		mZTop = fZtop
		mZBot = fZBot
		mDir = eDir
		mColor = clr
	End Sub
	Public Property Direction() As Parco.Trigger.Directions
		Get
			Return mDir
		End Get
		Set(ByVal Value As Parco.Trigger.Directions)
			mDir = Value
		End Set
	End Property
	Public Property XMax() As Single
		Get
			Return mXmax
		End Get
		Set(ByVal Value As Single)
			mXmax = Value
		End Set
	End Property
	Public Property XMin() As Single
		Get
			Return mXmin
		End Get
		Set(ByVal Value As Single)
			mXmin = Value
		End Set
	End Property
	Public Property YMax() As Single
		Get
			Return mYMax
		End Get
		Set(ByVal Value As Single)
			mYMax = Value
		End Set
	End Property
	Public Property YMin() As Single
		Get
			Return mYMin
		End Get
		Set(ByVal Value As Single)
			mYMin = Value
		End Set
	End Property

	Public Property ZTop() As Single
		Get
			Return mZTop
		End Get
		Set(ByVal Value As Single)
			mZTop = Value
		End Set
	End Property
	Public Property ZBottom() As Single
		Get
			Return mZBot
		End Get
		Set(ByVal Value As Single)
			mZBot = Value
		End Set
	End Property
	Public Property ID() As String
		Get
			Return mID
		End Get
		Set(ByVal Value As String)
			mID = Value
		End Set
	End Property
	Public Property Name() As String
		Get
			Return mName
		End Get
		Set(ByVal Value As String)
			mName = Value
		End Set
	End Property
	Public Property Color() As System.Drawing.Color
		Get
			Return mColor
		End Get
		Set(ByVal Value As System.Drawing.Color)
			mColor = Value
		End Set
	End Property
End Class


