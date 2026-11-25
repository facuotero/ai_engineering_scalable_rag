import argparse
import json
from rag.config import ROOT, Settings
from rag.corpus import load_manifest
from rag.system import RAGSystem
from rag.metrics import metrics_at_k

def evaluate(system, benchmark, k=5):
    if not benchmark:
        raise ValueError('Benchmark vacío.')
    results = []
    for case in benchmark:
        docs = system.retrieve(case['pregunta'], k=k)
        ids = [d.metadata['document_id'] for d in docs]
        precision, recall = metrics_at_k(ids, case['documentos_relevantes'], k)
        results.append({'pregunta': case['pregunta'], 'recuperados': ids,
                        'precision': precision, 'recall': recall})
    return results

def main():
    parser = argparse.ArgumentParser(description='Precision@5 y Recall@5 por documento fuente')
    parser.add_argument('--benchmark', default=str(ROOT/'data/golden_set.json'))
    parser.add_argument('--manifest', default=str(ROOT/'artifacts/corpus.json'))
    args = parser.parse_args()
    settings = Settings.load()
    benchmark = json.loads(open(args.benchmark, encoding='utf-8').read())
    docs, version = load_manifest(args.manifest, settings)
    known = {d.metadata['document_id'] for d in docs}
    for case in benchmark:
        if not case['documentos_relevantes'] or not set(case['documentos_relevantes']) <= known:
            raise ValueError('El benchmark referencia documentos ausentes del corpus.')
    rows = evaluate(RAGSystem.from_settings(settings, args.manifest), benchmark)
    print(f'Corpus: {version} | namespace: {settings.namespace} | k=5')
    for row in rows:
        print(f"{row['pregunta']}\n  P@5={row['precision']:.3f} R@5={row['recall']:.3f} IDs={row['recuperados']}")
    print(f"\nPromedio Precision@5: {sum(r['precision'] for r in rows)/len(rows):.3f}")
    print(f"Promedio Recall@5: {sum(r['recall'] for r in rows)/len(rows):.3f}")

if __name__ == '__main__':
    main()
