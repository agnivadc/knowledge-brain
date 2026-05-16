# Graph Report - .  (2026-05-16)

## Corpus Check
- Corpus is ~7,570 words - fits in a single context window. You may not need a graph.

## Summary
- 257 nodes · 474 edges · 19 communities (15 shown, 4 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 105 edges (avg confidence: 0.76)
- Token cost: 80,281 input · 20,071 output

## Community Hubs (Navigation)
- [[_COMMUNITY_CLI Integration Tests|CLI Integration Tests]]
- [[_COMMUNITY_Brain Operations & MCP Tools|Brain Operations & MCP Tools]]
- [[_COMMUNITY_SQLite Store & Schema|SQLite Store & Schema]]
- [[_COMMUNITY_Store Unit Tests|Store Unit Tests]]
- [[_COMMUNITY_Input Validation & Tokens|Input Validation & Tokens]]
- [[_COMMUNITY_CLI Commands & ID Helpers|CLI Commands & ID Helpers]]
- [[_COMMUNITY_Knowledge Node Model|Knowledge Node Model]]
- [[_COMMUNITY_JSONL ImportExport|JSONL Import/Export]]
- [[_COMMUNITY_Agent OS & CLI Entry|Agent OS & CLI Entry]]
- [[_COMMUNITY_MVP Plan & Scope|MVP Plan & Scope]]
- [[_COMMUNITY_Claude Code Hooks|Claude Code Hooks]]
- [[_COMMUNITY_Local Permissions|Local Permissions]]
- [[_COMMUNITY_Graphify Pre-Tool Hook|Graphify Pre-Tool Hook]]
- [[_COMMUNITY_TDD Convention|TDD Convention]]

## God Nodes (most connected - your core abstractions)
1. `KnowledgeNode` - 46 edges
2. `_run()` - 28 edges
3. `Store` - 24 edges
4. `BrainOperations` - 22 edges
5. `FakeStore` - 16 edges
6. `_node()` - 16 edges
7. `TestWriteAndQuery` - 14 edges
8. `TestExportImport` - 13 edges
9. `validate_write_input()` - 12 edges
10. `BrainStore` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Module execution order` --rationale_for--> `Store`  [EXTRACTED]
  docs/plans/2026-04-25-mvp.md → knowledge_brain/store.py
- `brain_write operation (manifest)` --references--> `brain_write MCP tool`  [INFERRED]
  AGENT_OS_MANIFEST.yaml → knowledge_brain/mcp/server.py
- `Filesystem + tool exec capabilities` --references--> `brain_write MCP tool`  [INFERRED]
  permissions.yaml → knowledge_brain/mcp/server.py
- `Module execution order` --rationale_for--> `KnowledgeNode`  [EXTRACTED]
  docs/plans/2026-04-25-mvp.md → knowledge_brain/models.py
- `Pydantic v2 deterministic JSON convention` --rationale_for--> `KnowledgeNode`  [EXTRACTED]
  CLAUDE.md → knowledge_brain/models.py

## Hyperedges (group relationships)
- **MCP tool dispatch flow** — mcp_server_brain_write_tool, mcp_server_brain_query_tool, mcp_server_brain_export_tool, mcp_server_ops_factory, knowledge_brain_operations_brainoperations [EXTRACTED 1.00]
- **Input validation pipeline (token + quality + model)** — knowledge_brain_quality_validate_write_input, knowledge_brain_quality_validate_query_input, knowledge_brain_token_utils_count_tokens, knowledge_brain_models_knowledgenode [EXTRACTED 1.00]
- **Agent OS to Knowledge Brain integration** — agent_os_manifest_yaml_manifest, permissions_yaml_fs_capabilities, readme_brain_db_path_env, mcp_server_brain_write_tool [INFERRED 0.85]
- **CLI subcommand register/run pattern** — cli_export_register, cli_import_jsonl_register, cli_init_register, cli_list_register, cli_query_register, cli_write_register [INFERRED 0.95]
- **BrainOperations.from_db consumers** — cli_export_run, cli_query_run, cli_write_run [EXTRACTED 1.00]
- **Store protocol test doubles** — unit_test_jsonl_fakemergestore, unit_test_operations_fakestore, tests_conftest_tmp_db_path [INFERRED 0.85]

## Communities (19 total, 4 thin omitted)

### Community 0 - "CLI Integration Tests"
Cohesion: 0.11
Nodes (8): _run(), TestExportImport, TestInit, TestList, TestParser, TestQuery, TestVersion, TestWrite

### Community 1 - "Brain Operations & MCP Tools"
Cohesion: 0.11
Nodes (19): brain_export operation (manifest), brain_query operation (manifest), brain_write operation (manifest), uvx as MCP entrypoint, JsonlImportStore, WriteResult, BrainOperations, BrainStore (+11 more)

### Community 2 - "SQLite Store & Schema"
Cohesion: 0.13
Nodes (13): run(), run(), run(), Locked design decisions, test_mcp_server._isolate_db, _connect(), _escape_like(), Return all nodes sorted by id (stable for diff-friendly export). (+5 more)

### Community 3 - "Store Unit Tests"
Cohesion: 0.13
Nodes (5): _node(), store(), TestMergeNode, TestSchema, TestWriteAndQuery

### Community 4 - "Input Validation & Tokens"
Cohesion: 0.13
Nodes (11): InputValidationError, validate_query_input(), validate_write_input(), count_tokens(), Approximate token count via word-based heuristic (~1.3 tokens/word)., test_input_validation_error_is_value_error(), TestValidateQueryInput, TestValidateWriteInput (+3 more)

### Community 5 - "CLI Commands & ID Helpers"
Cohesion: 0.11
Nodes (13): query._parse_tags, _parse_tags(), run(), write._parse_tags, _parse_tags(), run(), brain_export(), brain_query() (+5 more)

### Community 6 - "Knowledge Node Model"
Cohesion: 0.13
Nodes (20): BaseModel, Pydantic v2 deterministic JSON convention, Module execution order, CompiledContextResponse, KnowledgeNode, test_compiled_context_response_default_timestamp_is_iso_utc(), test_compiled_context_response_round_trip(), test_confidence_boundaries_accepted() (+12 more)

### Community 7 - "JSONL Import/Export"
Cohesion: 0.17
Nodes (17): run(), decode_node(), encode_node(), encode_nodes(), format_import_summary(), import_nodes_from_lines(), ImportSummary, JsonlNodeDecodeError (+9 more)

### Community 9 - "Agent OS & CLI Entry"
Cohesion: 0.2
Nodes (9): Agent OS Manifest, build_parser(), main(), Deterministic-by-construction MCP design, test_cli._run, Filesystem + tool exec capabilities, Agent OS memory-substrate integration, BRAIN_DB_PATH env var (+1 more)

### Community 10 - "MVP Plan & Scope"
Cohesion: 0.67
Nodes (3): Knowledge Brain MVP scope, MVP out-of-scope features, Knowledge Brain MVP Implementation Plan

## Knowledge Gaps
- **23 isolated node(s):** `PreToolUse`, `allow`, `Insert a node, skipping (or replacing if force) on ID conflict.          Retur`, `Return all nodes sorted by id (stable for diff-friendly export).`, `Approximate token count via word-based heuristic (~1.3 tokens/word).` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `KnowledgeNode` connect `Knowledge Node Model` to `Brain Operations & MCP Tools`, `SQLite Store & Schema`, `Store Unit Tests`, `Input Validation & Tokens`, `CLI Commands & ID Helpers`, `JSONL Import/Export`?**
  _High betweenness centrality (0.284) - this node is a cross-community bridge._
- **Why does `Store` connect `SQLite Store & Schema` to `Brain Operations & MCP Tools`, `Store Unit Tests`, `Knowledge Node Model`, `JSONL Import/Export`?**
  _High betweenness centrality (0.249) - this node is a cross-community bridge._
- **Why does `BrainOperations` connect `Brain Operations & MCP Tools` to `SQLite Store & Schema`, `Input Validation & Tokens`, `CLI Commands & ID Helpers`, `Knowledge Node Model`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `KnowledgeNode` (e.g. with `ImportSummary` and `JsonlNodeDecodeError`) actually correct?**
  _`KnowledgeNode` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Store` (e.g. with `BrainStore` and `TestSchema`) actually correct?**
  _`Store` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `BrainOperations` (e.g. with `CompiledContextResponse` and `WriteResult`) actually correct?**
  _`BrainOperations` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `FakeStore` (e.g. with `InputValidationError` and `KnowledgeNode`) actually correct?**
  _`FakeStore` has 6 INFERRED edges - model-reasoned connections that need verification._