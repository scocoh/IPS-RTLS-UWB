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
Public Class TagSerial
	Private eImg As TagImages
	Private fWidth As Single
	Private fHeight As Single
	Private sID As String
	Private sName As String
	Private mChildren As New Hashtable

	Public Property Image() As TagImages
		Get
			Return eImg
		End Get
		Set(ByVal Value As TagImages)
			eImg = Value
		End Set
	End Property
	Public Property Height() As Single
		Get
			Return fHeight
		End Get
		Set(ByVal Value As Single)
			fHeight = Value
		End Set
	End Property
	Public Property Width() As Single
		Get
			Return fWidth
		End Get
		Set(ByVal Value As Single)
			fWidth = Value
		End Set
	End Property

	Public Property ID() As String
		Get
			Return sID
		End Get
		Set(ByVal Value As String)
			sID = Value
		End Set
	End Property
	Public Property Name() As String
		Get
			Return sName
		End Get
		Set(ByVal Value As String)
			sName = Value
		End Set
	End Property

	Public Property Children() As Hashtable
		Get
			Return mChildren
		End Get
		Set(ByVal Value As Hashtable)
			mChildren = Value
		End Set
	End Property

End Class

<Serializable()> _
Public Class ChildSerial
	Private eImg As TagImages
	Private fSize As Single
	Private sData As String
	Public Property Image() As TagImages
		Get
			Return eImg
		End Get
		Set(ByVal Value As TagImages)
			eImg = Value
		End Set
	End Property
	Public Property Size() As Single
		Get
			Return fSize
		End Get
		Set(ByVal Value As Single)
			fSize = Value
		End Set
	End Property
	
	Public Property Data() As String
		Get
			Return sData
		End Get
		Set(ByVal Value As String)
			sData = Value
		End Set
	End Property

End Class
