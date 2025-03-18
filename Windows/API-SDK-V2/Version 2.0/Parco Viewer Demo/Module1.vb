Imports Parco
Imports System.Text
Imports System.Text.RegularExpressions

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

Module Module1

	Friend gTagHieghtDefault As Single = 2
	Friend gTagWidthDefault As Single = 2
	Friend gTagChildSizeDefault As Single = 0.5
	Friend gXOffset As Single
	Friend gYOffset As Single

	Friend Function GetChildSize(ByVal c As SIO3DViewer.TagChild) As Single
		'this code assumes that the child height and width are the same
		Dim radius, fRet As Single
		Dim vect As Microsoft.DirectX.Vector3
		'the radius is not actually a radius, it is the Max of the Hieght or width divided by 2!
		c.GetBoundingSphere(vect, radius)
		fRet = CType((2 * radius), Single)
		Return fRet
	End Function
	Friend Function CreateFigure(ByVal eImage As TagImages, Optional ByVal fWidth As Single = 2, Optional ByVal fHeight As Single = 2, Optional ByVal sID As String = "", Optional ByVal sName As String = "") As TagPlus
		'Dim fWidth As Single = 2
		'Dim fHeight As Single = 2
		Dim offsetX As Single = -fWidth / 2
		Dim offsetY As Single = -fHeight / 2
		Dim offsetZ As Single = 0
		Dim t As New TagPlus(eImage.ToString, "floor unselected", fWidth, fHeight, offsetX, offsetY, offsetZ, System.Drawing.Color.White, System.Drawing.Color.White)
		'the child UserColor property is the color used to render the figure in the Minimap control
		t.UserColor = Color.Navy

		'You may use a custom business object to contain more diverse data in the Data property  of the tag.
		t.ImageHeight = fHeight
		t.ImageWidth = fWidth
		t.ID = sID
		t.Name = sName
		t.ImageEnum = eImage
		t.Y = fHeight / 2		  'position all tags on the 'belt' of the person

		Return t
	End Function

	Friend Function CreateViewerAreaTrig(ByVal sName As String, ByVal originX As Single, ByVal originY As Single, ByVal originZ As Single, ByVal widthX As Single, ByVal depthZ As Single, ByVal clr As System.Drawing.Color) As SIO3DViewer.ColoredPlane
		'we are working in viewer coordinates here: X is to right, Z into the screen, Y is up
		'Keep the plane just above our floor
		Dim cp As New SIO3DViewer.ColoredPlane(originX, 0.05, originZ, widthX, depthZ, clr)
		Dim ft As Font = New Font("Verdana", 4, FontStyle.Regular, GraphicsUnit.Pixel)
		Dim t As New SIO3DViewer.TextObject(sName, ft, 0.1, 0.1, System.Drawing.Color.Black, 3)
		'rotate the text so we can see it from the side and above
		t.OrientationTransform.RotateX(0.8)
		'move the text to the upper right corner,just off the plane
		t.OrientationTransform.Translate(originX, originY + CType(0.3, Single), originZ)
		cp.Children.Add("text", t)
		'store the color in the data property so we can look it up when serializing triggers.
		cp.Data = clr

		Return cp
	End Function
	Friend Function ToRealCoord(ByVal Xviewer As Single, ByVal Yviewer As Single, ByVal Zviewer As Single) As Point3D
		'Assumes that  the viewer floor is at elevation 0 (no offset)
		Dim p As New Point3D
		p.X = Xviewer - gXOffset
		p.Y = Zviewer - gYOffset
		p.Z = Yviewer

		Return p
	End Function

	Friend Function ToViewerCoord(ByVal Xreal As Single, ByVal Yreal As Single, ByVal Zreal As Single) As Point3D

		Dim p As New Point3D

		'Here is where we make the transition from the parco RTLS system coordinate system to the 3D programming coordinate system.
		'In the 3D programming world X is the same, Y is up and Z is into the monitor.
		'We also need to add the X and Y offsets to compensate for the viewer's 0,0 ref being the middle of the floor.
		'Assumes that  the viewer floor is at elevation 0 (no offset)
		p.X = Xreal + gXOffset
		p.Y = Zreal
		p.Z = Yreal + gYOffset

		Return p
	End Function



	Friend Function TriggerCreate(ByVal xStartReal As Single, ByVal yStartReal As Single, ByVal xEndReal As Single, ByVal yEndReal As Single, _
	  ByVal zStartReal As Single, ByVal zEndReal As Single, ByVal eDir As Trigger.Directions, ByVal sNameKey As String) As Trigger
		Dim x As Single
		Dim x2 As Single
		Dim y As Single
		Dim y2 As Single
		Dim h As Single = zStartReal
		Dim h2 As Single = zEndReal
		'check for a drag that does not produce a rectangular area
		Select Case True
			Case xStartReal = xEndReal
				Return Nothing
			Case yStartReal = yEndReal
				Return Nothing
			Case zStartReal = zEndReal
				Return Nothing
			Case sNameKey = String.Empty
				Return Nothing
		End Select

		If xStartReal < xEndReal Then
			x = xStartReal
			x2 = xEndReal
		Else
			x2 = xStartReal
			x = xEndReal
		End If

		If yStartReal < yEndReal Then
			y = yStartReal
			y2 = yEndReal
		Else
			y2 = yStartReal
			y = yEndReal
		End If
		'Debug.WriteLine("params:x=" & x.ToString & " x2=" & x2.ToString & " y=" & y.ToString & " y2=" & y2.ToString)

		'points x,y then x,y2 then x2,y2 then x2,y to define the shape
		Dim verts() As Parco.Point3D = New Point3D(3) {}

		verts(0) = New Point3D(x, y, h)		'ToReal(x, y, h)
		verts(0).Number = 0
		'Debug.WriteLine("verts(0)=" & verts(0).ToString)
		verts(1) = New Point3D(x, y2, h)		 'ToReal(x, y2, h)
		verts(1).Number = 1
		'Debug.WriteLine("verts(1)=" & verts(1).ToString)
		verts(2) = New Point3D(x2, y2, h)		 'ToReal(x2, y2, h)
		verts(2).Number = 2
		'Debug.WriteLine("verts(2)=" & verts(2).ToString)
		verts(3) = New Point3D(x2, y, h)		 'ToReal(x2, y, h)
		verts(3).Number = 3
		'Debug.WriteLine("verts(3)=" & verts(3).ToString)

		Dim r As New Region3D
		r.ID = 1
		r.Vertices3D = verts
		'set our trigger Elevations
		r.ZBottom = h
		r.ZTop = h2

		Dim t As New Trigger(-1, sNameKey, eDir)
		'add the region to the trigger's region collection
		t.Regions.AddItem(r, r.ID.ToString)
		Return t

	End Function

	Friend Function TagTriggerCreate(ByVal CenterPoint As Point3D, ByVal radius As Single, ByVal zBottom As Single, ByVal zTop As Single, ByVal eDir As Trigger.Directions, ByVal sTrigName As String, ByVal key As Integer) As Trigger
		'Note: all args must in terms of real coordinates and not veiwer coordinates
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

		verts(0) = New Point3D(CenterPoint.X, CenterPoint.Y - radius, 0)
		verts(0).Number = 0

		verts(1) = New Point3D(CenterPoint.X - nLeg, CenterPoint.Y - nLeg, 0)
		verts(1).Number = 1
		'Debug.WriteLine("verts(1)=" & verts(1).ToString)
		verts(2) = New Point3D(CenterPoint.X - radius, CenterPoint.Y, 0)
		verts(2).Number = 2
		'Debug.WriteLine("verts(2)=" & verts(2).ToString)
		verts(3) = New Point3D(CenterPoint.X - nLeg, CenterPoint.Y + nLeg, 0)
		verts(3).Number = 3
		'Debug.WriteLine("verts(3)=" & verts(3).ToString)

		verts(4) = New Point3D(CenterPoint.X, CenterPoint.Y + radius, 0)
		verts(4).Number = 4

		verts(5) = New Point3D(CenterPoint.X + nLeg, CenterPoint.Y + nLeg, 0)
		verts(5).Number = 5

		verts(6) = New Point3D(CenterPoint.X + radius, CenterPoint.Y, 0)
		verts(6).Number = 6

		verts(7) = New Point3D(CenterPoint.X + nLeg, CenterPoint.Y - nLeg, 0)
		verts(7).Number = 7

		Dim rg As New Region3D
		rg.ID = 0		  ' region keys are mainly for use in database storage and retrieval
		rg.Vertices3D = verts
		'set the top and bottom elevations for the trigger
		rg.ZBottom = zBottom
		rg.ZTop = zTop

		Dim t As New Trigger(key, sTrigName, eDir)
		'add the region to the trigger's region collection
		t.Regions.AddItem(rg, rg.ID.ToString)

		Return t

	End Function

	Friend Function AreaTriggerCreate(ByVal xStart As Single, ByVal yStart As Single, ByVal xEnd As Single, ByVal yEnd As Single, ByVal zBot As Single, ByVal zTop As Single, ByVal sName As String, ByVal eDir As Trigger.Directions) As Trigger
		Dim x As Single
		Dim x2 As Single
		Dim y As Single
		Dim y2 As Single
		'check for a drag that does not produce a rectangular area
		'This code assumes parameters are passed in real coordinates and not viewer coordinates
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
		If yStart > yEnd Then
			y = yStart
			y2 = yEnd
		Else
			y2 = yStart
			y = yEnd
		End If

		'points x,y then x,y2 then x2,y2 then x2,y to define the polygonal shape
		'used zBot as the verts z value by standard Parco convention
		Dim verts() As Parco.Point3D = New Point3D(3) {}

		verts(0) = New Point3D(x, y, zBot)
		verts(0).Number = 0
		verts(1) = New Point3D(x, y2, zBot)
		verts(1).Number = 1
		verts(2) = New Point3D(x2, y2, zBot)
		verts(2).Number = 2
		verts(3) = New Point3D(x2, y, zBot)
		verts(3).Number = 3

		Dim r As New Region3D
		r.ID = 0
		r.Vertices3D = verts
		'set our trigger Elevations
		r.ZBottom = zBot
		r.ZTop = zTop

		Dim t As New Trigger(-1, sName, eDir)
		'add the region to the trigger's region collection
		t.Regions.AddItem(r, r.ID.ToString)
		Return t

	End Function
	Friend Sub IntegerOrControl(ByRef e As System.Windows.Forms.KeyPressEventArgs)
		'setting handled to true cancels the keystoke
		If Char.IsDigit(e.KeyChar) = False And Char.IsControl(e.KeyChar) = False Then
			e.Handled = True
		End If

	End Sub

	Friend Function EmailIsValid(ByVal sEmail As String) As Boolean
		Dim regex As New System.Text.RegularExpressions.Regex("\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*", RegexOptions.IgnoreCase)
		Dim m As Match = regex.Match(sEmail)
		If m.Success Then
			Return True
		Else
			Return False
		End If

	End Function
	Friend Sub NumberOrControl(ByRef e As System.Windows.Forms.KeyPressEventArgs)
		'setting Handled to true cancels the keystroke.
		Dim bHandled As Boolean = True
		Select Case True
			Case Char.IsDigit(e.KeyChar)
				bHandled = False
			Case e.KeyChar.ToString = "."
				bHandled = False
			Case e.KeyChar.ToString = "-"
				bHandled = False
			Case Char.IsControl(e.KeyChar)
				bHandled = False
		End Select
		e.Handled = bHandled
	End Sub


End Module
