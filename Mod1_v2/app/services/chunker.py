from __future__ import annotations
import re, hashlib, uuid
from typing import List
from dataclasses import dataclass
from ..config import settings

# Простая ру сегментация предложений
SENT_RX = re.compile(r"\s*(.+?)([.!?…]+)(?=\s+[A-ZА-ЯЁ]|$)")

@dataclass
class ChunkPolicy:
    sent_min: int
    sent_max: int
    char_limit: int
    overlap_sent: int

policy = ChunkPolicy(
    settings.chunking.sent_min,
    settings.chunking.sent_max,
    settings.chunking.char_limit,
    settings.chunking.overlap_sent,
)

def split_sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", text.strip())
    out: List[str] = []
    i = 0
    for m in SENT_RX.finditer(text):
        sent = (m.group(1) + m.group(2)).strip()
        out.append(sent)
        i = m.end()
    tail = text[i:].strip()
    if tail:
        out.append(tail)
    return out

@dataclass
class ChunkDTO:
    session_id: str
    chunk_id: str
    seq: int
    text: str
    overlap_prefix: str
    lang: str
    policy: dict
    hash: str
    created_at: str = ""

def _hash(session_id: str, seq: int, text: str) -> str:
    h = hashlib.sha256()
    h.update(f"{session_id}|{seq}|{text}".encode("utf-8"))
    return h.hexdigest()

def make_chunks(session_id: str, sentences: List[str], start_seq: int = 1) -> List[ChunkDTO]:
    chunks: List[ChunkDTO] = []
    buf: List[str] = []
    seq = start_seq
    overlap_prev = ""
    idx = 0
    while idx < len(sentences):
        buf.append(sentences[idx])
        cur_txt = " ".join(buf)
        if (len(buf) >= policy.sent_min and (len(buf) >= policy.sent_max or len(cur_txt) >= policy.char_limit)):
            text = cur_txt
            overlap_prefix = overlap_prev
            dto = ChunkDTO(
                session_id=session_id,
                chunk_id=str(uuid.uuid4()),
                seq=seq,
                text=text,
                overlap_prefix=overlap_prefix,
                lang="ru-RU",
                policy={"sentences_per_chunk": [policy.sent_min, policy.sent_max], "char_limit": policy.char_limit, "overlap_sentences": policy.overlap_sent},
                hash=_hash(session_id, seq, text),
            )
            chunks.append(dto)
            overlap_prev = buf[-1] if policy.overlap_sent > 0 else ""
            buf = []
            seq += 1
        idx += 1
    if buf:
        text = " ".join(buf)
        dto = ChunkDTO(
            session_id=session_id,
            chunk_id=str(uuid.uuid4()),
            seq=seq,
            text=text,
            overlap_prefix=overlap_prev,
            lang="ru-RU",
            policy={"sentences_per_chunk": [policy.sent_min, policy.sent_max], "char_limit": policy.char_limit, "overlap_sentences": policy.overlap_sent},
            hash=_hash(session_id, seq, text),
        )
        chunks.append(dto)
    return chunks