# Proyecto de Análisis de Seguridad (Hacking Ético)

Este proyecto educativo demuestra técnicas de reconocimiento y escaneo ético enfocadas en análisis de organizaciones. Utilizando Python y diversas herramientas, el proyecto recopila información pública disponible sobre una organización objetivo (Tesla) de manera ética y legal.

## 🎯 Objetivos del Proyecto

- Demostrar técnicas de reconocimiento pasivo utilizando herramientas de código abierto
- Documentar el proceso de descubrimiento de información pública sobre una organización
- Analizar subdominios, IPs, información de empleados y tecnologías utilizadas
- Aplicar y documentar buenas prácticas de hacking ético y seguridad

## 📋 Contenido del Proyecto

- `reconocimiento.py`: Script principal para análisis de dominios, subdominios e IPs
- `buscar_empleados.py`: Script para obtener información real de empleados mediante OSINT ético
- `subdominios_comunes.txt`: Lista de subdominios comunes para fuerza bruta
- `analisis_tesla.md`: Informe completo del análisis con hallazgos y metodología
- `requirements.txt`: Dependencias necesarias para ejecutar los scripts

## 🛠️ Requisitos

- Python 3.7 o superior
- Bibliotecas Python (ver requirements.txt)
- API Key de Hunter.io (para el script de búsqueda de empleados)

## ⚙️ Instalación

1. Clona este repositorio o descarga los archivos
2. Instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

3. Obtén una API Key gratuita de [Hunter.io](https://hunter.io/api-keys) para el script de búsqueda de empleados

## 🚀 Uso

### Script de Reconocimiento Principal

Para ejecutar el análisis completo sobre el dominio objetivo:

```bash
python reconocimiento.py
```

Este script realizará:
- Análisis de dominio principal
- Búsqueda de subdominios
- Obtención de información DNS
- Análisis de headers de seguridad
- Escaneo básico de puertos
- Guardará los resultados en `resultados_reconocimiento.json`

### Script de Análisis de Empleados

Para realizar un análisis ético de información pública sobre empleados:

```bash
python buscar_empleados.py <dominio> --api-key-hunter <tu_api_key>
```

Ejemplos:
```bash
# Análisis básico con 10 resultados (valor predeterminado)
python buscar_empleados.py tesla.com --api-key-hunter TU_API_KEY

# Análisis con más resultados (25)
python buscar_empleados.py tesla.com --api-key-hunter TU_API_KEY --limite 25

# Guardar resultados en un archivo específico
python buscar_empleados.py tesla.com --api-key-hunter TU_API_KEY --output tesla_empleados.json
```

## 📊 Resultados

Los scripts generan resultados en formato JSON y también los muestran en la consola:

- `resultados_reconocimiento.json`: Contiene información sobre dominios, IPs, subdominios y puertos
- `resultados_empleados.json`: Contiene información de empleados obtenida mediante OSINT ético

Además, se incluye un informe completo en Markdown (`analisis_tesla.md`) que detalla:
- Metodología utilizada
- Hallazgos principales
- Análisis de la infraestructura
- Información sobre tecnologías y empleados
- Recomendaciones de seguridad

## ⚠️ Consideraciones Éticas

Este proyecto se ha desarrollado con fines puramente educativos y sigue principios de hacking ético:

1. **Solo se accede a información pública**: No se intenta acceder a sistemas protegidos ni eludir medidas de seguridad
2. **Respeto por la infraestructura**: Las solicitudes se realizan con retardos y tasas bajas para no afectar servicios
3. **Privacidad**: Aunque se accede a información pública de empleados, se respetan los términos de servicio de las APIs
4. **Transparencia**: Todo el código está documentado y explicado claramente

## 📝 Notas Importantes

- **Propósito Educativo**: Este proyecto está diseñado exclusivamente para fines educativos y de investigación
- **Uso Responsable**: Utiliza estas técnicas solo en sistemas para los que tengas autorización
- **Limitaciones Legales**: Asegúrate de comprender las leyes y regulaciones aplicables en tu jurisdicción antes de aplicar estas técnicas
- **Términos de Servicio**: Respeta los términos de servicio de Hunter.io y otras APIs utilizadas

## 📚 Referencias

- [Documentación de Python Requests](https://docs.python-requests.org/)
- [Prácticas éticas de OSINT](https://osintframework.com/)
- [Documentación de Hunter.io](https://hunter.io/api-documentation)
- [Guía de Hacking Ético](https://www.hackerone.com/ethical-hacker/ethical-hacking-guide)
- [Metodología de Pruebas de Penetración](https://owasp.org/www-project-web-security-testing-guide/)
- [Artículo: Corporate Reconnaissance and Data Analysis](https://infosecwriteups.com/corporate-reconnaissance-and-data-analysis-a-guide-to-ethical-hacking-ef0a341fa87a)

## 👥 Autor

Este proyecto fue desarrollado como parte de un ejercicio educativo para el curso de Hacking Ético. 