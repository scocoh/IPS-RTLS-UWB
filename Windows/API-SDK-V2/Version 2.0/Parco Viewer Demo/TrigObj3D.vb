Imports Microsoft.DirectX
Imports SIO3DViewer

Public Class TrigObj3D
	Inherits SIO3DViewer.Obj3D

	Private mRadius As Single
	Private mHieght As Single
	Private mTrig As MeshObject



	Public Sub New(ByVal clr As Color)
		Me.New(clr, Color.White)
	End Sub

	Public Sub New(ByVal diffuse As Color, ByVal specular As Color)
		MyBase.New()
		mTrig = New MeshObject("TagTrig.x", diffuse, specular)

	End Sub
End Class
