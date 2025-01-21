# -*- coding: utf-8 -*-
__author__ = 'Lucianinski Orange'

import requests
from bs4 import BeautifulSoup
import csv
import time

def obtener_urls_desde_archivo(ruta_archivo):
    """
    Lee las URLs desde un archivo de texto y las devuelve como una lista.
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            urls = [line.strip() for line in archivo if line.strip()]
        return urls
    except Exception as e:
        print(f"Error al leer el archivo de URLs: {e}")
        return []

def extraer_datos_de_pagina(url):
    """
    Extrae los datos de una página de producto de AliExpress.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Lanza una excepción si el status code no es 200
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión para la URL {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extraer el nombre del producto
    try:
        producto = soup.find('h1', {'class': 'product-name'}).get_text(strip=True)
    except AttributeError:
        producto = 'N/A'

    # Extraer las categorías
    categorias = []
    try:
        categorias_div = soup.find('div', {'class': 'module m-sop m-sop-crumb'})
        if categorias_div:
            categorias = [catego.get_text(strip=True) for catego in categorias_div.find_all('a')]
    except Exception as e:
        print(f"Error al extraer categorías para {url}: {e}")

    # Extraer el precio
    try:
        precio = soup.find('span', {'id': 'j-sku-price'}).get_text(strip=True)
    except AttributeError:
        precio = 'N/A'

    # Extraer la URL de la imagen principal
    try:
        image_div = soup.find('div', {'class': 'ui-image-viewer-thumb-wrap'})
        if image_div:
            link = image_div.find('img').get('src')
            if link.startswith('//'):
                link = 'https:' + link
            elif not link.startswith('http'):
                link = 'https://www.aliexpress.com' + link
        else:
            link = 'N/A'
    except Exception as e:
        print(f"Error al extraer la imagen para {url}: {e}")
        link = 'N/A'

    # Extraer colores
    colores = []
    try:
        colores_li = soup.find_all('li', {'class': 'item-sku-color'})
        colores = [color.find('span').get_text(strip=True) for color in colores_li if color.find('span')]
    except Exception as e:
        print(f"Error al extraer colores para {url}: {e}")

    # Extraer tallas
    tallas = []
    try:
        tallas_ul = soup.find_all('ul', {'class': 'sku-attr-list util-clearfix'})
        for talla_ul in tallas_ul:
            talla_span = talla_ul.find_all('span')
            for ts in talla_span:
                tallas.append(ts.get_text(strip=True))
    except Exception as e:
        print(f"Error al extraer tallas para {url}: {e}")

    # Extraer dimensiones
    dimensiones = []
    try:
        especificaciones_ul = soup.find_all('ul', {'class': 'product-packaging-list util-clearfix'})
        for espec_ul in especificaciones_ul:
            espec_span = espec_ul.find_all('span')
            for es in espec_span:
                dimensiones.append(es.get_text(strip=True))
    except Exception as e:
        print(f"Error al extraer dimensiones para {url}: {e}")

    return {
        'producto': producto,
        'categorias': ', '.join(categorias),
        'precio': precio,
        'imagen': link,
        'colores': ', '.join(colores),
        'tallas': ', '.join(tallas),
        'dimensiones': ', '.join(dimensiones),
        'url': url
    }

def guardar_datos_en_csv(datos, ruta_archivo):
    """
    Guarda los datos en un archivo CSV.
    """
    archivo_existe = os.path.isfile(ruta_archivo)
    try:
        with open(ruta_archivo, 'a', newline='', encoding='utf-8') as archivo_csv:
            writer = csv.writer(archivo_csv)
            if not archivo_existe:
                writer.writerow(['ID', 'Nombre', 'Categorías', 'Precio', 'Imagen', 'Colores', 'Tallas', 'Dimensiones', 'URL'])
            writer.writerow([
                datos['id'],
                datos['producto'],
                datos['categorias'],
                datos['precio'],
                datos['imagen'],
                datos['colores'],
                datos['tallas'],
                datos['dimensiones'],
                datos['url']
            ])
    except Exception as e:
        print(f"Error al escribir en el archivo CSV: {e}")

def main():
    ruta_archivo_urls = input("Escribe la ruta del archivo de listado de URLs en TXT: ")
    urls = obtener_urls_desde_archivo(ruta_archivo_urls)
    if not urls:
        print("No se encontraron URLs en el archivo proporcionado.")
        return

    max_pages = len(urls)
    contador = 0

    with open('productoAliexpress.csv', 'w', newline='', encoding='utf-8') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerow(['ID', 'Nombre', 'Categorías', 'Precio', 'Imagen', 'Colores', 'Tallas', 'Dimensiones', 'URL'])

        for url in urls:
            datos = extraer_datos_de_pagina(url)
            if datos:
                datos['id'] = contador + 1
                guardar_datos_en_csv(datos, 'productoAliexpress.csv')
                contador += 1
                print(f"Producto {contador}/{max_pages} procesado.")
            else:
                print(f"Producto no procesado: {url}")

            time.sleep(1)  # Esperar un segundo entre peticiones para no sobrecargar el servidor

    print("Proceso terminado. Los datos se han guardado en 'productoAliexpress.csv'.")

if __name__ == "__main__":
    main()
