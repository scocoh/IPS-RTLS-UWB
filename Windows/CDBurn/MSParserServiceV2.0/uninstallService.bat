@echo off
set SERVICE_HOME=c:\parco\msparser
set SERVICE_EXE=ParcoMSParserService.exe
REM the following directory is for .NET 1.1, your mileage may vary
set INSTALL_UTIL_HOME=C:\Windows\Microsoft.NET\Framework\v1.1.4322

set PATH=%PATH%;%INSTALL_UTIL_HOME%

cd %SERVICE_HOME%

echo Uninstalling Service...
installutil /u /name=Parco.MSParser %SERVICE_EXE%

echo Done.
