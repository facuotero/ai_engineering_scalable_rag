# Rutas de archivos con pathlib

Path permite representar rutas como objetos. El operador / combina directorios y nombres de archivo sin concatenar separadores manualmente. Path.read_text y Path.write_text leen y escriben texto; se recomienda indicar encoding="utf-8". Path.glob busca archivos mediante patrones dentro de un directorio; Path.rglob aplica la búsqueda recursivamente. exists comprueba existencia e is_file distingue archivos de directorios. Para crear directorios intermedios se usa mkdir(parents=True, exist_ok=True). Las rutas relativas dependen del directorio de trabajo del proceso, por lo que un script reproducible debe resolverlas respecto de una ubicación conocida. Leer una ruta inexistente produce FileNotFoundError.

Fuente de referencia: https://docs.python.org/3.12/library/pathlib.html

Nota: explicación original de ejemplo para el corpus educativo.
