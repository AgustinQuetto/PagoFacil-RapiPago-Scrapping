@ECHO OFF		

cd "nssm\win64"

If Not Exist "Logs" md "Logs"

echo Creacion de servicio CRONJOB-PAGOFACIL >> "Logs\services.log"
nssm install CRONJOB-PAGOFACIL "%~dp0..\exec\CRONJOB-PAGOFACIL.bat"
nssm set CRONJOB-PAGOFACIL AppStdout "Logs\CRONJOB-PAGOFACIL.txt"
nssm set CRONJOB-PAGOFACIL AppStderr "Logs\CRONJOB-PAGOFACIL.txt"
nssm set CRONJOB-PAGOFACIL Start SERVICE_AUTO_START
nssm set CRONJOB-PAGOFACIL AppStdoutCreationDisposition 4
nssm set CRONJOB-PAGOFACIL AppRotateFiles 1
nssm set CRONJOB-PAGOFACIL AppRotateOnline 1
nssm set CRONJOB-PAGOFACIL AppRotateSeconds 86400
nssm set CRONJOB-PAGOFACIL AppRotateBytes 368640
nssm start CRONJOB-PAGOFACIL >> "Logs\services.log"