from __future__ import annotations

import math
import re
from collections import Counter
from typing import List, Tuple

from core.memory.types import MemoryRecord


class VectorStore:
    """Semantic retrieval — Chroma when available, keyword fallback otherwise."""

    def __init__(self, persist_dir: str = "./memory_db/vectors"):
        self.persist_dir = persist_dir
        self._chroma = None
        self._collections = {}
        self._last_query_error: str | None = None
        self._init_chroma()

    def _init_chroma(self) -> None:
        try:
            import chromadb

            self._chroma = chromadb.PersistentClient(path=self.persist_dir)
        except Exception:
            self._chroma = None

    def _collection(self, agent_id: str):
        if not self._chroma:
            return None
        if agent_id not in self._collections:
            self._collections[agent_id] = self._chroma.get_or_create_collection(
                name=f"agent_{agent_id.replace('/', '_')[:48]}"
            )
        return self._collections[agent_id]

    def _embed_chroma(self, text: str) -> List[float]:
        try:
            import ollama

            from core.config.ollama_models import MODELS

            model = MODELS["embed"]
            return ollama.embeddings(model=model, prompt=text)["embedding"]
        except Exception:
            return []

    def upsert(self, agent_id: str, record: MemoryRecord) -> None:
        col = self._collection(agent_id)
        if not col:
            return
        emb = self._embed_chroma(record.content)
        if not emb:
            return
        col.upsert(
            ids=[record.id],
            documents=[record.content],
            embeddings=[emb],
            metadatas=[
                {
                    "kind": record.kind.value,
                    "importance": record.importance,
                }
            ],
        )

    def query(self, agent_id: str, query_text: str, top_k: int = 6) -> List[Tuple[MemoryRecord, float]]:
        col = self._collection(agent_id)
        if col:
            emb = self._embed_chroma(query_text)
            if emb:
                try:
                    res = col.query(query_embeddings=[emb], n_results=top_k)
                    docs = res.get("documents", [[]])[0]
                    metas = res.get("metadatas", [[]])[0]
                    dists = res.get("distances", [[]])[0]
                    ids = res.get("ids", [[]])[0]
                    out = []
                    for i, doc in enumerate(docs):
                        if not doc:
                            continue
                        try:
                            kind = MemoryKind(metas[i].get("kind", "fact"))
                        except ValueError:
                            kind = MemoryKind.FACT
                        rec = MemoryRecord(
                            id=ids[i] if i < len(ids) else str(i),
                            agent_id=agent_id,
                            kind=kind,
                            content=doc,
                            importance=float(metas[i].get("importance", 0.5)),
                        )
                        score = 1.0 / (1.0 + (dists[i] if i < len(dists) else 1.0))
                        out.append((rec, score))
                    if out:
                        return out
                except Exception as exc:
                    # Observable degradation — caller may keyword-fallback via MemoryLayer
                    self._last_query_error = str(exc)
        return []

    @staticmethod
    def keyword_search(
        records: List[MemoryRecord], query: str, top_k: int = 6
    ) -> List[Tuple[MemoryRecord, float]]:
        tokens = set(re.findall(r"[\w\u4e00-\u9fff]+", query.lower()))
        if not tokens:
            return []
        scored = []
        for rec in records:
            text = rec.content.lower()
            hits = sum(1 for t in tokens if t in text)
            if hits == 0:
                continue
            score = hits / math.sqrt(len(tokens)) + rec.importance * 0.2
            scored.append((rec, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
