# Contadores y colas con collections

collections ofrece estructuras especializadas. Counter cuenta ocurrencias de elementos hashables y most_common devuelve los elementos más frecuentes. defaultdict utiliza una fábrica para crear valores cuando se accede a una clave inexistente; defaultdict(list) facilita agrupar registros. deque permite agregar y quitar elementos eficientemente en ambos extremos mediante append, appendleft, pop y popleft. Una deque con maxlen limita su tamaño y descarta elementos del extremo opuesto al insertar cuando está llena. Estas estructuras reducen código repetitivo en procesamiento de datos. Counter sirve para frecuencias de palabras, defaultdict para agrupar documentos por categoría y deque para mantener una ventana reciente de eventos.

Fuente de referencia: https://docs.python.org/3.12/library/collections.html

Nota: explicación original de ejemplo para el corpus educativo.
