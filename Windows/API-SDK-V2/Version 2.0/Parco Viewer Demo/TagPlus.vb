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


'Note: we are using th tostring method to specify images. 
'The viewer image keys are case sensitive, hence the 
'text must exactly match the viewer's image key text.
Public Enum TagImages As Integer
	None = -1
	Patient = 0
	Doctor = 1
	Nurse = 2
	Wheelchair = 3
	IV = 4
	Monitor = 5
	Microscope = 6
	Redcross = 7
	Heartbeat = 8
	Xray = 9
	Thermometer = 10
	Globe = 11

End Enum

'This class extends the viewer tag class for easy databinding to lists
Friend Class TagPlus
	Inherits SIO3DViewer.Tag

	Private mID As String
	Private mName As String
	Private mImage As TagImages	'the emumerated constant for our image
	Private mfHeight As Single	'needed because I could not seem to get at a tags size property
	Private mfWidth As Single	'needed because I could not seem to get at a tags size property


	Sub New(ByVal ImageKey As Object, ByVal selImageKey As Object, ByVal fWidth As Single, ByVal fHeight As Single, ByVal offsetX As Single, _
	ByVal offsetY As Single, ByVal offsetZ As Single, ByVal cTag As System.Drawing.Color, ByVal cFloor As System.Drawing.Color)
		MyBase.New(ImageKey, selImageKey, fWidth, fHeight, offsetX, offsetY, offsetZ, cTag, cFloor)

	End Sub

	Public Property Name() As String
		Get
			Return mName
		End Get
		Set(ByVal Value As String)
			mName = Value
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

	Public Property ImageEnum() As TagImages
		Get
			Return mImage
		End Get
		Set(ByVal Value As TagImages)
			mImage = Value
		End Set
	End Property

	Public Property ImageHeight() As Single
		Get
			Return mfHeight
		End Get
		Set(ByVal Value As Single)
			mfHeight = Value
		End Set
	End Property

	Public Property ImageWidth() As Single
		Get
			Return mfWidth
		End Get
		Set(ByVal Value As Single)
			mfWidth = Value
		End Set
	End Property
	Public Overrides Function ToString() As String
		'for use in databinding to a listbox
		Return mID
	End Function

End Class
