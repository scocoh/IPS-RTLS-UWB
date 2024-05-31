Imports System.ServiceProcess

Public Class ZoneNotificationService
    Inherits System.ServiceProcess.ServiceBase

#Region " Component Designer generated code "

    Public Sub New()
        MyBase.New()

        ' This call is required by the Component Designer.
        InitializeComponent()

        ' Add any initialization after the InitializeComponent() call

    End Sub

    'UserService overrides dispose to clean up the component list.
    Protected Overloads Overrides Sub Dispose(ByVal disposing As Boolean)
        If disposing Then
            If Not (components Is Nothing) Then
                components.Dispose()
            End If
        End If
        MyBase.Dispose(disposing)
    End Sub

    ' The main entry point for the process
    <MTAThread()> _
    Shared Sub Main()
        Dim ServicesToRun() As System.ServiceProcess.ServiceBase

        ' More than one NT Service may run within the same process. To add
        ' another service to this process, change the following line to
        ' create a second service object. For example,
        '
        '   ServicesToRun = New System.ServiceProcess.ServiceBase () {New Service1, New MySecondUserService}
        '
        ServicesToRun = New System.ServiceProcess.ServiceBase() {New ZoneNotificationService}

        System.ServiceProcess.ServiceBase.Run(ServicesToRun)
    End Sub

    'Required by the Component Designer
    Private components As System.ComponentModel.IContainer

    ' NOTE: The following procedure is required by the Component Designer
    ' It can be modified using the Component Designer.  
    ' Do not modify it using the code editor.
    Friend WithEvents ServiceController1 As System.ServiceProcess.ServiceController
    <System.Diagnostics.DebuggerStepThrough()> Private Sub InitializeComponent()
        Me.ServiceController1 = New System.ServiceProcess.ServiceController
        '
        'ZoneNotificationService
        '
        Me.ServiceName = "ZoneNotificationService"

    End Sub

#End Region

    Friend mZnTg As ZoneTagHash

    Friend WithEvents mStream As Parco.DataStream
    Friend mCampus As Zone 'the zone hierarchy, begining with the campus zone object
    Friend mData As Parco.Data
    Friend mDataURL As String ' the URL of the dataservice
    Friend mResourceType As Integer ' the resource type to connect to for tag data
    Delegate Sub delLoadZones()
    Friend mbStopping As Boolean 'for auto reconnect functionality
    Friend Event ZoneChange(ByVal sender As Object, ByVal e As ZoneChangeEventArgs) 'output event

    Protected Overrides Sub OnStart(ByVal args() As String)
        ' Add code here to start your service. This method should set things
        ' in motion so your service can do its work.
        Try
            mbStopping = False
            mDataURL = Configuration.ConfigurationSettings.AppSettings("DataServiceURL")
            mResourceType = CType(Configuration.ConfigurationSettings.AppSettings("ResourceType"), Integer)

            mData = New Parco.Data(mDataURL)
            'we are doing an asyncronous load so that the service controller does not timeout on start
            'while we are loading up the zones into memory. 
            mZnTg = New ZoneTagHash

            'Hook up our event handler. Using the event should decouple the datastream from the stream event
            'and help prevent heartbeat failures
            AddHandler ZoneChange, AddressOf ZoneChangeOutput

            'aysynh load as the service controller is sensitive to startup time.
            'It was taking 35 seconds or so to remotely load all the zones via the vpn
            BeginLoad()

        Catch ex As Exception
            LogServiceError(ex, "Service.OnStart")
        End Try
    End Sub

    Protected Overrides Sub OnStop()
        ' Add code here to perform any tear-down necessary to stop your service.
        Try
            mbStopping = True
            If Not mStream Is Nothing AndAlso mStream.IsConnected Then
                'close our data stream from the manager
                Dim req As New Parco.ParcoMsg.Request(ParcoMsg.RequestType.EndStream, "ZNSEnd")
                mStream.SendRequest(req)
            End If
        Catch ex As Exception
            LogServiceError(ex, "Service.OnStop")
        End Try
    End Sub

    Private Sub BeginLoad()
        Try
            Dim ar As IAsyncResult
            Dim del As New delLoadZones(AddressOf LoadZones)
            Dim cb As New AsyncCallback(AddressOf EndLoad)
            ar = del.BeginInvoke(cb, Nothing)
        Catch ex As Exception
            LogServiceError(ex, "Service.BeginLoad")
        End Try
    End Sub
    Private Sub EndLoad(ByVal ar As IAsyncResult)
        'If the mCampus Zone object is nothing then we could not load any zones.
        'In the event that we do not have any zones, dont bother connect to the datastream 
        'as we do not the necessary info to run.
        'WriteEventLog("ZoneNotify", "In End Load", EventLogEntryType.Information)
        Try
            If mCampus Is Nothing Then
                WriteEventLog("ZoneNotify", "No Campus Zone, service not connecting to stream.", EventLogEntryType.Error)
            Else
                ConnectStream()
            End If
        Catch ex As Exception
            LogServiceError(ex, "Zones.EndLoad")
        End Try
    End Sub

    Private Sub ConnectStream()
        'WriteEventLog("ZoneNotify", "Getting Resource Type", EventLogEntryType.Information)

        Dim r As Parco.Resource = mData.ResourceGet(mResourceType)
        If r.IsFullstream Then
            'we are ok to go as this is what we coded for
            If Not mStream Is Nothing Then
                If mStream.IsConnected Then
                    Dim endreq As New Parco.ParcoMsg.Request(ParcoMsg.RequestType.EndStream, "ZNSrecon")
                    mStream.SendRequest(endreq)
                    'Return if we have autoreconnect code 
                End If
            End If
            mStream = New Parco.DataStream(r.TCPIP, r.Port)
            mStream.IsSubscriptionBased = False
            mStream.Name = r.Name
            mStream.IsAveraged = r.IsAveraged
            Dim req As New Parco.ParcoMsg.Request(ParcoMsg.RequestType.BeginStream, "ZNSBegin")
            mStream.Connect()
            mStream.SendRequest(req)
            'WriteEventLog("ZoneNotify", "Stream Request Sent", EventLogEntryType.Information)
        Else
            WriteEventLog("ZoneNotificationService", "The resouce type specified in the config file is not a fullstream resouce.", EventLogEntryType.Error)
        End If

    End Sub

    Private Sub LoadZones()
        'The Zones are loaded into the database in a hierarchal structure.
        'The ZoneChildrenGet method throws a Parco.DataException if the zone does not have any children zones.
        'I am letting other exceptions drop to the outer handler as they indicate some other unanticipated problem.
        Dim i As Integer
        Try
            'see if we have a campus zone to begin the hierarchy
            Dim ds As DataSet = mData.ZonesList(Parco.ZoneType.Campus)

            'we should get just one here
            If ds.Tables(0).Rows.Count = 1 Then
                mCampus = mData.ZoneGet(CType(ds.Tables(0).Rows(0).Item("I_ZN"), Integer))
                'now get the child building zones
                i = 1
                mCampus.Children = mData.ZoneChildrenGet(mCampus.I_ZN)
                'for each building zone, load the floor children
                Dim zBlg As Zone
                For Each zBlg In mCampus.Children
                    'for each building zone in the campus, load the building's floor zones 
                    Try
                        zBlg.Parent = mCampus
                        zBlg.Children = mData.ZoneChildrenGet(zBlg.I_ZN)
                        Dim zFloors As ZoneCollection
                        zFloors = zBlg.Children
                        Dim zFloor As Zone
                        'for each floor load the wing
                        For Each zFloor In zFloors
                            i += 1
                            Try
                                zFloor.Parent = zBlg
                                zFloor.Children = mData.ZoneChildrenGet(zFloor.I_ZN)

                                Dim zWings As ZoneCollection = zFloor.Children
                                Dim zWing As Zone
                                'for each wing load the room zones
                                For Each zWing In zWings
                                    'we have proximity zones and O data zones at the wing level which do not have children
                                    i += 1
                                    'only zones of type wing should have rooms, not Prox and O zones
                                    zWing.Parent = zFloor
                                    If zWing.ZoneType = ZoneType.Wing Then
                                        Try
                                            zWing.Children = mData.ZoneChildrenGet(zWing.I_ZN)
                                            'add the room zone count to our total
                                            i += zWing.Children.Count
                                            Dim zRoom As Zone
                                            For Each zRoom In zWing.Children
                                                zRoom.Parent = zWing
                                            Next
                                        Catch ex As Parco.DataException
                                            'no room children for this wing
                                        End Try
                                    End If
                                Next
                            Catch ex As Parco.DataException
                                'no wing children for this floor
                            End Try

                        Next 'Each zFloor In zFloors
                    Catch ex As Parco.DataException
                        'no floor children for this building
                    End Try
                Next 'Each zBlg In mCampus.Children
            Else
                'we could not load a zone hierarchy
                mCampus = Nothing
                EventLog.WriteEntry("ZoneNotificationService", "No Zones loaded to enable the service to run.", EventLogEntryType.Error)
            End If
            ' we have zones
            EventLog.WriteEntry("ZoneNotificationService", "Zone Notification Service loaded with " & i.ToString & " Zones ", EventLogEntryType.Information)
        Catch ex As Exception
            LogServiceError(ex, "LoadZones")
            mCampus = Nothing
        End Try
    End Sub

    Private Sub mStream_Connection(ByVal sender As Object, ByVal e As StreamConnectionEventArgs) Handles mStream.Connection
        If e.State <> ConnectionState.Connected And mbStopping = False Then
            'may want to reconnect the stream here..
            'we could have been disconnected if the code slowed to the point where
            'a heartbeat did not make it back to the manager in a timely manner
        Else
            If e.State = ConnectionState.Connected Then
                'WriteEventLog("ZoneNotify", "Conneted to stream", EventLogEntryType.Information)
            End If
        End If
    End Sub

    Private Sub mStream_Response(ByVal sender As Object, ByVal e As StreamResponseEventArgs) Handles mStream.Response
        If e.Response.Message <> String.Empty Then
            'we have an issue with our request meaning that we will not get streaming data
            WriteEventLog("Zone Notification", "Stream Request Error: " & e.Response.Message, EventLogEntryType.Error)
        End If
    End Sub

    Private Sub mStream_Stream(ByVal sender As Object, ByVal e As StreamDataEventArgs) Handles mStream.Stream
        Try
            'WriteEventLog("ZoneNotify", e.Tag.ID & " arrived!", EventLogEntryType.Information)

            Dim zt As ZoneTag
            If mZnTg.ContainsKey(e.Tag.ID) Then
                zt = mZnTg.Item(e.Tag.ID)

                If zt.CurrentZone.ContainsTag(e.Tag) = False Then
                    'the zone has changed
                    Dim zOrig As Zone = zt.CurrentZone
                    zt.CurrentZone = FindZone(e.Tag, zt.CurrentZone)
                    If zt.CurrentZone Is Nothing Then
                        'something is wrong, go back the original zone and log a problem....
                        zt.CurrentZone = zOrig
                        WriteEventLog("ZoneNotificationService", "Zone not found for tag " & e.Tag.ToString, EventLogEntryType.Warning)
                    Else
                        RaiseEvent ZoneChange(sender, New ZoneChangeEventArgs(zt))
                    End If
                End If
            Else
                'we have not seen this tag before
                zt = New ZoneTag
                zt.Tag = e.Tag
                'now find the lowest level zone
                zt.CurrentZone = FindNewZone(e.Tag)
                If zt.CurrentZone Is Nothing Then
                    'something is wrong
                    WriteEventLog("ZoneNotificationService", "Zone not found for new tag " & e.Tag.ToString, EventLogEntryType.Warning)
                Else
                    'may need to synchlock the hash table here....
                    mZnTg.Add(e.Tag.ID, zt)
                    RaiseEvent ZoneChange(sender, New ZoneChangeEventArgs(zt))
                End If
            End If
        Catch ex As Exception
            LogServiceError(ex, "Zone Notification stream event")
        End Try
    End Sub

    Private Function FindZone(ByRef t As Parco.Tag, ByRef zn As Zone) As Zone
        'Args are passed ByRef to keep from allocating memory
        'I am calling this method only if we know that the tag is not in this zone, but may be in the parent
        If Not zn.Parent Is Nothing Then
            If zn.Parent.ContainsTag(t) Then
                'loop through the rest of the children to find it.
                Dim zc As Zone
                For Each zc In zn.Parent.Children
                    If zc.ContainsTag(t) Then
                        Return zc
                    End If
                Next
                'if we made it here, then we have to return the parent
                'since none of the children seem to have the tag but the tag is in the parent
                Return zn.Parent
            Else
                'do a top down search
                'this could possibly be optimized a bit more by traversing up one level and trying again
                'testing will tell if there is any perfomance benefit as there are very few items higher in the hierarchy
                Return FindNewZone(t)
            End If
        Else
            Return Nothing
        End If
    End Function

    Private Function FindNewZone(ByRef t As Parco.Tag) As Zone
        'Args are passed ByRef to keep from allocating memory
        Dim znB, znF, znW, znR As Zone
        If mCampus.ContainsTag(t) Then
            For Each znB In mCampus.Children
                If znB.ContainsTag(t) Then
                    If znB.Children Is Nothing Then
                        'the building has no children, so return it
                        Return znB
                    Else
                        For Each znF In znB.Children
                            If znF.ContainsTag(t) Then
                                If znF.Children Is Nothing Then
                                    'the floor has no children, so return it
                                    Return znF
                                Else
                                    For Each znW In znF.Children
                                        'at this level one or more zones may contain the tag
                                        'since OData and PData zones may overlap. We are doing Room lookups so ingnore all Prox and OData zones.
                                        If znW.ZoneType = ZoneType.Wing AndAlso znW.ContainsTag(t) Then
                                            If znW.Children Is Nothing Then
                                                'the wing does not contain any children, so return it
                                                Return znW
                                            Else
                                                For Each znR In znW.Children
                                                    If znR.ContainsTag(t) Then
                                                        Return znR
                                                    End If
                                                Next
                                                'we did not find a room, so return the wing
                                                Return znW
                                            End If
                                        End If
                                    Next
                                    'if we made it here then we did not find a wing containing the tag so return the floor
                                    Return znF
                                End If
                            End If
                        Next 'Each znF In znB.Children
                        'if we made it here then we did not find floor containing the point so return the building
                        Return znB
                    End If
                End If
            Next 'Each znB In mCampus.Children
        Else
            'not in the campus?
            Return Nothing
        End If
    End Function

    Private Sub ZoneChangeOutput(ByVal sender As Object, ByVal e As ZoneChangeEventArgs)
        'this is where you would put in your code to send the data to the Azyxxi database
        Try
            'you have full access to all of the tag info such as battery info and MsgType(T,O,P)
            'and the complete zone object
            Dim sMsg As String = e.ZoneTag.Tag.ID & " is now in " & e.ZoneTag.CurrentZone.Name
            WriteEventLog("ZoneNotify", sMsg, EventLogEntryType.Information)
        Catch ex As Exception
            LogServiceError(ex, "ZoneNotify.OutputData")
        End Try
    End Sub

    'For Service Errors that we should not get 
    Private Sub LogServiceError(ByVal ex As Exception, ByVal routine As String)
        WriteEventLog("Parco.ZoneNotificationService", routine & ": " & ex.ToString, EventLogEntryType.Error)
    End Sub

    'For other Service Events such as start/stop incase we want to customize the message in a particular format
    Private Sub WriteEventLog(ByVal src As String, ByVal msg As String, ByVal type As System.Diagnostics.EventLogEntryType)
        EventLog.WriteEntry(src, msg, type)
    End Sub

End Class
