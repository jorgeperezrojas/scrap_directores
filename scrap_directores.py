import csv
import re
import bs4
import mechanicalsoup
import argparse
from selenium import webdriver
from time import sleep
from collections import defaultdict
from datetime import datetime


def get_url_empresas(
    url_base='http://www.cmfchile.cl', 
    url_table='http://www.cmfchile.cl/portal/principal/605/w3-propertyvalue-18591.html',
    tries=100,
    trh=20,
    initial_politeness=1,
    mult_politeness=1.5,
    max_politeness=60,
    verbose=True
    ):

    if verbose:
        print('Comenzando...')

    politeness = initial_politeness

    for t in range(tries+1):
        if t == tries:
            raise Exception('No fue posible obtener los links a datos de empresas!')

        print('Intento',t)
        driver = webdriver.PhantomJS()
        driver.get(url_table)
        html = driver.page_source
        page = bs4.BeautifulSoup(html,'lxml')
        div_f = page.find('div',{'id':'listado_fiscalizados'})
        trs = div_f.findAll('tr')
        if len(trs) > trh:
            if verbose:
                print('Links obtenidos.')
            break
        else:
            if verbose:
                print('Intento',t,'falló')
                print('Esperando',str(politeness)[:5],'seg')
            sleep(politeness)
            if politeness < max_politeness:
                politeness = politeness * mult_politeness

    if verbose:
        print('Ahora formatea')    

    lista_empresas = []
    lista_links = []

    for tr in trs:
        tds = tr.findAll('td')
        if len(tds) < 3:
            continue
        else:
            a_rut = tds[0].find('a')
            a_empresa = tds[1].find('a')
            
            rut = a_rut.text
            empresa = a_empresa.text
            link = a_rut.get('href')

            lista_empresas.append((rut,empresa))
            lista_links.append(url_base+link)

    
    if verbose:
        print('Listo')
    return lista_empresas, lista_links
    
def setea_pestania(lista_links,pestania=46):
    nueva_lista_links = []
    for link in lista_links:
        nuevo_link = re.sub('pestania=[0-9]+','pestania='+str(pestania),link)
        nueva_lista_links.append(nuevo_link)
    return nueva_lista_links

def get_data_directores(lista_empresas,lista_links,verbose=True):
    browser = mechanicalsoup.Browser(soup_config={'features':'lxml'})
    directorio = {}
    for (rut,nombre),  url in zip(lista_empresas, lista_links):
        if verbose:
            print('Obteniendo datos para',nombre)
        page = browser.get(url)
        trs = page.soup.findAll('tr')
        dir_data = []
        for tr in trs:
            tds = tr.findAll('td')
            if len(tds) < 4:
                continue
            else:
                rut_dir = tds[0].text
                nombre_dir = tds[1].text
                cargo_dir = tds[2].text
                fecha_nombramiento = tds[3].text

                director = {}
                director['rut'] = rut_dir
                director['nombre'] = nombre_dir
                director['cargo'] = cargo_dir
                director['fecha_nombramiento'] = fecha_nombramiento

                dir_data.append(director)
        directorio[rut] = dir_data
    return directorio

def get_directorios_por_persona(lista_empresas,directorio):
    dir_per = defaultdict(list)

    for rut_empresa, nombre_empresa in lista_empresas:
        for director in directorio[rut_empresa]:
            key = (director['rut'],director['nombre'])

            data = {}
            data['rut_empresa'] = rut_empresa
            data['nombre_empresa'] = nombre_empresa
            data['cargo'] = director['cargo']
            data['fecha_nombramiento'] = director['fecha_nombramiento']

            dir_per[key].append(data)
    return dir_per


def main():
    parser = argparse.ArgumentParser(description='Obtiene datos de directores.')
    parser.add_argument('-o', '--outFile', metavar='O', type=str, nargs='?',
                        default='directores', help='Archivo donde guardar datos de directores.')
    parser.add_argument('-od', '--outFileDetalle', metavar='D', type=str, nargs='?',
                        default='detalle_directores', help='Archivo donde guardar de directorios para cada persona.')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='Show in detail what the script is doing.')

    args = parser.parse_args()
    out_csv_file = args.outFile
    out_detalle_csv_file = args.outFileDetalle
    verbose = args.verbose

    suffix = '_' + str(datetime.now()) + '.csv'
    out_csv_file += suffix
    out_detalle_csv_file += suffix

    le, ll = get_url_empresas(verbose=verbose)
    nll = setea_pestania(ll)
    directorio = get_data_directores(le,nll,verbose=verbose)

    if verbose:
        print('Guardando directores en', out_csv_file)

    with open(out_csv_file, 'w') as out_csv:
        wr = csv.writer(out_csv, quoting=csv.QUOTE_ALL)

        for (rut_empresa,nombre_empresa) in le:
            for director in directorio[rut_empresa]:
                data = [
                    rut_empresa,
                    nombre_empresa,
                    director['rut'],
                    director['nombre'],
                    director['cargo'],
                    director['fecha_nombramiento']
                ]
                wr.writerow(data)

    if verbose:
        print('Guardando detalle directores en', out_detalle_csv_file)

    dir_emp = get_directorios_por_persona(le,directorio)

    with open(out_detalle_csv_file, 'w') as out_detalle_csv:
        wr = csv.writer(out_detalle_csv, quoting=csv.QUOTE_ALL)
        for (rut, nombre) in dir_emp:
            data = [rut,nombre]
            num_dirs = len(dir_emp[(rut,nombre)])
            data.append(num_dirs)
            for dir_data in dir_emp[(rut,nombre)]:
                data += [
                    dir_data['cargo'],
                    dir_data['fecha_nombramiento'],
                    dir_data['rut_empresa'],
                    dir_data['nombre_empresa']
                ]
            wr.writerow(data)


if __name__ == '__main__':
    main()
