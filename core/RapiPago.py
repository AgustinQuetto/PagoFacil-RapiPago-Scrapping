import json, requests, time
from bs4 import BeautifulSoup
from utils import *
from omgeo import Geocoder

with open('rapipago_paths.json') as json_data:
    paths = json.load(json_data)

toPendingFixCount = 0
root = '../Files'
provincesHeader = ['ID', 'PROVINCIA']
localidadesHeader = ['ID', 'ID-PROVINCIA', 'LOCALIDAD']
branchesHeader = ['Localidad','Sucursal','Direccion', 'Horario', 'Latitud', 'Longitud']
dirs(root)
for pd in paths.keys():
    dirs(root+paths[pd])

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
def getBranches(provinceId, localidadId, localidadName, provinceName, extracash=False):
    try:
        fixpath = root+paths['fix']+'/rapipago_fix.csv'
        toFix = []
        g = Geocoder()
        extracash = 'true' if extracash else 'false'
        res = requests.get('https://www.rapipago.com.ar/rapipagoWeb/index.php/resultado_sucursales?prov='+provinceId+'&loc='+localidadId+'&extracash='+extracash)
        if res.status_code != 200:
            raise ValueError('Error solicitando sucursales.') 
        soup = BeautifulSoup(res.text, 'lxml')
        content = soup.find_all('div', class_="w-row accordion_content")
        branches = []
        #chequeo si el sitio posee sucursales
        if content != None:
            for c in content:
                try:
                    global toPendingFixCount
                    withoutError = True
                    title = c.select('.text_expand_drop')[0].get_text()
                    address = c.select('.text_expand_drop')[1].get_text()
                    attentionHour = c.select('.text_horarios_drop')[0].get_text().replace('Horarios de atención:', '').replace('\n', '').replace('   ', '')
                    data = [localidadName, title, address, attentionHour]
                    latlngExt = c.find_all('a')
                    #chequeo si encontro etiquetas de latitud y longitud
                    if len(latlngExt) > 0:
                        latlngExt = str(latlngExt[0])
                        lat = findBetweenR(latlngExt, 'data-lat="', '" data-lng')
                        lng = findBetweenR(latlngExt, 'data-lng="', '" data-marker')
                        data.append(lat)
                        data.append(lng)
                    #al no encontrar o no poseer con exactitud, controla si ya fueron definidas manualmente
                    if len(latlngExt) == 0 or (lat == '0.00000000' or lng == '0.00000000'):
                        fixNotFound = True
                        with open(fixpath, 'r') as f:
                            reader = csv.reader(f)
                            fixList = list(reader)
                        search = [provinceName,localidadName,title,address]
                        for i, lc in enumerate(fixList):
                            concurrence = 0
                            for co in search:
                                if co in lc:
                                    concurrence = concurrence + 1
                            if concurrence == len(search):
                                data = lc[1:len(lc)]
                                fixNotFound = False
                        #no esta la sucursal definida manualmente e intenta geolocalizarla
                        if fixNotFound:
                            try:
                                result = g.geocode(address+', '+localidadName+', Argentina')
                                lat = result['candidates'][0].x
                                lng = result['candidates'][0].y
                            except Exception as e:
                                #no logro geolocalizarla y sera puesta a la lista manual
                                withoutError = False
                                try:
                                    mode = 'a' if os.path.exists(fixpath) else 'w'
                                    listString = ','.join(data)
                                    if len(latlngExt) == 0:
                                        listString = listString + ',0.00000000,0.00000000'
                                    with open(fixpath, mode) as _file:
                                        _file.write('\n'+provinceName+','+(listString))
                                    toPendingFixCount = toPendingFixCount + 1
                                except Exception as e:
                                    print(e)
                    if withoutError:
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
        provinces = getProvinces()
        if len(provinces) < 1:
            raise ValueError('No se obtuvieron provincias.')
        toCSV(root+paths['provincias']+'/CodigoProvincias.csv', provinces, provincesHeader)

        for p in provinces:
            localidades = getLocalidades(p[0])
            if len(localidades) < 1:
                raise ValueError('No se obtuvieron localidades.')
            toCSV(root+paths['localidades']+'/Localidad-'+p[1]+'.csv', localidades, localidadesHeader)

            for loc in localidades:
                branches = getBranches(p[0], loc[0], loc[2], p[1])
                toCSV(root+paths['sucursales']+'/Sucursales_'+p[1]+'_'+loc[2]+'_RapiPago.csv',
                        branches, branchesHeader)

    except Exception as e:
        print(e)

try:
    print('RUNNING')
    start_time = time.time()
    run()
    elapsed_time = time.time() - start_time
    print('Finished: ' + elapsed_time + ' seconds')
    if toPendingFixCount > 0:
        #send email here
        pass
    toPendingFixCount = 0
except Exception as e:
    print(e)
