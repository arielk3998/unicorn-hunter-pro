"""Skills Strength Visualization
Aggregates skill frequency across experience bullets.
"""
from __future__ import annotations
from typing import Dict, List
import re

COMMON_SPLIT = re.compile(r'[;,\n]')

def extract_skills(text_blocks: List[str]) -> Dict[str, int]:
    freq: Dict[str,int] = {}
    for blk in text_blocks:
        words = re.findall(r'[A-Za-z0-9+#\.]+', blk)
        for w in words:
            if len(w) < 2:  # skip tiny
                continue
            key = w.strip()
            freq[key] = freq.get(key, 0) + 1
    return freq

def top_skills(freq: Dict[str,int], limit: int = 25) -> List[tuple]:
    return sorted(freq.items(), key=lambda x: x[1], reverse=True)[:limit]

if __name__ == '__main__':
    demo = ["Led SAP ERP migration with SQL data validation", "Implemented Python automation reducing manual Excel work"]
    f = extract_skills(demo)
    print(top_skills(f))
