echo off
rem SET count=1
rem this is a comment
rem FOR /f "tokens=*" %%G IN ('dir /b') DO (call :subroutine "%%G")
rem GOTO :eof
rem 
rem :subroutine
rem this subroutine takes one parameter, here invoked as %1
rem  echo %count%:%1
rem  set /a count+=1
rem  GOTO :eof

rem FOR /F %i IN (file.txt) DO @echo %i
rem FOR /F "tokens=*" %%i IN (SmallTest.txt) DO @ECHO %%i

SET count = 0
echo %count%
FOR /F "tokens=1,2,3 delims=," %%i in (SmallTest.txt) DO (call :subroutine %%i %%j %%k)
GOTO :eof

:subroutine
 echo %count%
 echo %1,%2,%3
 set /a count += %1
 echo %count%
 GOTO :eof