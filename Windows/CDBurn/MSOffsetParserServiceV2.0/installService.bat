@echo off
set SERVICE_HOME=c:\parco\msoffsetparser
set SERVICE_EXE=ParcoMSOffsetParser.exe
REM the following directory is for .NET 1.1, your mileage may vary
set INSTALL_UTIL_HOME=C:\Windows\Microsoft.NET\Framework\v1.1.4322
REM Account credentials if the service uses a user account
set USER_NAME=
set PASSWORD=

set PATH=%PATH%;%INSTALL_UTIL_HOME%

cd %SERVICE_HOME%

echo Installing Service...
installutil /name=Parco.MSOffsetParser /account=localsystem /user=%USER_NAME% /password=%PASSWORD% %SERVICE_EXE%

echo Done.
