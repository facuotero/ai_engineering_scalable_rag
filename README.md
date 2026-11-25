# Pre-entrega 4 — RAG escalable con Pinecone

Módulo de recuperación en Python 3.12: ingesta Markdown → embeddings OpenAI → Pinecone Serverless, búsqueda híbrida BM25 + vectores mediante `EnsembleRetriever`, y evaluación por documento fuente. No requiere un modelo generativo ni despliegue de una API.

## Instalación y configuración

```bash
git clone https://github.com/facuotero/ai_engineering_scalable_rag.git
cd ai_engineering_scalable_rag
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock.txt
cp .env.example .env
```

Completar `.env` localmente:

```dotenv
PINECONE_API_KEY=tu_clave_pinecone
OPENAI_API_KEY=tu_clave_openai
INDEX_NAME=rag-preentrega4
PINECONE_NAMESPACE=python-docs
```

Las claves se obtienen de las respectivas cuentas de Pinecone y OpenAI. La cuenta OpenAI debe permitir embeddings; estas operaciones pueden consumir crédito. `.env` está excluido de Git. `requirements.lock.txt` fija el entorno verificado; `requirements.txt` declara rangos para actualizaciones deliberadas. Se utiliza Pinecone SDK 7.3.0 y su API `create_index`/`ServerlessSpec`.

## Replicar el índice y ejecutar

```bash
python init_index.py
python ingest.py
python query.py "¿Cómo registrar el traceback de una excepción?"
python evaluate.py
```

`init_index.py` crea el índice si falta: Serverless, AWS `us-east-1`, dimensión **1536**, métrica **cosine**. Comprueba la configuración y espera disponibilidad hasta 120 segundos. Un índice incompatible produce un error y no se modifica. `ingest.py` también ejecuta esta comprobación.

La ingesta incluye diez textos educativos originales en español sobre la biblioteca estándar de Python, con referencias a su documentación. Acepta otros directorios Markdown mediante `--documents ruta`. `RecursiveCharacterTextSplitter` divide a un máximo de 700 tokens (`cl100k_base`), con solapamiento objetivo de 100 tokens; los textos breves no se rellenan. El modelo es `text-embedding-3-small`, con dimensión explícita 1536.

Cada vector conserva `text`, `source`, `document_id`, `chunk_id`, `categories` y `corpus_version`. Las categorías se derivan del nombre del archivo. Markdown no tiene páginas: ese campo se omite. Esta versión no incluye cargadores PDF o JSON.

Los lotes tienen 64 chunks y los IDs son deterministas. Repetir la misma ingesta sobrescribe los mismos IDs. Después de comprobar visibilidad mediante fetch, se guarda atómicamente `artifacts/corpus.json`; no se publica un manifiesto parcial si falla la carga. Si una consulta inmediatamente posterior no ve datos recientes, repetirla tras unos segundos: Pinecone tiene consistencia eventual.

El manifiesto contiene los mismos chunks que BM25 necesita, sin credenciales. Debe conservarse junto al entorno de ejecución. `--manifest ruta` permite cambiar su ubicación en ingesta, consultas y evaluación. Una versión del corpus incluye hash del contenido, rutas y configuración de chunking. Ambos recuperadores usan esa versión y el mismo namespace. Cambiar el corpus genera otra versión; los vectores anteriores se conservan y no se recuperan por accidente. Su limpieza queda fuera de estos scripts y debe hacerse deliberadamente si es necesaria.

## Recuperación híbrida

`RAGSystem.retrieve(query, k=5)` devuelve objetos `Document` con contenido y metadatos. Usa BM25 en memoria con tokenización por palabras en minúsculas y un adaptador LangChain para el SDK nativo de Pinecone. `EnsembleRetriever` fusiona ambos rankings por Reciprocal Rank Fusion, con pesos 0,5/0,5 y deduplicación por `chunk_id`.

Cada rama aporta inicialmente veinte candidatos. El sistema conserva el chunk mejor clasificado por fuente y devuelve hasta cinco fuentes distintas. Si los candidatos concentran varias partes de pocas fuentes, duplica progresivamente el número de candidatos hasta cubrir el corpus o alcanzar el límite de 10.000. Puede devolver menos de cinco si no encuentra suficientes fuentes dentro de ese límite. La expansión implica consultas adicionales. No se consultan bases relacionales: el contenido vectorial vuelve en los metadatos de Pinecone.

Pinecone escala la recuperación vectorial; el BM25 local consume memoria proporcional al corpus y se reconstruye al iniciar cada comando. No es una solución distribuida para corpus masivos. `langchain-community` emite actualmente un aviso de deprecación; se mantiene `BM25Retriever` para cumplir la consigna con las versiones verificadas.

## Benchmark y métricas

`data/golden_set.json` contiene cinco preguntas, respuesta de referencia, `documento_id_esperado` y `documentos_relevantes`. El evaluador usa esta última lista como juicio explícito de relevancia y comprueba que sus IDs existan en el manifiesto. Las respuestas de referencia sirven para revisión humana; no se evalúa generación de texto.

- **Precision@5:** cantidad de fuentes relevantes recuperadas / 5.
- **Recall@5:** cantidad de fuentes relevantes recuperadas / cantidad total de fuentes relevantes anotadas.

Se cuentan fuentes únicas, no chunks. Las posiciones faltantes cuentan como no relevantes. Con una única fuente relevante por pregunta, Precision@5 tiene máximo **0,20** y Recall@5 indica si hubo acierto. Por eso no debe interpretarse 0,20 como una mala precisión de este benchmark. La salida muestra resultados por pregunta, IDs recuperados y promedios macro, junto al namespace y versión del corpus.

### Resultados verificados

| Ejecución | Precision@5 | Recall@5 | Estado |
|---|---:|---:|---|
| Baseline local BM25, rama vectorial vacía | 0,16 | 0,80 | Verificado en tests |
| Híbrido BM25 + Pinecone real | — | — | Pendiente de credenciales |

El baseline falla una paráfrasis de argparse: demuestra una limitación léxica que debe contrastarse con la recuperación híbrida real. No representa resultados de Pinecone. Para completar el reporte de entrega, ejecutar `python evaluate.py` con credenciales y sustituir la fila pendiente por los valores reales, conservando la identificación del corpus. No se estableció un umbral artificial de aprobación.

## Pruebas

```bash
python -m pytest -q
python -m pip check
```

Las pruebas no necesitan claves: verifican métricas conocidas, chunking, IDs deterministas, configuración y timeout del índice, aislamiento, fusión, ingesta repetida y manifiesto. Los clientes remotos se simulan. Incluyen también el baseline BM25 sobre el corpus real. Una ejecución real de inicialización, ingesta y evaluación sigue siendo necesaria para validar conectividad, permisos y comportamiento del proveedor.
