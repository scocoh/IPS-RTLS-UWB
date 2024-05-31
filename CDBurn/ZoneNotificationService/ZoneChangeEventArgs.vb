Public Class ZoneChangeEventArgs
    Inherits EventArgs

    Sub New(ByVal zt As ZoneTag)
        mZT = zt
    End Sub
    Private mZT As ZoneTag

    Public ReadOnly Property ZoneTag() As ZoneTag
        Get
            Return mZT
        End Get
    End Property
End Class
