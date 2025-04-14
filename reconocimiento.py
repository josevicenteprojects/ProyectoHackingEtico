import socket
import requests
from datetime import datetime
import json
import subprocess
import sys
import concurrent.futures
import time
import ssl
import urllib3

urllib3.disable_warnings()

def banner():
    """Muestra un banner decorativo para el script."""
    print("""
    ╔════════════════════════════════════════╗
    ║     Herramienta de Reconocimiento      ║
    ║          Proyecto Educativo            ║
    ╚════════════════════════════════════════╝
    """)

def analizar_headers_seguridad(url):
    """
    Analiza los headers de seguridad de la respuesta HTTP.
    
    Esta función busca headers específicos de seguridad que comúnmente se
    implementan como buenas prácticas (HSTS, CSP, X-Frame-Options, etc.)
    
    Args:
        url (str): URL a analizar
        
    Returns:
        dict: Diccionario con los headers de seguridad encontrados
    """
    # Definimos los headers de seguridad que nos interesa buscar
    headers_seguridad = {
        'Strict-Transport-Security': 'No presente',
        'Content-Security-Policy': 'No presente',
        'X-Frame-Options': 'No presente',
        'X-Content-Type-Options': 'No presente',
        'X-XSS-Protection': 'No presente',
        'Referrer-Policy': 'No presente'
    }
    
    try:
        # Realizamos la petición con un timeout para evitar bloqueos
        response = requests.get(url, verify=False, 
                              headers={'User-Agent': 'Mozilla/5.0'}, 
                              timeout=5)
        
        # Verificamos si cada header de seguridad está presente
        for header in headers_seguridad.keys():
            if header in response.headers:
                headers_seguridad[header] = response.headers[header]
        
        return headers_seguridad
    except Exception as e:
        # En caso de error, devolvemos un diccionario con el error
        return {'Error': str(e)}

def obtener_info_dominio(dominio):
    """
    Obtiene información básica del dominio mediante una petición HTTP.
    
    Esta función analiza los headers de la respuesta para identificar información
    sobre el servidor, tecnologías utilizadas, etc.
    
    Args:
        dominio (str): Dominio a analizar
        
    Returns:
        dict: Diccionario con la información obtenida
    """
    print("\n[+] Obteniendo información del dominio...")
    try:
        # Usamos un User-Agent común para evitar restricciones
        response = requests.get(f'https://{dominio}', timeout=5, verify=False,
                              headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        
        # Extraemos información relevante de la respuesta
        return {
            'dominio': dominio,
            'servidor': response.headers.get('Server', 'No disponible'),
            'tecnologias': response.headers.get('X-Powered-By', 'No disponible'),
            'status_code': response.status_code,
            'headers': dict(response.headers)
        }
    except Exception as e:
        # Manejo de errores para evitar que el script se detenga
        return {
            'dominio': dominio,
            'servidor': 'Error',
            'tecnologias': 'Error',
            'status_code': 'Error',
            'headers': {'error': str(e)}
        }

def obtener_ip(dominio):
    """
    Resuelve la dirección IP de un dominio usando el módulo socket.
    
    Args:
        dominio (str): Dominio a resolver
        
    Returns:
        str: Dirección IP o None si no se pudo resolver
    """
    try:
        # Usamos gethostbyname de socket para la resolución DNS
        return socket.gethostbyname(dominio)
    except Exception:
        return None

def verificar_subdominio(subdominio, dominio_base):
    """
    Verifica si un subdominio existe y es accesible.
    
    Esta función combina resolución DNS y verificación HTTP para determinar
    si un subdominio existe y responde a peticiones.
    
    Args:
        subdominio (str): Subdominio a verificar (sin el dominio base)
        dominio_base (str): Dominio base (ej. 'ejemplo.com')
        
    Returns:
        dict: Información del subdominio o None si no existe
    """
    # Construimos el nombre de dominio completo
    dominio_completo = f"{subdominio}.{dominio_base}"
    
    # Primero verificamos si el DNS resuelve
    ip = obtener_ip(dominio_completo)
    
    if ip:
        try:
            # Si hay IP, intentamos una conexión HTTP
            response = requests.get(f"https://{dominio_completo}", timeout=2, verify=False,
                                  headers={'User-Agent': 'Mozilla/5.0'})
            return {
                'subdominio': dominio_completo,
                'ip': ip,
                'status_code': response.status_code
            }
        except:
            # Si hay errores HTTP pero el DNS resuelve, lo reportamos igualmente
            return {
                'subdominio': dominio_completo,
                'ip': ip,
                'status_code': 'No accesible'
            }
    # Si el DNS no resuelve, el subdominio no existe o no es público
    return None

def buscar_subdominios(dominio):
    """
    Busca subdominios utilizando una lista predefinida y multithreading.
    
    Esta función carga una lista de subdominios comunes desde un archivo y
    verifica cada uno en paralelo para mejorar el rendimiento.
    
    Args:
        dominio (str): Dominio base para la búsqueda
        
    Returns:
        list: Lista de subdominios encontrados
    """
    print("\n[+] Buscando subdominios (esto puede tomar unos minutos)...")
    subdominios_encontrados = []
    
    try:
        # Cargamos la lista de subdominios comunes
        with open('subdominios_comunes.txt', 'r') as file:
            subdominios = file.read().splitlines()
        
        # Implementación de multithreading para mejorar rendimiento
        # Esta es la parte más compleja: ejecutamos múltiples verificaciones en paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Creamos un futuro para cada subdominio a verificar
            futuros = [executor.submit(verificar_subdominio, subdominio, dominio) 
                      for subdominio in subdominios]
            
            # Procesamos los resultados a medida que se completan
            for futuro in concurrent.futures.as_completed(futuros):
                resultado = futuro.result()
                if resultado:
                    subdominios_encontrados.append(resultado)
                    print(f"[+] Encontrado: {resultado['subdominio']} ({resultado['ip']})")
        
        return subdominios_encontrados
    except Exception as e:
        print(f"[!] Error en la búsqueda de subdominios: {str(e)}")
        return []

def obtener_info_adicional(dominio):
    """
    Obtiene información adicional del dominio usando nslookup.
    
    Args:
        dominio (str): Dominio a consultar
        
    Returns:
        str: Resultado de la consulta nslookup
    """
    print("[+] Obteniendo información adicional mediante nslookup...")
    try:
        # Ejecutamos nslookup como proceso externo y capturamos su salida
        resultado = subprocess.run(['nslookup', dominio], capture_output=True, text=True)
        return resultado.stdout
    except Exception as e:
        return f"Error al obtener información adicional: {str(e)}"

def buscar_info_empleados(empresa, limite=10):
    """
    Simula una búsqueda ética de información pública sobre empleados.
    
    En un proyecto real, este código podría implementar técnicas de web scraping
    ético para analizar perfiles públicos profesionales, siguiendo las mejores
    prácticas y términos de servicio de las plataformas.
    
    Args:
        empresa (str): Nombre de la empresa objetivo
        limite (int): Número máximo de perfiles a analizar
        
    Returns:
        dict: Información agregada sobre roles, tecnologías y departamentos
    """
    print(f"\n[+] Buscando información pública sobre empleados de {empresa}...")
    
    # NOTA: Esta es una simulación con fines educativos
    # En un proyecto real implementaríamos técnicas de OSINT éticas
    
    # Estructura de datos para almacenar información agregada
    # No almacenamos información personal específica por razones éticas
    info_empleados = {
        "roles_comunes": [
            "Software Engineer", 
            "Data Scientist",
            "Security Engineer",
            "Network Administrator",
            "DevOps Engineer",
            "UI/UX Designer"
        ],
        "tecnologias_mencionadas": [
            "Python", "Java", "AWS", "Kubernetes",
            "TensorFlow", "React", "Angular",
            "Docker", "Jenkins", "Terraform"
        ],
        "departamentos_identificados": [
            "Autopilot", "Infotainment", "Security",
            "Cloud Infrastructure", "Manufacturing Systems",
            "Solar Energy", "Vehicle Software"
        ]
    }
    
    # Simulamos un retardo para representar el tiempo de procesamiento
    time.sleep(2)
    
    print("[+] Análisis de información pública de empleados completado")
    return info_empleados

def escaneo_basico_puertos(dominio, puertos_comunes=[80, 443, 8080, 22]):
    """
    Realiza un escaneo básico y ético de puertos comunes.
    
    Esta función solo verifica puertos estándar web y SSH por razones educativas.
    Utiliza una técnica no intrusiva y con baja tasa de solicitudes.
    
    Args:
        dominio (str): Dominio a escanear
        puertos_comunes (list): Lista de puertos a verificar
        
    Returns:
        dict: Estado de cada puerto analizado
    """
    print(f"\n[+] Realizando escaneo básico de puertos para {dominio}...")
    resultados = {}
    
    for puerto in puertos_comunes:
        try:
            # Creamos un socket para cada puerto
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # Timeout corto para no bloquear
            
            # Intentamos conectarnos al puerto
            resultado = sock.connect_ex((dominio, puerto))
            if resultado == 0:
                resultados[puerto] = "Abierto"
            else:
                resultados[puerto] = "Cerrado/Filtrado"
                
            sock.close()
            
            # Añadimos un pequeño retardo para ser respetuosos
            time.sleep(0.5)
            
        except Exception as e:
            resultados[puerto] = f"Error: {str(e)}"
    
    return resultados

def mostrar_resultados(resultados):
    """
    Muestra los resultados en un formato legible.
    
    Args:
        resultados (dict): Diccionario con los resultados del análisis
    """
    print("\n" + "="*50)
    print("RESULTADOS DEL RECONOCIMIENTO")
    print("="*50)
    
    print(f"\nFecha de análisis: {resultados['fecha_analisis']}")
    print(f"Dominio: {resultados['dominio_info']['dominio']}")
    print(f"IP principal: {resultados['ip']}")
    
    print("\nInformación del servidor:")
    print(f"- Servidor: {resultados['dominio_info']['servidor']}")
    print(f"- Tecnologías: {resultados['dominio_info']['tecnologias']}")
    
    print("\nHeaders de Seguridad:")
    if isinstance(resultados['headers_seguridad'], dict):
        for header, valor in resultados['headers_seguridad'].items():
            print(f"- {header}: {valor}")
    else:
        print("Error al obtener headers de seguridad")
    
    print("\nSubdominios encontrados:")
    for subdominio in resultados['subdominios']:
        print(f"- {subdominio['subdominio']} ({subdominio['ip']})")
    
    print("\nPuertos analizados:")
    for puerto, estado in resultados['puertos'].items():
        print(f"- Puerto {puerto}: {estado}")
    
    print("\nInformación sobre empleados (análisis agregado):")
    print("- Roles comunes detectados:")
    for rol in resultados['info_empleados']['roles_comunes'][:5]:  # Limitamos a 5 para no saturar
        print(f"  * {rol}")
    
    print("- Tecnologías mencionadas:")
    for tech in resultados['info_empleados']['tecnologias_mencionadas'][:5]:
        print(f"  * {tech}")
    
    print("\nInformación adicional (nslookup):")
    print(resultados['info_adicional'])

def main():
    """Función principal que coordina el proceso de reconocimiento."""
    banner()
    
    # Dominio objetivo
    dominio = "tesla.com"
    print(f"\nIniciando reconocimiento de {dominio}")
    print("="*50)
    
    # Fases de reconocimiento
    # 1. Información del dominio principal
    info_dominio = obtener_info_dominio(dominio)
    
    # 2. Resolución de IP
    ip = obtener_ip(dominio)
    
    # 3. Búsqueda de subdominios
    subdominios = buscar_subdominios(dominio)
    
    # 4. Análisis de headers de seguridad
    headers_seguridad = analizar_headers_seguridad(f'https://{dominio}')
    
    # 5. Información adicional DNS
    info_adicional = obtener_info_adicional(dominio)
    
    # 6. Búsqueda de información sobre empleados
    info_empleados = buscar_info_empleados("Tesla")
    
    # 7. Escaneo básico de puertos
    puertos = escaneo_basico_puertos(dominio)
    
    # Agrupamos todos los resultados
    resultados = {
        'fecha_analisis': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'dominio_info': info_dominio,
        'ip': ip,
        'subdominios': subdominios,
        'headers_seguridad': headers_seguridad,
        'info_adicional': info_adicional,
        'info_empleados': info_empleados,
        'puertos': puertos
    }
    
    # Guardamos resultados en un archivo JSON
    with open('resultados_reconocimiento.json', 'w') as f:
        json.dump(resultados, f, indent=4)
    
    # Mostramos los resultados en la consola
    mostrar_resultados(resultados)
    print("\n[+] Análisis completado. Resultados guardados en 'resultados_reconocimiento.json'")

if __name__ == "__main__":
    main() 