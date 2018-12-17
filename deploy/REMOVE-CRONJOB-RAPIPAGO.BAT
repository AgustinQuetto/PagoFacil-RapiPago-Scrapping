@ECHO OFF		

cd "nssm\win64"

If Not Exist "Logs" md "Logs"

nssm stop CRONJOB-RAPIPAGO >> Logs\services.log
nssm remove CRONJOB-RAPIPAGO confirm >> Logs\services.log