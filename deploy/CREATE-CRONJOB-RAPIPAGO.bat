@ECHO OFF		

cd "nssm\win64"

If Not Exist "Logs" md "Logs"

echo Creacion de servicio CRONJOB-RAPIPAGO >> "Logs\services.log"
nssm install CRONJOB-RAPIPAGO "%~dp0..\exec\CRONJOB-RAPIPAGO.bat"
nssm set CRONJOB-RAPIPAGO AppStdout "Logs\CRONJOB-RAPIPAGO.txt"
nssm set CRONJOB-RAPIPAGO AppStderr "Logs\CRONJOB-RAPIPAGO.txt"
nssm set CRONJOB-RAPIPAGO Start SERVICE_AUTO_START
nssm set CRONJOB-RAPIPAGO AppStdoutCreationDisposition 4
nssm set CRONJOB-RAPIPAGO AppRotateFiles 1
nssm set CRONJOB-RAPIPAGO AppRotateOnline 1
nssm set CRONJOB-RAPIPAGO AppRotateSeconds 86400
nssm set CRONJOB-RAPIPAGO AppRotateBytes 368640
nssm start CRONJOB-RAPIPAGO >> "Logs\services.log"