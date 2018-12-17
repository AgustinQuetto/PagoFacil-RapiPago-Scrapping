import json, requests
from bs4 import BeautifulSoup
from html_table_extractor.extractor import Extractor
from utils import *

#solicita las provincias a rapipago y retorna una lista con todas
def getProvinces():
    try:
        res = requests.get('https://www.rapipago.com.ar/rapipagoWeb/index.php')
        if res.status_code != 200:
            raise ValueError('Error solicitando provincias.')
        soup = BeautifulSoup(res.text, 'lxml')
        provincesExtract = soup.select('#field-provincia > option')
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
        res = requests.get('https://www.rapipago.com.ar/rapipagoWeb/index.php/services/localidades/'+provinceId)
        if res.status_code != 200:
            raise ValueError('Error solicitando localidades.')
        localidades = json.loads(res.text)['data']
        clean = []
        for loc in localidades:
            clean.append([loc['id_prov_partido_localidad'], provinceId, loc['descripcion']])
        return clean
    except Exception as e:
        print(e)

#solicita las sucursales mediante el id de provincia y localidad, extrayendo cada una del contenido del sitio
#retorna una lista
def getBranches(provinceId, localidadId, extracash=False):
    try:
        extracash = 'true' if extracash else 'false'
        res = requests.get('https://www.rapipago.com.ar/rapipagoWeb/index.php/resultado_sucursales?prov='+provinceId+'&loc='+localidadId+'&extracash='+extracash)
        if res.status_code != 200:
            raise ValueError('Error solicitando sucursales.') 
        soup = BeautifulSoup(res.text, 'lxml')
        tableContent = soup.select('.tableizer-table')
        extractor = Extractor(str(tableContent))
        extractor.parse()
        listed = extractor.return_list()
        return listed
    except Exception as e:
        print(e)

#retorna una nueva lista con los datos finales necesarios de las sucursales extraidas en bruto
def necessaryBranches(branches):
    b = []
    for br in branches:
        b.append([br[1], br[2], br[3]])
    return b

#funcion que se llama y contiene la ejecucion del programa
def run():
    try:
        paths = {
                    'localidades': 'localidades_Rapipago',
                    'provincias': 'provincias_Rapipago',
                    'sucursales': 'ArchivosCSV_Rapipago'
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

            for loc in localidades:
                branches = getBranches(p[0], loc[0])
                #header = branches[0]
                branches.pop(0)
                necessary = necessaryBranches(branches)
                toCSV(paths['sucursales']+'/Sucursales_'+p[1]+'_'+loc[2]+'_RapiPago.csv',
                        necessary, ['Localidad','Sucursal','Direccion'])

    except Exception as e:
        print(e)

try:
    run()
except Exception as e:
    print(e)