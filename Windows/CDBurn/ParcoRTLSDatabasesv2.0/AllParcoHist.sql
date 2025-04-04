if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[uspPositionInsert]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[uspPositionInsert]
GO

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[uspHistoryByLocation]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[uspHistoryByLocation]
GO

SET QUOTED_IDENTIFIER ON 
GO
SET ANSI_NULLS OFF 
GO

/* ParcoRTLS 1.0 compatability
Purpose: Insert a postion for a device into the ParcoHistory table
Database:	ParcoRTLS
CreateDate: 07/01/2003
CreateBy:	Mike Farnsworth, Standard I-O Inc
ModDate:	4/20/2006
ModBy:		MWF
Modifications:	changed float types to decimal(18,9) to fix floating decimal problems

*/

CREATE procedure uspPositionInsert
(
	@I_PH int = null output,
	@X_ID_DEV	nvarchar	(200),
	@N_X	decimal(18,9),
	@N_Y	decimal(18,9),
	@N_Z	decimal(18,9),
	@D_POS_BGN	datetime,
	@D_POS_END datetime
)

as

Begin
	set nocount on
	
	Insert into PositionHistory ( X_ID_DEV, N_X, N_Y, N_Z, D_POS_BGN, D_POS_END )
		values (@X_ID_DEV, @N_X, @N_Y, @N_Z, @D_POS_BGN, @D_POS_END)

	if @@Error = 0
		set @I_PH = scope_identity()
	else
		set @I_PH = -1

	RETURN @@ERROR 

End
GO
SET QUOTED_IDENTIFIER OFF 
GO
SET ANSI_NULLS ON 
GO

SET QUOTED_IDENTIFIER ON 
GO
SET ANSI_NULLS OFF 
GO

/*Purpose: Select all of the rows between the begin and end dates for a rectangular volume from the ParcoHistory table
Database:	ParcoRTLS
CreateDate: 07/01/2003
CreateBy:	Mike Farnsworth, Standard I-O Inc
ModDate:	4/20/2006
ModBy:		MWF
Modifications:	changed float types to decimal(18,9) to fix floating decimal problems

Note: this sproc is used by history player and relies on the orderby clause to be D_POS_BGN ASC !

*/

CREATE procedure uspHistoryByLocation
(
	@XMin decimal(18,9),
	@XMax decimal(18,9),
	@YMin decimal(18,9),
	@YMax decimal(18,9),
	@ZMin decimal(18,9),
	@ZMax decimal(18,9),
	@D_POS_BGN datetime,
	@D_POS_END datetime
)

as

Begin

	Select * From PositionHistory 
		Where ( D_POS_BGN >= @D_POS_BGN AND D_POS_END <= @D_POS_END)  AND
			 ( N_X <= @XMax  and  N_X >= @XMin   AND
			 	N_Y <= @YMax  and N_Y >= @YMin  AND 
				N_Z <= @ZMax  and N_Z >= @ZMin  )
		 	 Order By D_POS_BGN Asc

	RETURN @@ERROR 

End
GO
SET QUOTED_IDENTIFIER OFF 
GO
SET ANSI_NULLS ON 
GO

