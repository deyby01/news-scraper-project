import requests
from bs4 import BeautifulSoup
import csv # Usamos este modulo para guardar datos en archivos .csv
import os # Añade esta importación al inicio de tu scraper.py si no está

# Por ahora voy a usar una URL de prueba para request luego agregare la url real de donde
# quiero obtener los datos para el scraper 'https://quotes.toscrape.com/' es para pruebas
# usare la seccion de citas para simular noticias
URL_NOTICIAS = 'https://quotes.toscrape.com/'

def obtener_contenido_pagina(url):
    """
    Obtiene el contenido HTML de una página web.

    Args:
        url (str): La URL de la página web a obtener.
        
    Returns:
        str: El contenido HTML de la página como texto, o None si ocurre un error.
    """
    try:
        # Hacemos la peticion GET
        # Añadimos un User-Agent para simular un navegador y evitar bloqueos por parte del servidor
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        respuesta = requests.get(url, headers=headers, timeout=10) # Timeout de 10 segundos
        
        # Verificamos si la respuesta fue exitosa (estado 200)
        respuesta.raise_for_status() # Esto lanzara una excepcion HTTPError para codigos 4xx y 5xx
        
        print(f"Página obtenida correctamente: {url}")
        return respuesta.text  # Retornamos el contenido HTML de la página
        
    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP al obtener la página: {http_err} - Status code: {respuesta.status_code if 'respuesta' in locals() else 'N/A'}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Error de conexión al obtener la página: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout al obtener la página: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Ocurrio un error inesperado al obtener la página: {req_err}")
    
    return None # Retornamos None si hubo algun error


def extraes_citas_autores(html_content):
    """
    Extrae citas y autores del contenido HTML de la página.

    Args:
        html_content (str): El contenido HTML de la página.
    
    Returns:
        list: Una lista de diccionarios, donde cada diccionario contiene
            'texto' (la cita) y 'autor'. Retorna lista vacia si no se encuentran.
    """
    citas_extraidas = []
    if not html_content:
        return citas_extraidas
    
    try:
        # Creamos un objeto BeautifulSoup para parsear el HTML
        # 'lxml' es un parser rapido. Alternativamente, podrias usar 'html.parser' (incorporado en Python)
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Buscamos todos los div con la clase 'quote' que contienen las citas
        # Nota: Class_ (con guion bajo) se usa por que class es una palabra reservada en Python
        contenedores_citas = soup.find_all('div', class_='quote')
        
        print(f"\nSe encontraron {len(contenedores_citas)} citas en la página.")
        
        for contenedor in contenedores_citas:
            # Dentro de cada div.quote, encontramos el span.text y el small.author
            texto_tag = contenedor.find('span', class_='text')
            autor_tag = contenedor.find('small', class_='author')
            
            # Verificamos que encontramos los tags antes de acceder a .text
            if texto_tag and autor_tag:
                texto_cita = texto_tag.text.strip()  # .text obtiene el contenido, .strip() limpia espacios extra
                nombre_autor = autor_tag.text.strip()
                
                citas_extraidas.append({'texto': texto_cita, 'autor': nombre_autor})
            
            else:
                print("Advertencia: No se pudo encontrar texto o autor en uno de los contenedores de cita.")

    except Exception as e:
        print(f"Ocurrió un error durante el parseo del HTML: {e}")
    
    return citas_extraidas  # Retornamos la lista de citas extraidas


def guardar_datos_csv(datos, nombre_archivo_base='citas_extraidas.csv'):
    """
    Guarda una lista de diccionarios enun archivo CSV.

    Args:
        datos (list): Una lista de diccionarios para guardar.
        nombre_archivo (str, optional): El nombre del archivo CSV. 
                                        Defaults to 'citas_extraidas.csv'.
    """
    if not datos:
        print('No hay datos para guardar.')
        return
    
    # Las llaves del primer diccionario se usaran como encabezados (fieldnames)
    # Asumimos que todos los diccionarios tienen las mismas llaves.
    fieldnames = datos[0].keys()
    
    # Definimos la ruta de salida dentro del contenedor
    directorio_salida = "output" # Este es /app/output dentro del contenedor
    # os.makedirs(directorio_salida, exist_ok=True) # Ya lo creamos en el Dockerfile
                                                 # pero no está de más asegurarse si se corre localmente
    
    # Es mejor si importamos os para crear la carpeta si no existe (para ejecución local)
    # y para unir rutas de forma segura
    if not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)

    ruta_completa_archivo = os.path.join(directorio_salida, nombre_archivo_base)
    
    try:
        with open(ruta_completa_archivo, 'w', newline='', encoding='utf-8') as csvfile:
            # 'w' para modo escritura.
            # newline='' para evitar filas vacias extra en Windows.
            # encodig='utf-8' para manejar caracteres especiales.
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader() # Escribe la fila de encabezados
            writer.writerows(datos) # Escribe todas las filas de datos

        print(f'\nDatos guardados exitosamente en el archivo {ruta_completa_archivo}')
    except IOError:
        print(f'Error de E/S: No se pudo escribir en el archivo {ruta_completa_archivo}')
    except Exception as e:
        print(f'Ocurrió un error al guardar los datos en CSV: {e}')
        
        

# ----- Bloque Principal para probar la funcion -----
if __name__ == "__main__":
    print("Inciando el extractor de noticias...")
    contenido_html = obtener_contenido_pagina(URL_NOTICIAS)
    
    if contenido_html:
        # Ya no imprimimos el HTML aqui, sino que lo pasamos a la nueva funcion
        #print("\nPrimeros 500 caracteres del HTML obtenido:")
        #print(contenido_html[:500])
        
        lista_citas = extraes_citas_autores(contenido_html)
        
        if lista_citas:
            print("\n----Citas extraidas ----")
            for i, cita_info in enumerate(lista_citas, start=1):
                print(f'\nCita {i}:')
                print(f' Texto: {cita_info["texto"]}')
                print(f' Autor: {cita_info["autor"]}')
                
            # Llamamos a la nueva funcion para guardar los datos
            guardar_datos_csv(lista_citas) # Podriamos cambiar nombre, pero lo dejamos por defecto
        
        else:
            print("\nNo se pudieron extraer citas de la página.")
        
    else:
        print("\nNo se pudo obtener el contenido de la página.")
        
    print("\n---- Fin del Script ----")