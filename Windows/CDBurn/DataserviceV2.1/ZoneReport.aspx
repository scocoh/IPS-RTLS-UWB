<%@ Page Language="vb" AutoEventWireup="false" Codebehind="ZoneReport.aspx.vb" Inherits="ParcoRTLSDataservice.ZoneReport"%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
	<HEAD>
		<title>Parco Zone Report</title>
		<meta name="GENERATOR" content="Microsoft Visual Studio .NET 7.1">
		<meta name="CODE_LANGUAGE" content="Visual Basic .NET 7.1">
		<meta name="vs_defaultClientScript" content="JavaScript">
		<meta name="vs_targetSchema" content="http://schemas.microsoft.com/intellisense/ie5">
	</HEAD>
	<body>
		<form id="Form1" method="post" runat="server">
			<P align="center"><STRONG>Parco Zone Report</STRONG>&nbsp;</P>
			Report Date:&nbsp;&nbsp;<asp:Label id="lblDate" runat="server" EnableViewState="False"></asp:Label>
			<ul title="Notes:">
				<li>Each Zone is followed by its level (in parenthesis) in the hierarchy.</li>
				<li>The building level may contain outside areas in addition to buildings.</li>
			</ul>
			<P>
				<asp:Label id="lblError" runat="server" EnableViewState="False" ForeColor="Red"></asp:Label><br>
				<asp:Label id="lblZones" runat="server"></asp:Label></P>
		</form>
	</body>
</HTML>
