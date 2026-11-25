# Consultas SQL con sqlite3

sqlite3 permite utilizar una base de datos SQLite desde Python. connect abre una conexión a un archivo o a :memory: para una base temporal en memoria. Las consultas deben usar parámetros: execute("SELECT * FROM docs WHERE id = ?", (identifier,)) separa SQL de los valores. No se deben concatenar entradas del usuario dentro del SQL. Los cambios requieren gestionar transacciones y confirmar con commit o revertir con rollback. fetchone devuelve una fila y fetchall obtiene las restantes. El contexto de una conexión gestiona confirmación o reversión, pero no cierra automáticamente la conexión: el cierre debe manejarse explícitamente. SQLite resulta útil para persistencia local sin un servidor separado.

Fuente de referencia: https://docs.python.org/3.12/library/sqlite3.html

Nota: explicación original de ejemplo para el corpus educativo.
