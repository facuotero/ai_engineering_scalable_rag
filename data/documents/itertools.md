# Iteradores con itertools

itertools proporciona herramientas para combinar y transformar iteradores sin materializar necesariamente todo el resultado. chain concatena secuencias y islice toma una porción de un iterable. product genera combinaciones cartesianas, mientras combinations produce grupos sin repetición de posiciones. count genera una secuencia potencialmente infinita y debe consumirse con un límite cuando corresponda. groupby agrupa elementos consecutivos con una misma clave; si se buscan grupos globales por clave normalmente se debe ordenar previamente. Los iteradores se consumen al recorrerlos y pueden agotarse. El procesamiento perezoso reduce memoria, aunque convertir el resultado a list vuelve a materializarlo completo.

Fuente de referencia: https://docs.python.org/3.12/library/itertools.html

Nota: explicación original de ejemplo para el corpus educativo.
