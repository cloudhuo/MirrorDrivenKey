@echo off

echo ===================================

echo =========MY_TOOLS INSTALLATION====

echo ===================================

 

set TOOLS_LOCATION=%~dp0
set INPUT=2014-x64

:INSTALL
for  %%A in (%INPUT%) do (

    echo Maya Version is %%A
    echo %userprofile%

    IF EXIST  %userprofile%\Documents\maya\%%A\prefs\shelves\ (
        
        echo Found maya %%A and installing ...

        XCOPY "%TOOLS_LOCATION%MirrorDrivenKey.mel" "%userprofile%\Documents\maya\%%A\scripts\"
	XCOPY "%TOOLS_LOCATION%userSetup.mel" "%userprofile%\Documents\maya\%%A\scripts\"
	XCOPY "%TOOLS_LOCATION%MirrorDrivenKey.py" "%userprofile%\Documents\maya\%%A\scripts\"
    
        echo "Installation is Done!"
        
    ) else (

        echo Maya %%A is not installed
        set INPUT=
        set /P INPUT=Type Maya Version:
        echo Your input was: %INPUT%

        GOTO INSTALL

    )
)

pause