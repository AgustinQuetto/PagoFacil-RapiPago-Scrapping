import re, csv, os

#escribe a CSV utilizando el path, una lista y opcionalmente la primera fila como cabezal
def toCSV(file_path, vector, head=False):
    with open(file_path, 'w') as outcsv:
        writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        if head and isinstance(head, list):
            writer.writerow(head)
        for item in vector:
            writer.writerow(item)

#extrae un substring de un string
def findBetweenR(s, first, last):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

#si el directorio no existe, lo crea
def dirs(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)