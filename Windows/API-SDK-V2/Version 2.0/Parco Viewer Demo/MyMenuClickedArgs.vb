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


Public Class MyMenuClickedArgs
	Inherits System.EventArgs

	Private mTagKey As Object

	Public Property TagKey() As Object
		Get
			Return mTagKey
		End Get
		Set(ByVal Value As Object)
			mTagKey = Value
		End Set
	End Property
End Class
