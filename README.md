running the sql statement below to create a database to store the intent

USE [20231119]
GO

/****** Object:  Table [dbo].[Intents]    Script Date: 2024/1/15 下午 03:26:40 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Intents](
	[IntentID] [int] NULL,
	[IntentName] [nvarchar](100) NULL,
	[Description] [nvarchar](max) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO



