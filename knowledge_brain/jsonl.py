from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal, Protocol

from .models import KnowledgeNode

MergeResult = Literal["inserted", "skipped", "replaced"]


class JsonlImportStore(Protocol):
    def merge_node(self, node: KnowledgeNode, *, force: bool = False) -> MergeResult: ...


@dataclass(frozen=True)
class ImportSummary:
    inserted: int = 0
    skipped: int = 0
    replaced: int = 0


class JsonlNodeDecodeError(ValueError):
    pass


def encode_node(node: KnowledgeNode) -> str:
    return json.dumps(node.model_dump(mode="json"), sort_keys=True)


def encode_nodes(nodes: list[KnowledgeNode]) -> list[str]:
    return [encode_node(node) for node in nodes]


def decode_node(line: str, *, line_no: int) -> KnowledgeNode:
    try:
        data = json.loads(line)
        return KnowledgeNode(**data)
    except Exception as e:
        raise JsonlNodeDecodeError(f"line {line_no}: {e}") from e


def import_nodes_from_lines(
    lines: Iterable[str],
    store: JsonlImportStore,
    *,
    force: bool = False,
) -> ImportSummary:
    counts = {"inserted": 0, "skipped": 0, "replaced": 0}
    for line_no, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            continue
        result = store.merge_node(decode_node(line, line_no=line_no), force=force)
        counts[result] += 1
    return ImportSummary(
        inserted=counts["inserted"],
        skipped=counts["skipped"],
        replaced=counts["replaced"],
    )


def format_import_summary(summary: ImportSummary) -> str:
    return (
        f"import complete: {summary.inserted} inserted, "
        f"{summary.skipped} skipped, {summary.replaced} replaced"
    )
