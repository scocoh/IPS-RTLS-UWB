CREATE TABLE [dbo].[Maps] (
	[I_MAP] [int] IDENTITY (1, 1) NOT NULL ,
	[X_MAP] [nvarchar] (200) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL ,
	[I_ZN_MAP] [int] NULL ,
	[N_OGN_X] [decimal](18, 2) NOT NULL ,
	[N_OGN_Y] [decimal](18, 2) NOT NULL ,
	[N_UR_X] [decimal](18, 2) NOT NULL ,
	[N_UR_Y] [decimal](18, 2) NOT NULL ,
	[N_TOP_Z] [decimal](18, 2) NOT NULL ,
	[N_BTM_Z] [decimal](18, 2) NOT NULL ,
	[B_IMG] [image] NOT NULL 
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

ALTER TABLE [dbo].[Maps] WITH NOCHECK ADD 
	CONSTRAINT [PK_Maps] PRIMARY KEY  CLUSTERED 
	(
		[I_MAP]
	)  ON [PRIMARY] 
GO

ALTER TABLE [dbo].[Maps] ADD 
	CONSTRAINT [IX_Maps] UNIQUE  NONCLUSTERED 
	(
		[X_MAP]
	)  ON [PRIMARY] 
GO

ALTER TABLE [dbo].[Maps] ADD 
	CONSTRAINT [FK_Maps_Zones] FOREIGN KEY 
	(
		[I_ZN_MAP]
	) REFERENCES [dbo].[Zones] (
		[I_ZN]
	)
GO

