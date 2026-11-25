"""Document-level retrieval metrics; absent slots count as non-relevant."""
def metrics_at_k(retrieved, relevant, k=5):
    relevant = set(relevant)
    if not relevant or k < 1:
        raise ValueError('Se requiere al menos un documento relevante y k positivo.')
    unique = list(dict.fromkeys(retrieved))[:k]
    hits = len(set(unique) & relevant)
    return hits / k, hits / len(relevant)
