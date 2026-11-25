from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from rag.corpus import prepare_corpus
from rag.metrics import metrics_at_k
from rag.infrastructure import ensure_index
from rag.system import RAGSystem, PineconeRetriever

def test_metrics():
    assert metrics_at_k(['a','a','b'], ['a'], 5) == (0.2, 1.0)
    assert metrics_at_k(['a','b'], ['a','c'], 5) == (0.2, 0.5)
    assert metrics_at_k([], ['a'], 5) == (0, 0)
    assert metrics_at_k(['a','b'], ['a','b'], 2) == (1, 1)

def test_corpus(tmp_path):
    (tmp_path/'a.md').write_text('token técnico ' * 1500)
    docs, version = prepare_corpus(tmp_path)
    import tiktoken
    enc = tiktoken.get_encoding('cl100k_base')
    assert len(docs) > 1
    assert all(len(enc.encode(d.page_content)) <= 700 for d in docs)
    assert all(d.metadata['document_id'] == 'a' for d in docs)
    assert prepare_corpus(tmp_path)[1] == version
    (tmp_path/'a.md').write_text('otro contenido')
    assert prepare_corpus(tmp_path)[1] != version

def test_index():
    pc = Mock()
    pc.list_indexes.return_value.names.return_value = []
    pc.describe_index.return_value = SimpleNamespace(dimension=1536, metric='cosine', status={'ready':True})
    ensure_index(pc, 'demo')
    pc.create_index.assert_called_once()
    pc.list_indexes.return_value.names.return_value = ['demo']
    pc.create_index.reset_mock()
    ensure_index(pc, 'demo')
    pc.create_index.assert_not_called()
    pc.describe_index.return_value.dimension = 512
    with pytest.raises(ValueError, match='1536'):
        ensure_index(pc, 'demo')

class FixedRetriever(BaseRetriever):
    docs: list[Document]
    def _get_relevant_documents(self, query, *, run_manager):
        return self.docs

def test_hybrid():
    docs = [Document(page_content=f'text {i}', metadata={'document_id':str(i//2), 'chunk_id':str(i)}) for i in range(14)]
    system = RAGSystem(FixedRetriever(docs=docs), FixedRetriever(docs=list(reversed(docs))))
    result = system.retrieve('test')
    assert len(result) == len({d.metadata['document_id'] for d in result}) == 5
    with pytest.raises(ValueError):
        system.retrieve(' ')

def test_vector_isolation():
    index, embeddings = Mock(), Mock()
    embeddings.embed_query.return_value = [0.0]*1536
    index.query.return_value = {'matches':[{'metadata':{'text':'contenido', 'document_id':'a', 'chunk_id':'a1'}}]}
    retriever = PineconeRetriever(index=index, embeddings=embeddings, namespace='tenant', corpus_version='v1')
    assert retriever.invoke('test')[0].page_content == 'contenido'
    assert index.query.call_args.kwargs['namespace'] == 'tenant'
    assert index.query.call_args.kwargs['filter'] == {'corpus_version': {'$eq': 'v1'}}

def test_upload_is_repeatable_and_stores_text(tmp_path):
    from rag.infrastructure import upload
    from rag.corpus import save_manifest, load_manifest
    from rag.config import Settings
    (tmp_path/'a.md').write_text('Texto técnico sobre Python.')
    docs, version = prepare_corpus(tmp_path)
    index, embeddings = Mock(), Mock()
    embeddings.embed_documents.return_value = [[0.0]*1536 for _ in docs]
    index.fetch.return_value = SimpleNamespace(vectors={d.metadata['chunk_id']: {} for d in docs})
    upload(index, embeddings, docs, 'tenant')
    first = index.upsert.call_args
    upload(index, embeddings, docs, 'tenant')
    assert index.upsert.call_args == first
    assert first.kwargs['vectors'][0]['metadata']['text'] == docs[0].page_content
    assert first.kwargs['namespace'] == 'tenant'
    settings = Settings('secret', 'secret', 'index', 'tenant')
    path = tmp_path/'manifest.json'
    save_manifest(path, docs, version, settings)
    assert load_manifest(path, settings) == (docs, version)
    with pytest.raises(ValueError, match='namespace'):
        load_manifest(path, Settings('', '', 'index', 'other'))
    embeddings.embed_documents.return_value = [[0.0]*512]
    with pytest.raises(ValueError, match='1536'):
        upload(index, embeddings, docs, 'tenant')

def test_index_timeout():
    pc = Mock()
    pc.list_indexes.return_value.names.return_value = ['demo']
    pc.describe_index.return_value = SimpleNamespace(dimension=1536, metric='cosine', status={'ready':False})
    with pytest.raises(TimeoutError):
        ensure_index(pc, 'demo', timeout=0)

def test_benchmark_and_real_bm25():
    import json
    from langchain_community.retrievers import BM25Retriever
    from rag.system import tokenize
    from rag.config import ROOT
    from evaluate import evaluate
    docs, _ = prepare_corpus(ROOT/'data/documents')
    cases = json.loads((ROOT/'data/golden_set.json').read_text())
    assert len(cases) == 5
    bm25 = BM25Retriever.from_documents(docs, preprocess_func=tokenize, k=20)
    system = RAGSystem(bm25, FixedRetriever(docs=[]))
    rows = evaluate(system, cases)
    # A lexical-only baseline can miss paraphrases; verify measured aggregates.
    assert sum(row['recall'] for row in rows)/5 == pytest.approx(0.8)
    assert sum(row['precision'] for row in rows)/5 == pytest.approx(0.16)

class LimitedRetriever(FixedRetriever):
    k: int = 20
    def _get_relevant_documents(self, query, *, run_manager):
        return self.docs[:self.k]

def test_expand_candidates_for_distinct_sources():
    docs = [Document(page_content=str(i), metadata={'document_id':str(i//25), 'chunk_id':str(i)}) for i in range(150)]
    system = RAGSystem(LimitedRetriever(docs=docs), LimitedRetriever(docs=docs), max_candidates=150)
    assert len(system.retrieve('test')) == 5
