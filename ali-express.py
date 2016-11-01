# -*- coding: utf-8 -*-
__author__ = 'Lucianinski Orange'

from bs4 import BeautifulSoup
import requests
import urllib
import csv
urlBase = "http://es.aliexpress.com/"
maxPages = 21
numlineas = maxPages - 1
counter = 0
# Encabezado
archivo=open('productoAliexpress.txt','w')
archivo.write("ID|Name|Categories|Price|Imagen|Color|Tallas|Dimensiones|Url\n")
archivo.close() 
unaurl = input("Escribe la URL de tu archivo de listado en TXT, debe tener exactamente %s entradas: " %(numlineas)) 

for i in range(0,maxPages):
    # Construyo la URL
    infile = open(unaurl, 'r')
    # Mostramos por pantalla lo que leemos desde el fichero
    print('>>> Se está leyendo el fichero, espera...')
    try:
        url = infile.readlines()[i]
    # Cerramos el fichero.
        infile.close()
        # Realizamos la petición a la web
        req = requests.get(url)
        # Comprobamos que la petición nos devuelve un Status Code = 200
        statusCode = req.status_code
        if statusCode == 200:
            # Pasamos el contenido HTML de la web a un objeto BeautifulSoup()
            html = BeautifulSoup(req.text, 'html.parser')
            # Obtenemos todos los divs donde estan las entradas
            entradas = html.find_all('div',{'class':'official-content detail-page-content'})
            # Recorremos todas las entradas para extraer el título, autor y fecha
            for entrada in entradas:

                counter += 1
                producto = entrada.find('h1',{'class' : 'product-name'}).text
                categorias = entrada.find_all('div',{'class' : 'module m-sop m-sop-crumb'})
                for categoria in categorias:
                    catego = categoria.find('b').text
                precio = entrada.find('span',{'id' : 'j-sku-price'}).text
                imageLinks = entrada.find_all('div', {'class':'ui-image-viewer-thumb-wrap'})
                for imageLink in imageLinks:
                    link = imageLink.find_all('img')[0].get('src')
                colores = entrada.find_all('li',{'class' : 'item-sku-color'})
                for color in colores:
                    thecolor = color.find_all('span')
                tallas = entrada.find_all('ul',{'class' : 'sku-attr-list util-clearfix'})
                for talla in tallas:
                    thetalla = talla.find_all('span')
                especificaciones = entrada.find_all('ul',{'class' : 'product-packaging-list util-clearfix'})
                for especificacion in especificaciones:
                    dimensiones = especificacion.find_all('span')
                # Imprimo el Título, Autor y Fecha de las entradas
                try:
                    archivo=open('productoAliexpress.txt','a')
                    archivo.write("%d|%s|%s|%s|%s|%s|%s|%s|%s" %(counter,producto,catego,precio,link,thecolor,thetalla,dimensiones,url))
                    archivo.close()
                except:
                    print ("Ha habido algún error. No se pudo crear el archivo TXT")
        else:
            print('Fin del programa')
            # Si ya no existe la página y me da un 400
            break
    except:
        print ("Hubo algún error o no se pudo leer la direccion")
    
    print('>>> Terminado')
