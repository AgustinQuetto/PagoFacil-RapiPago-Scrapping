cd "nssm\win64"


If Not Exist "Logs" md "Logs"


nssm stop CRONJOB-PAGOFACIL >> Logs\services.log

nssm remove CRONJOB-PAGOFACIL confirm >> Logs\services.log