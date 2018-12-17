from   lxml import html
import requests
import numpy as  np
import geocoder
import smtplib

from   urllib.request import urlopen
import json
import csv
import string
import time
import os
import inspect


inicio=time.clock()


##try:
## Cargo los nombres de las provincias con sus respectivos ids en una matriz de la forma [id][nombre]   
Codigos_Provincias = open('MaestroCodigosProvincias.csv', 'r')

Temp_Provincia = np.zeros((1,2))

for cod_prov in Codigos_Provincias:
    temp=cod_prov.rstrip().partition(',')
    provincias= np.array([  [temp[0]   ,  temp[2]]  ])
    Temp_Provincia=np.append( Temp_Provincia,provincias,axis=0 )
    
Provincia=np.delete(Temp_Provincia,0,0)




## creo una matriz base en donde voy a ir concatenando las localidades y sus nombres junto los datos de la provincia y su id obtenidos previamente
## donde los 2 primeros van a ser obtenidos del archivo json obtenido de la consulta con el id de la provincia.
## como resultado obtenemos una matriz de la forma [id_prov][name_prov][id_loc][name_loc]
Provincia_localidad=np.zeros((1,4))

##iteramos sobre las provincias para obtener todas las localidades
for codigo in Provincia:
    
        link= 'https://www.rapipago.com.ar/rapipagoWeb/index.php/services/localidades/'+codigo[0]
        
        url = urlopen(link)

        Rapi_Pago = json.loads(url.read())


        for dato in Rapi_Pago['data'] :
            test= np.array([[codigo[0],codigo[1], dato['id_prov_partido_localidad'], dato['descripcion']]])
            Provincia_localidad=np.append(Provincia_localidad,test,axis=0)
Provincia_localidad=np.delete(Provincia_localidad,0,0)

   

##    estructura de la matriz Provincia_localidad
##        [id_prov name_prov id_loc name_loc ]  de dimensiones (n,4) donde n es la cantidad de registros y 4 son las dimensiones mencionadas
##        [   0        1        2      3     ]  para referencias, estos son los subindices correspondientes


## iteramos por cada localidad para obtener las sucursales
## genera un archivo csv con la información: 'Localidad','Sucursal','Direccion','Latitud','Longitud'
## nombrado Sucursales_%Provincia%_%Localidad%_RapiPago.csv donde lo mencionado entre '%' varia a medida que se avanza en la iteración.
for Localidad in Provincia_localidad:

    url='https://www.rapipago.com.ar/rapipagoWeb/index.php/resultado_sucursales?prov='+Localidad[0]+'&loc='+Localidad[2]+'&extracash=false'
    page = requests.get(url)
    tree = html.fromstring(page.content)
       
    ##leemos la dirección y el nombre del local, directamente del html
    data = tree.xpath('//div[@class="text_drop"]/text()')


    vindice = 1

    sucursal = []
    direccion = []


    ## dado que la direccion  y la sucursal vienen una detras de la otra, sin distinción, sabemos que siempre van a estar
    ## en la secuencia sucursal[n], direccion[n+1] es decir contiguas. Donde n es un numero natural
    for dato in data:

       if vindice % 2 == 0:
          direccion.append(dato.rstrip())
       else:
          sucursal.append(dato.rstrip())
      
       vindice += 1
       
    ##leemos la latitud y la longitud, directamente del html
    ## accediendo primero a los elemntos a que posean atributo data-lat
    ## y luego accediendo a la informacion del atributo propiamente dicha
    dato= tree.xpath('//a[@data-lat]')

    lat  = []
    long = []

    vindice = 1
    vindicedireccion = 0


    ##dado que la informacion se encuentra duplicada en la consulta
    ##seleccionamos solo 1 par de valores de cada atributo del elemento a (guardado en dato)
    for dat in dato:

       if vindice % 2 == 0:
           if dat.attrib['data-lat'] == '0.00000000' :
              lat.append( dat.attrib['data-lat'])
              long.append( dat.attrib['data-lng'])
              vindicedireccion += 1
          
       vindice += 1
       

    
    ## convierto todo a arrays del tipo numpy para mejorar la velocidad de las operaciones matriciales y facilitar la sintaxis
    sucursal  = np.transpose(np.asarray(sucursal))
    direccion = np.transpose(np.asarray(direccion))
    lat   = np.transpose(np.asarray(lat))
    long  = np.transpose(np.asarray(long))

    print(sucursal)
    print(direccion)
    print(lat)
    print(long)
    
    ## si la sucursal no es nula entonces genero una matriz del formato [name_loc][sucursal][direccion][lat][long]
    if sucursal.size:
       
        sucursal_direccion=np.array( [sucursal, direccion,lat,long])
        sucursal_direccion=sucursal_direccion.T
        print(sucursal_direccion.shape)
        print(sucursal_direccion)
        ## inserto el nombre de la localidad como primera fila de la matriz ( notese el 0 indicando que será la primer fila donde se insertará)
        Localidad_Sucursal_Direccion=np.insert( sucursal_direccion ,0, Localidad[3], axis=1) ##agrego el nombre de la localidad

         
        RutaArchivosCSV = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))

        ## Sucursales_%Provincia%_%Localidad%_RapiPago.csv
        RutaArchivosCSV = RutaArchivosCSV.replace("\t","\\t")  + '\\ArchivosCSV_Rapipago\\' + 'Sucursales_'+Localidad[1] +'_'+ Localidad[3] + '_RapiPago.csv'

  
        ## abro un archivo csv para lectrau, si no existe, lo creo
        Archivo_RapiPago = open(RutaArchivosCSV, 'w+')


        ## creo un objeto writer para escribir el csv abierto

        csvwriter = csv.writer(Archivo_RapiPago)

        count = 0

        ## por cada registro de la matriz  Localidad_Sucursal_Direccion
        ## guardo una linea dentro del csv
        ## cada linea sera de la forma Localidad, Sucursal, Direccion, Latitud, Longitud
        for registro in Localidad_Sucursal_Direccion:

              if count == 0:
                  header = 'Provincia','Localidad','Sucursal','Direccion','Latitud','Longitud'

                  csvwriter.writerow((header))

                  count += 1

              csvwriter.writerow(Localidad[1],registro)

        Archivo_RapiPago.close()
    
    
fin=time.clock()
print(fin-inicio,' sec.')
##except:
##    fin=time.clock()
##    tiempo=fin-inicio
##    gmail_user = 'esteban.ruiz@taligent.com.ar'  
##    gmail_password = '-----'
##
##    sent_from = gmail_user  
##    to = ['obi@taligent.com.ar']  
##    subject = 'Python Email Test'  
##    body = 'Ha ocurrido un error en la extracion de datos.\n\n\n Estado del programa al momento de la falla:\n'+str(link)+'\n'+str(url)+'\n tiempo de ejecucion: '+str(tiempo)+' sec.\n\n'+'Saludos.'
##
##    email_text = """  
##    %s
##    """ % (body)
##
##    email_text='Subject: {}\n\n{}'.format(subject, email_text)
##    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
##    server.ehlo()
##    server.login(gmail_user, gmail_password)
##    server.sendmail(sent_from, to, email_text)
##    server.close()
##
##    print ('Email sent!');
