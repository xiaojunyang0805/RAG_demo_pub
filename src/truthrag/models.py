"""Data passed between stages. Everything stored is already redacted."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

# Truth classes, from most to least authoritative about "now".
CURRENT, LOG_CURRENT, REFERENCE, LOG, ARCHIVE = "current", "log_current", "reference", "log", "archive"
CLASSES = (CURRENT, LOG_CURRENT, REFERENCE, LOG, ARCHIVE)
STATUS_TAG = {CURRENT: "current", LOG_CURRENT: "current", REFERENCE: "vendor claim", LOG: "history",
              ARCHIVE: "history"}
PROMPT_LABEL = {CURRENT: "CURRENT", LOG_CURRENT: "CURRENT", REFERENCE: "EXTERNAL SOURCE", LOG: "HISTORY",
                ARCHIVE: "HISTORY"}


@dataclass
class Chunk:
    id: str
    path: str
    heading_path: list[str]
    text: str
    truth: str
    retired_by: list[str]
    tokens: int

    @property
    def citation(self) -> str:
        heading = " › ".join(self.heading_path[1:]) or (self.heading_path[0] if self.heading_path else "")
        return f"{self.path} § {heading}" if heading else self.path

    def embed_text(self) -> str:
        return f"{self.path}\n{' > '.join(self.heading_path)}\n\n{self.text}"

    def to_json(self) -> dict:
        return asdict(self)


@dataclass
class Hit:
    chunk: Chunk
    score: float = 0.0
    bm25_rank: int | None = None
    vector_rank: int | None = None
    vector_sim: float | None = None
    fused: float = 0.0
    weight: float = 1.0


@dataclass
class Answer:
    question: str
    text: str
    citations: list[int] = field(default_factory=list)
    status: str = ""
    superseded: str = ""
    refused: bool = False
    hits: list[Hit] = field(default_factory=list)
    guard_issues: list[str] = field(default_factory=list)
    usage: dict = field(default_factory=dict)
