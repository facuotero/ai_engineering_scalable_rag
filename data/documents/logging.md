# Registro de eventos con logging

logging permite registrar eventos con niveles DEBUG, INFO, WARNING, ERROR y CRITICAL. Un logger se obtiene mediante logging.getLogger(__name__), lo que permite identificar el módulo de origen. logging.basicConfig configura manejadores básicos, formato y umbral de nivel. Para incluir un traceback dentro de un bloque except se usa logger.exception. Los mensajes pueden incorporar argumentos mediante placeholders como logger.info("Procesados %s archivos", cantidad). El nivel configurado determina qué eventos se emiten. Los registros sirven para diagnosticar operaciones, pero no deben contener contraseñas ni claves de API. Un FileHandler permite enviar eventos a un archivo y un StreamHandler a un flujo.

Fuente de referencia: https://docs.python.org/3.12/library/logging.html

Nota: explicación original de ejemplo para el corpus educativo.
