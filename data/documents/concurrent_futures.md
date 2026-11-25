# Tareas concurrentes con futures

concurrent.futures ofrece ThreadPoolExecutor y ProcessPoolExecutor. Un executor recibe tareas mediante submit y devuelve objetos Future. future.result obtiene el resultado y propaga la excepción de la tarea. as_completed permite recorrer futuros conforme terminan. ThreadPoolExecutor resulta habitual para operaciones que esperan entrada o salida, como solicitudes de red. ProcessPoolExecutor utiliza procesos separados y requiere argumentos y funciones serializables; es habitual proteger el punto de entrada con if __name__ == "__main__". El administrador de contexto del executor espera la finalización al salir. La concurrencia debe limitarse para respetar capacidad y cuotas de servicios externos.

Fuente de referencia: https://docs.python.org/3.12/library/concurrent_futures.html

Nota: explicación original de ejemplo para el corpus educativo.
