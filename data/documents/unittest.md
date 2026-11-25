# Pruebas automatizadas con unittest

unittest organiza pruebas en clases que heredan de TestCase. Los métodos cuyo nombre comienza con test se descubren como casos de prueba. assertEqual compara resultados y assertRaises verifica excepciones esperadas. setUp prepara recursos antes de cada caso y tearDown permite limpiarlos. unittest.mock ofrece Mock y patch para sustituir dependencias externas durante una prueba; se debe aplicar patch donde el símbolo es utilizado. Las pruebas de una aplicación con servicios remotos pueden simular respuestas para verificar errores y contratos sin consumir cuotas. Estas pruebas no reemplazan una ejecución de integración real con el proveedor. python -m unittest discover busca y ejecuta pruebas automáticamente.

Fuente de referencia: https://docs.python.org/3.12/library/unittest.html

Nota: explicación original de ejemplo para el corpus educativo.
