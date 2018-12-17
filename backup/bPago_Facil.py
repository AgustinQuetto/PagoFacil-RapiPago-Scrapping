from urllib.request import urlopen
import json
import csv
import string
import time
import os
import inspect

inicio=time.clock()


 # open a file for reading
Provincias_Localidades = open('MaestroProvinciasLocalidades.csv', 'r')

spamreader = csv.reader(Provincias_Localidades, delimiter=',', quotechar='|')
count = 0

n = 1337                # cantidad de lineas en el csv
m = 3                   # provincia localidad codigo
Localidades=[None] * n  # creo una lista vacia de 1337 registros para luego convertirla en matriz

for i in range(n):
  Localidades[i] = [None] * m   #creo una matriz de  3 x 1337 
 
for row in spamreader:
    Localidades[count]=row      #relleno la lista con los datos leidos del maestro csv
    count +=1



indice = 0

for Localidad in Localidades:  #itero por cada registro del csv
    
    Base = "https://www.e-pagofacil.com/backend/intranet/coordenadas.php?p="+Localidades[indice][2]+"&l=" # Creo la base con el codigo de la provincia
    Localidad_UrlEncoded = Localidades[indice][1].replace(' ','%20') # formateo la localidad a url reemplazando espacios por %20
    link = Base+Localidad_UrlEncoded

    response = urlopen(link)


    Pago_facil = json.loads(response.read())

    PF_data = Pago_facil

    RutaArchivosCSV = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))

    
    RutaArchivosCSV = RutaArchivosCSV.replace("\t","\\t")  + '\\ArchivosCSV\\' + 'Sucursales_'+Localidades[indice][0] +'_'+ Localidades[indice][1] + '_PagoFacil.csv'


    # open a file for writing
    Archivo_PagoFacil = open(RutaArchivosCSV, 'w+')

    # create the csv writer object

    csvwriter = csv.writer(Archivo_PagoFacil)

    count = 0

    for registro in PF_data:

          if count == 0:

                 header = registro.keys()

                 csvwriter.writerow(header)

                 count += 1

          csvwriter.writerow(registro.values())

    Archivo_PagoFacil.close()
    print(indice)
    indice += 1
    
fin=time.clock()
print(fin-inicio,' sec.')
