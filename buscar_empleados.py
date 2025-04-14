"""
Script de Búsqueda de Empleados - PROYECTO EDUCATIVO DE HACKING ÉTICO

Este script realiza la búsqueda ética de información pública sobre empleados
de una empresa objetivo utilizando la API de Hunter.io. Se basa en las mejores 
prácticas de OSINT ético para recopilar información disponible públicamente.

IMPORTANTE: Este script es SOLO para fines educativos y debe usarse de manera 
responsable y ética. Respeta siempre los términos de servicio de las APIs utilizadas.

Referencias:
- https://hunter.io/api-documentation
- https://infosecwriteups.com/corporate-reconnaissance-and-data-analysis-a-guide-to-ethical-hacking-ef0a341fa87a
"""

import json
import time
import random
import argparse
import requests
from datetime import datetime

def banner():
    """Muestra un banner decorativo para el script."""
    print("""
    ╔════════════════════════════════════════╗
    ║    Análisis de Información Pública     ║
    ║          Proyecto Educativo            ║
    ╚════════════════════════════════════════╝
    """)

def obtener_info_hunter(dominio, api_key, limite=10):
    """
    Obtiene información real de empleados usando la API de Hunter.io
    
    Args:
        dominio (str): Dominio de la empresa a analizar
        api_key (str): API key de Hunter.io
        limite (int): Número máximo de resultados
        
    Returns:
        dict: Información sobre empleados encontrados
    """
    print(f"[+] Buscando información de empleados en {dominio} mediante Hunter.io")
    
    url = f"https://api.hunter.io/v2/domain-search?domain={dominio}&limit={limite}&api_key={api_key}"
    
    headers = {
        'User-Agent': 'ProyectoHackingEtico/1.0 (Educativo)'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"[!] Error al consultar Hunter.io: Código {response.status_code}")
            print(f"[!] Mensaje: {response.text}")
            return None
    except Exception as e:
        print(f"[!] Error en la petición: {str(e)}")
        return None

def obtener_tecnologias(dominio):
    """
    Obtiene información sobre tecnologías usadas en el dominio
    mediante análisis de cabeceras HTTP y otros métodos pasivos.
    
    Args:
        dominio (str): Dominio a analizar
        
    Returns:
        dict: Tecnologías detectadas
    """
    print(f"[+] Analizando tecnologías en {dominio}")
    
    tecnologias = {}
    
    url = f"https://{dominio}"
    headers = {'User-Agent': 'Mozilla/5.0 ProyectoHackingEtico/1.0 (Educativo)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Analizamos cabeceras
        if 'Server' in response.headers:
            tecnologias['servidor'] = response.headers['Server']
        
        if 'X-Powered-By' in response.headers:
            tecnologias['powered_by'] = response.headers['X-Powered-By']
        
        # Podríamos expandir esto para detectar frameworks, CDNs, etc.
        tecnologias['status_code'] = response.status_code
        
        return tecnologias
    except Exception as e:
        print(f"[!] Error al analizar tecnologías: {str(e)}")
        return {'error': str(e)}

def procesar_resultados(datos_hunter, tecnologias, dominio):
    """
    Procesa y estructura los resultados obtenidos.
    
    Args:
        datos_hunter (dict): Datos obtenidos de Hunter.io
        tecnologias (dict): Tecnologías detectadas
        dominio (str): Dominio analizado
        
    Returns:
        dict: Resultados procesados y estructurados
    """
    resultados = {
        "dominio": dominio,
        "fecha_analisis": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "empleados": [],
        "estadisticas": {
            "total_empleados": 0,
            "dominios_relacionados": [],
            "departamentos": {}
        },
        "tecnologias": tecnologias
    }
    
    if not datos_hunter or 'data' not in datos_hunter:
        return resultados
    
    # Procesamos información de empleados
    if 'emails' in datos_hunter['data']:
        for email in datos_hunter['data']['emails']:
            empleado = {
                "nombre": f"{email.get('first_name', '')} {email.get('last_name', '')}".strip(),
                "correo": email.get('value', ''),
                "tipo": email.get('type', ''),
                "posicion": email.get('position', ''),
                "departamento": email.get('department', '')
            }
            
            resultados["empleados"].append(empleado)
            
            # Actualizamos estadísticas de departamentos
            if empleado["departamento"]:
                resultados["estadisticas"]["departamentos"][empleado["departamento"]] = \
                    resultados["estadisticas"]["departamentos"].get(empleado["departamento"], 0) + 1
    
    # Datos generales
    resultados["estadisticas"]["total_empleados"] = datos_hunter['data'].get('total', 0)
    
    # Dominios relacionados
    if 'related_domains' in datos_hunter['data'] and 'domain_names' in datos_hunter['data']['related_domains']:
        resultados["estadisticas"]["dominios_relacionados"] = datos_hunter['data']['related_domains']['domain_names']
    
    return resultados

def mostrar_resultados(datos):
    """
    Muestra los resultados del análisis de manera legible.
    
    Args:
        datos (dict): Resultados procesados
    """
    print("\n" + "="*50)
    print("RESULTADOS DEL ANÁLISIS DE INFORMACIÓN PÚBLICA")
    print("="*50)
    
    print(f"\nDominio analizado: {datos['dominio']}")
    print(f"Fecha del análisis: {datos['fecha_analisis']}")
    
    # Tecnologías detectadas
    print("\nTecnologías detectadas:")
    for tech, valor in datos['tecnologias'].items():
        print(f"  - {tech}: {valor}")
    
    # Estadísticas generales
    print(f"\nTotal empleados encontrados: {datos['estadisticas']['total_empleados']}")
    
    # Departamentos
    if datos['estadisticas']['departamentos']:
        print("\nDepartamentos identificados:")
        for depto, cantidad in datos['estadisticas']['departamentos'].items():
            print(f"  - {depto}: {cantidad} empleados")
    
    # Dominios relacionados
    if datos['estadisticas']['dominios_relacionados']:
        print("\nDominios relacionados:")
        for dominio in datos['estadisticas']['dominios_relacionados']:
            print(f"  - {dominio}")
    
    # Muestra los primeros 5 empleados como ejemplo
    if datos['empleados']:
        print(f"\nPrimeros {min(5, len(datos['empleados']))} empleados encontrados (muestra):")
        for i, emp in enumerate(datos['empleados'][:5]):
            print(f"  {i+1}. {emp['nombre']} - {emp['posicion']} - {emp['correo']}")
        
        if len(datos['empleados']) > 5:
            print(f"  ... y {len(datos['empleados']) - 5} más (ver archivo JSON para detalles completos)")

def guardar_resultados(datos, archivo="resultados_empleados.json"):
    """
    Guarda los resultados en un archivo JSON.
    
    Args:
        datos (dict): Datos a guardar
        archivo (str): Nombre del archivo de salida
    """
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)
    print(f"\n[+] Resultados guardados en '{archivo}'")

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description='Análisis ético de información pública de empleados mediante Hunter.io',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python buscar_empleados.py tesla.com --api-key-hunter=TU_API_KEY
  python buscar_empleados.py tesla.com --api-key-hunter=TU_API_KEY --limite 20 --output tesla_empleados.json
        """
    )
    parser.add_argument('dominio', help='Dominio de la empresa a analizar (ej: tesla.com)')
    parser.add_argument('--api-key-hunter', required=True, help='API key de Hunter.io')
    parser.add_argument('--limite', type=int, default=10, help='Número de resultados a obtener')
    parser.add_argument('--output', default='resultados_empleados.json', help='Archivo para guardar resultados')
    
    args = parser.parse_args()
    
    banner()
    
    # Obtenemos información de Hunter.io
    datos_hunter = obtener_info_hunter(args.dominio, args.api_key_hunter, args.limite)
    
    # Obtenemos información de tecnologías
    tecnologias = obtener_tecnologias(args.dominio)
    
    # Procesamos los resultados
    resultados = procesar_resultados(datos_hunter, tecnologias, args.dominio)
    
    # Mostramos y guardamos resultados
    mostrar_resultados(resultados)
    guardar_resultados(resultados, args.output)
    
    print("\n[+] Análisis completado. Recuerda utilizar esta información solo con fines educativos y éticos.")

if __name__ == "__main__":
    main() 