import json, requests, time
from bs4 import BeautifulSoup
from utils import *

with open('pagofacil_paths.json') as json_data:
    paths = json.load(json_data)

toPendingFixCount = 0
root = '../Files'
provincesHeader = ['ID', 'PROVINCIA']
localidadesHeader = ['ID', 'ID-PROVINCIA', 'LOCALIDAD']
branchesHeader = ['IDSUCURSAL','NRO_AGENTE_PF','NOMBRE','DIRECCION','LOCALIDAD','PROVINCIA',
                    'WESTERN_UNION','ENVIO_NACIONAL','PAGO_FACTURAS','RECARGA_FACIL',
                    'HS_LAV','HS_SABADO','HS_DOMINGO','LATITUD','LONGITUD']
dirs(root)
for pd in paths.keys():
    dirs(root+paths[pd])

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
        return dicted
    except Exception as e:
        print(e)

#funcion que se llama y contiene la ejecucion del programa
def run():
    provinces = getProvinces()
    if len(provinces) < 1:
        raise ValueError('No se obtuvieron provincias.')
    toCSV(root+paths['provincias']+'/CodigoProvincias.csv', provinces, provincesHeader)
    for p in provinces:
        localidades = getLocalidades(p[0])
        if len(localidades) < 1:
            raise ValueError('No se obtuvieron localidades.')
        toCSV(root+paths['localidades']+'/Localidad-'+p[1]+'.csv', localidades, localidadesHeader)
        for l in localidades:
            location = getLocation(p[0], l[1])
            toCSV(root+paths['sucursales']+'/Sucursales_'+p[1]+'_'+l[1]+'_PagoFacil.csv',
                    location, branchesHeader)

try:
    start_time = time.time()
    run()
    elapsed_time = time.time() - start_time
    print(elapsed_time)
except Exception as e:
    print(e)
