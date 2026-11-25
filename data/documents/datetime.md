# Fechas y zonas horarias

datetime contiene tipos para fechas, horas y duraciones. datetime.now(timezone.utc) produce un instante con zona UTC explícita. Un datetime sin información de zona es naive y uno con zona es aware. Mezclar ambos en operaciones puede provocar errores o ambigüedad. timedelta representa diferencias de tiempo. isoformat serializa fechas en una representación legible e interoperable y fromisoformat interpreta formatos compatibles. astimezone convierte un instante a otra zona. Para zonas geográficas con cambios históricos y horario estacional se utiliza ZoneInfo del módulo zoneinfo. Guardar instantes en UTC y convertirlos al presentar resultados ayuda a evitar ambigüedades.

Fuente de referencia: https://docs.python.org/3.12/library/datetime.html

Nota: explicación original de ejemplo para el corpus educativo.
