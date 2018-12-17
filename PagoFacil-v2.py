import json, requests
from bs4 import BeautifulSoup
from utils import *

#solicita las provincias a rapipago y retorna una lista con todas
def getProvinces():
    try:
        res = requests.get('https://www.e-pagofacil.com/', verify=False)
        if res.status_code != 200:
            raise ValueError('Error solicitando provincias.')
        soup = BeautifulSoup(res.text, 'lxml')
        provincesExtract = soup.find('select', {'name': 'Provincia'}).findChildren('option')
        provincesExtract.pop(0)
        extracted = []
        for item in provincesExtract:
            province = [findBetweenR(str(item), '<option value="', '">'), item.get_text()]
            extracted.append(province)
        return extracted
    except Exception as e:
        print(e)

#solicita las localidades mediante el id de la provincia y retorna una lista
def getLocalidades(provinceId):
    try:
        body = {'idprov': provinceId}
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest'}
        res = requests.post('https://www.e-pagofacil.com/clientes/contacto', verify=False, headers=headers, data=body)
        if res.status_code != 200:
            raise ValueError('Error solicitando localidades.')
        res.encoding = 'utf-8'
        dicted = []
        if res.status_code == 200:
            for item in json.loads(res.text):
                dicted.append([item['id_loca'], item['de_loca']])
            return dicted
        return False
    except Exception as e:
        print(e)

#solicita las localidades mediante el id de la provincia y retorna una lista
def getLocation(provinceId, locationId):
    try:
        res = requests.get('https://www.e-pagofacil.com/backend/intranet/coordenadas.php?p='+provinceId+'&l='+locationId, verify=False)
        dicted = []
        if res.status_code != 200:
            raise ValueError('Error solicitando localizacion e informacion.')
        for item in json.loads(res.text):
            dicted.append(list(item.values()))
        print(dicted)
        return dicted
    except Exception as e:
        print(e)

#funcion que se llama y contiene la ejecucion del programa
def run():
    paths = {
                'localidades': 'localidades_PagoFacil',
                'provincias': 'provincias_PagoFacil',
                'sucursales': 'ArchivosCSV'
            }

    for d in paths.keys():
        dirs(paths[d])
    provinces = getProvinces()
    if len(provinces) < 1:
        raise ValueError('No se obtuvieron provincias.')
    toCSV(paths['provincias']+'/CodigoProvincias.csv', provinces, ['ID', 'PROVINCIA'])
    for p in provinces:
        localidades = getLocalidades(p[0])
        if len(localidades) < 1:
            raise ValueError('No se obtuvieron localidades.')
        toCSV(paths['localidades']+'/Localidad-'+p[1]+'.csv', localidades, ['ID', 'ID-PROVINCIA', 'LOCALIDAD'])
        for l in localidades:
            location = getLocation(p[0], l[1])
            toCSV(paths['sucursales']+'/Sucursales_'+p[1]+'_'+l[1]+'_PagoFacil.csv',
                    location, ['IDSUCURSAL','NRO_AGENTE_PF','NOMBRE','DIRECCION','LOCALIDAD','PROVINCIA',
                    'WESTERN_UNION','ENVIO_NACIONAL','PAGO_FACTURAS','RECARGA_FACIL',
                    'HS_LAV','HS_SABADO','HS_DOMINGO','LATITUD','LONGITUD'])

try:
    run()
except Exception as e:
    print(e)