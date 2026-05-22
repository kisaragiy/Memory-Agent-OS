# core/memory/memory_kernel.py

from typing import List, Dict, Any
import time

class MemoryKernel:

    def __init__(self):
        self.episodic: List[Dict[str, Any]] = []   # 事件
        self.semantic: Dict[str, Dict[str, Any]] = {}   # 用户事实
        self.last_k = 5
        self.time = 0  # 时间步

    def store(self, text: str):
        """
        存储策略：
        - “我叫xxx” → semantic["name"]
        - “我在学xxx” → semantic["learning"]
        - 其他 → episodic
        """
        self.time += 1
        if "我叫" in text:
            name = text.split("我叫")[-1].strip()
            self.semantic["name"] = {
                "value": name,
                "importance": 10,
                "access_count": 0
            }
        elif "我在学" in text:
            learning = text.split("我在学")[-1].strip()
            self.semantic["learning"] = {
                "value": learning,
                "importance": 10,
                "access_count": 0
            }
        else:
            importance = self.score_importance(text)
            self.episodic.append({
                "content": text,
                "importance": importance,
                "access_count": 0,
                "last_used": self.time
            })

    def query(self, text: str):
        """
        查询策略：
        - 问名字 → semantic["name"]
        - 问学习 → semantic["learning"]
        - 否则 → 返回最近 episodic
        """
        self.time += 1
        if "叫什么" in text:
            return self.semantic.get("name", {"value": "不知道"})["value"]
        elif "学什么" in text:
            return self.semantic.get("learning", {"value": "不知道"})["value"]
        else:
            # Sort episodic memories by last_used in descending order
            sorted_episodic = sorted(self.episodic, key=lambda x: x["last_used"], reverse=True)
            results = []
            for m in sorted_episodic:
                if self.is_match(m["content"], text):
                    m["access_count"] += 1
                    m["last_used"] = self.time
                    results.append(m["content"])
                if len(results) == self.last_k:
                    break
            return results

    def get_context(self):
        """
        返回压缩上下文（Claude风格）
        """
        sorted_mem = sorted(
            self.episodic,
            key=lambda x: (
                x["importance"] * 2 +
                x["access_count"] +
                (self.time - x["last_used"]) * -0.1
            ),
            reverse=True
        )
        context = {
            "episodic": sorted_mem[:self.last_k],
            "semantic": self.semantic
        }
        return context

    def score_importance(self, text: str) -> float:
        score = 1

        # 身份类（最高）
        if "我叫" in text or "我是" in text:
            score += 10

        # 长期行为
        if "我在学" in text or "我喜欢" in text:
            score += 6

        # 明显重要
        if "重要" in text or "记住" in text:
            score += 8

        return score

    def is_match(self, memory: str, query: str) -> bool:
        # 简单的匹配逻辑，可以根据需要进行扩展
        return query in memory
