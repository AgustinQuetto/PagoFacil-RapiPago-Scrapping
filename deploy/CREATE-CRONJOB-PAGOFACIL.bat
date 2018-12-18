echo Creacion de servicio CRONJOB-PAGOFACIL >> "Logs\services.log"

nssm install CRONJOB-PAGOFACIL "C:\Users\eamarillo\Desktop\PagoFacil-RapiPago\exec\CRONJOB-PAGOFACIL.bat" >> "Logs\services.log"
nssm set CRONJOB-PAGOFACIL AppStdout "Logs\CRONJOB-PAGOFACIL.txt" >> "Logs\services.log"
nssm set CRONJOB-PAGOFACIL AppStderr "Logs\CRONJOB-PAGOFACIL.txt" >> "Logs\services.log"
nssm set CRONJOB-PAGOFACIL Start SERVICE_AUTO_START >> "Logs\services.log"
nssm set CRONJOB-PAGOFACIL AppStdoutCreationDisposition 4 >> "Logs\services.log"
nssm set CRONJOB-PAGOFACIL AppRotateFiles 1 >> "Logs\services.log"
nssm set CRONJOB-PAGOFACIL AppRotateOnline 1 >> "Logs\services.log"
nssm set CRONJOB-PAGOFACIL AppRotateSeconds 86400
 >> "Logs\services.log"
nssm set CRONJOB-PAGOFACIL AppRotateBytes 368640 >> "Logs\services.log"
nssm start CRONJOB-PAGOFACIL >> "Logs\services.log"