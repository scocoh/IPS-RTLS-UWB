Public Class ZoneTag
    Private mTag As Parco.Tag
    Private mZone As Parco.Zone

    Public Property Tag() As Parco.Tag
        Get
            Return mTag
        End Get
        Set(ByVal Value As Parco.Tag)
            mTag = Value
        End Set
    End Property

    Public Property CurrentZone() As Parco.Zone
        Get
            Return mZone
        End Get
        Set(ByVal Value As Parco.Zone)
            mZone = Value
        End Set
    End Property
End Class
