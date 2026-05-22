import ollama
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


EMBED_MODEL = "nomic-embed-text"


# =========================
# EMBEDDING GENERATION
# =========================

def get_embedding(text: str):
    """
    🧠 获取向量
    """

    res = ollama.embeddings(
        model=EMBED_MODEL,
        prompt=text
    )

    return np.array(res["embedding"])


# =========================
# SIMILARITY SCORE
# =========================

def similarity(a: str, b: str) -> float:
    """
    🧠 语义相似度
    """

    emb_a = get_embedding(a)
    emb_b = get_embedding(b)

    score = cosine_similarity(
        [emb_a],
        [emb_b]
    )[0][0]

    return float(score)
