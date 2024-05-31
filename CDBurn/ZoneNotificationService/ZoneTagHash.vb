Public Class ZoneTagHash
    Implements IEnumerable
    Private mObjects As Hashtable

    Public Sub New()
        mObjects = New Hashtable
    End Sub
    '
    '<summary>
    'The number of objects currently stored in the collection.
    '</summary>
    Public ReadOnly Property Count() As Int32
        Get
            Return mObjects.Count

        End Get
    End Property
    '
    '<summary>
    'Gets a System.Collections.ICollection containing the keys in the System.Collections.Hashtable
    '</summary>
    Public ReadOnly Property Keys() As System.Collections.ICollection
        Get
            Return mObjects.Keys

        End Get
    End Property
    '
    '<summary>
    'Gets a System.Collections.ICollection containing the values in the System.Collections.Hashtable
    '</summary>
    Public ReadOnly Property Values() As System.Collections.ICollection
        Get
            Return mObjects.Values
        End Get
    End Property
    '
    '<summary>
    ' Returns the EntityAssignment specified by the key.
    '</summary>
    Public ReadOnly Property Item(ByVal key As Object) As ZoneTag
        Get
            If Not key Is Nothing Then
                If mObjects.ContainsKey(key) Then
                    Dim o As ZoneTag = DirectCast(mObjects(key), ZoneTag)
                    Return o
                End If
            End If
            Return Nothing
        End Get

    End Property
    '
    '<summary>
    ' Removes all objects from the collection
    '</summary>
    Public Sub Clear()
        mObjects.Clear()
    End Sub
    '
    ' <summary>
    ' Adds a new EntityAssignment to the collection with the specified key.
    ' </summary>
    Public Function Add(ByVal key As Object, ByVal obj As ZoneTag) As Boolean
        If mObjects.ContainsKey(key) Then
            Return False
        End If
        mObjects.Add(key, obj)
        Return True
    End Function
    '
    '<summary>
    ' Removes the element (EntityAssignment) with the specified key.
    '</summary>
    Public Function Remove(ByVal key As Object) As Boolean
        If mObjects.ContainsKey(key) Then
            mObjects.Remove(key)
            Return True
        End If
        Return False
    End Function
    '
    '<summary>
    'Determines whether the the collection contains the specific key.
    '</summary>
    Public Function ContainsKey(ByVal key As Object) As Boolean
        If key Is Nothing Then
            Return False
        End If
        Return mObjects.ContainsKey(key)
    End Function
    '
    '<summary>
    'Determines whether the the collection contains the specific value.
    '</summary>
    Public Function ContainsValue(ByVal value As ZoneTag) As Boolean
        If value Is Nothing Then
            Return False
        End If
        Return mObjects.ContainsValue(value)
    End Function
    '
    '<summary>
    'Returns an enumerator that will enumerate all objects in the collection.
    '</summary>
    Public Function GetEnumerator() As System.Collections.IEnumerator Implements System.Collections.IEnumerable.GetEnumerator
        Return mObjects.Values.GetEnumerator
    End Function
    '
    '<summary>
    'Returns a synchronized (thread-safe) wrapper for the System.Collections.Hashtable is synchronized (thread-safe).
    '</summary>
    Public Function Synchronized(ByVal table As System.Collections.Hashtable) As System.Collections.Hashtable
        Return mObjects.Synchronized(table)
    End Function
    '
    '<summary>
    'Gets an value indication whether access to synchronize access to the System.Collections.Hashtable is
    '</summary>
    Public Function IsSynchronized() As Boolean
        Return mObjects.IsSynchronized
    End Function
    '
    '<summary>
    'Gets an object that can be used to synchronize access to the System.Collections.Hashtable
    '</summary>
    Public ReadOnly Property SyncRoot() As Object
        Get
            Return mObjects.SyncRoot
        End Get
    End Property

End Class
