Updates as of 4/20/2006 to fix all floating point errors:
If you need to keep existing data you can update your databases as follows, if not then simply attach
the new databases.

ParcoRTLSMaint Database changes:
	Table Vertices:
	fields N_X, N_Y, N_Z changed from float to decimal length=9 precision-18 Scale=2
	Field N_ORD changed from float to int

	Table Regions:
	Fields N_MAX_X, N_MAX_y, N_MAX_Z, N_MIN_X, N_MIN_Y, N_MIN_Z changed from float
	 to decimal length=9 precision-18 Scale=2

	Table Devices
	Fields N_MOE_X, N_MOE_Y, N_MOE_Z changed from float to decimal length=9 precision-18
 	Scale=2

	Run the ParcoRTLSMaint4.20.2006upgrd.sql script to update these sprocs:
	uspVertexAdd, uspVertexEdit, uspRegionAdd, uspRegionEdit, uspDeviceAdd, uspDeviceEdit

ParcoRTLSHistO and ParcoRTLSHistP and ParcoRTLSHistR database changes:
	Table PositionHistory:
	Fields N_X, N_Y, N_Z changed from float to decimal length=9 precision-18 Scale=2

	Run the AllParcoHist.sql script to update these sprocs in each of the history databases:
	uspPostionInsert, uspHistoryByLocation.

Updates for version 2.1 of the SDK and dataservice (8/31/2006 release date) require the Maps table to be added to the database. Run the Version2.1.upgrade.sql script to add the maps table to an existing database.