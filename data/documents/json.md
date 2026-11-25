# Serialización de JSON

json.loads convierte una cadena JSON en objetos de Python y json.dumps realiza la conversión inversa. json.load y json.dump trabajan con objetos de archivo. Los objetos JSON se representan como diccionarios y los arrays como listas; null se convierte en None. Para preservar caracteres legibles en español al serializar se puede usar ensure_ascii=False y abrir el archivo con encoding="utf-8". El parámetro indent facilita inspeccionar el resultado. Un documento mal formado provoca JSONDecodeError. JSON no conserva automáticamente tipos como fechas, conjuntos o instancias de clases: deben convertirse a valores compatibles. Parsear JSON tampoco valida por sí solo el esquema de una aplicación.

Fuente de referencia: https://docs.python.org/3.12/library/json.html

Nota: explicación original de ejemplo para el corpus educativo.
