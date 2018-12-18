import json, requests, time
from bs4 import BeautifulSoup
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
def getBranches(provinceId, localidadId, localidadName, extracash=False):
    try:
        extracash = 'true' if extracash else 'false'
        res = requests.get('https://www.rapipago.com.ar/rapipagoWeb/index.php/resultado_sucursales?prov='+provinceId+'&loc='+localidadId+'&extracash='+extracash)
        if res.status_code != 200:
            raise ValueError('Error solicitando sucursales.') 
        soup = BeautifulSoup(res.text, 'lxml')
        content = soup.find_all('div', class_="w-row accordion_content")
        branches = []
        if content != None:
            for c in content:
                try:
                    title = c.select('.text_expand_drop')[0].get_text()
                    address = c.select('.text_expand_drop')[1].get_text()
                    attentionHour = c.select('.text_horarios_drop')[0].get_text().replace('Horarios de atención:', '').replace('\n', '').replace('   ', '')
                    data = [localidadName, title, address, attentionHour]
                    latlngExt = c.find_all('a')
                    if len(latlngExt) > 0:
                        latlngExt = str(latlngExt[0])
                        lat = findBetweenR(latlngExt, 'data-lat="', '" data-lng')
                        lng = findBetweenR(latlngExt, 'data-lng="', '" data-marker')
                        data.append(lat)
                        data.append(lng)
                    branches.append(data)
                except Exception as e:
                    print(e)
            return branches
        return []
    except Exception as e:
        print(e)

#funcion que se llama y contiene la ejecucion del programa
def run():
    try:
        paths = {
                    'files': '..\Files',
                    'localidades': '..\Files\localidades_Rapipago',
                    'provincias': '..\Files\provincias_Rapipago',
                    'sucursales': '..\Files\ArchivosCSV_Rapipago'
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
                branches = getBranches(p[0], loc[0], loc[2])
                toCSV(paths['sucursales']+'/Sucursales_'+p[1]+'_'+loc[2]+'_RapiPago.csv',
                        branches, ['Localidad','Sucursal','Direccion', 'Horario', 'Latitud', 'Longitud'])

    except Exception as e:
        print(e)

try:
    print('RUNNING '+str(time.time()))
    start_time = time.time()
    run()
    elapsed_time = time.time() - start_time
    print(elapsed_time)
except Exception as e:
    print(e)
