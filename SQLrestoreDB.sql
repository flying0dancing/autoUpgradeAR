-- ================================================
-- Template generated from Template Explorer using:
-- Create Procedure (New Menu).SQL
--
-- Use the Specify Values for Template Parameters 
-- command (Ctrl-Shift-M) to fill in the parameter 
-- values below.
--
-- This block of comments will not be included in
-- the definition of the procedure.
-- ================================================
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'RestoreDB') AND type in (N'P', N'PC'))
DROP PROCEDURE RestoreDB
GO
-- =============================================
-- Author:		<Author,,Kun Shen>
-- Create date: <Create Date,,2017-05-15>
-- Description:	<Description,,restore database with back file>
-- =============================================
CREATE PROCEDURE RestoreDB 
	-- Add the parameters for the stored procedure here
	@NewDB nvarchar(100),
	@BakDBFullPath nvarchar(2000),
	@NewDBPath nvarchar(2000)
	
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

    -- Insert statements for procedure here
	DECLARE @Table TABLE (LogicalName varchar(128),[PhysicalName] varchar(128), [Type] varchar, [FileGroupName] varchar(128), [Size] varchar(128), 
            [MaxSize] varchar(128), [FileId]varchar(128), [CreateLSN]varchar(128), [DropLSN]varchar(128), [UniqueId]varchar(128), [ReadOnlyLSN]varchar(128), [ReadWriteLSN]varchar(128), 
            [BackupSizeInBytes]varchar(128), [SourceBlockSize]varchar(128), [FileGroupId]varchar(128), [LogGroupGUID]varchar(128), [DifferentialBaseLSN]varchar(128), [DifferentialBaseGUID]varchar(128), [IsReadOnly]varchar(128), [IsPresent]varchar(128), [TDEThumbprint]varchar(128)
			)
	DECLARE @LogicalNameData varchar(128),@LogicalNameLog varchar(128)
	declare @NewDBMdfPath nvarchar(2000);
	declare @NewDBLdfPath nvarchar(2000);

	INSERT INTO @table
	EXEC('RESTORE FILELISTONLY FROM DISK=''' +@BakDBFullPath+ '''')

    SET @LogicalNameData=(SELECT LogicalName FROM @Table WHERE Type='D')
    SET @LogicalNameLog=(SELECT LogicalName FROM @Table WHERE Type='L')

	set @NewDBMdfPath=@NewDBPath+'\'+@NewDB+'.mdf'
	set @NewDBLdfPath=@NewDBPath+'\'+@NewDB+'_log.ldf'

RESTORE DATABASE @NewDB FROM  DISK =@BakDBFullPath WITH RECOVERY,NOUNLOAD,REPLACE,MOVE @LogicalNameData TO @NewDBMdfPath,MOVE @LogicalNameLog TO @NewDBLdfPath;


END
GO
