import time
import os
 
def startCronjob():
	os.system("echo ----------------------------------------------------------")
	os.system("echo ------------------------running---------------------------")
	os.system("echo --------------------CRONJOB RAPIPAGO----------------------")
	os.system('python RapiPago.py')
	os.system("echo ----------------------------------------------------------")
	os.system("echo -----------------------finished---------------------------")
	os.system("echo ----------------------------------------------------------")
 
if __name__ == '__main__':
	#1209600 = two weeks
	while True:
		startCronjob() 
		time.sleep(1209600)
