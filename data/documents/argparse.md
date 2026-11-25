# Argumentos de línea de comandos

argparse construye interfaces de consola con ayuda automática. Se crea un ArgumentParser, se declaran argumentos con add_argument y se obtienen valores con parse_args. Los argumentos posicionales identifican entradas requeridas; las opciones suelen comenzar con --. El parámetro type convierte valores, default define un valor por defecto y choices restringe alternativas. action="store_true" permite implementar banderas booleanas. La opción --help muestra uso y descripción. Cuando el usuario entrega un valor inválido, el parser informa el error y termina con código distinto de cero. Los subparsers permiten agrupar operaciones como ingest, query y evaluate en un mismo comando.

Fuente de referencia: https://docs.python.org/3.12/library/argparse.html

Nota: explicación original de ejemplo para el corpus educativo.
