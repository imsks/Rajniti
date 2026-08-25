# Rajniti — Civic Tech for Political Accountability

Rajniti enables citizens to track their elected representatives, monitor political promises, and access civic data through an AI-powered Q&A interface.

## Language

### Domain Terms

**Representative**:
An elected official (MP, MLA) with a constituency, party affiliation, and public record.
_Avoid_: Politician, leader, lawmaker

**Promise**:
A verifiable commitment made by a Representative, tracked through its lifecycle (made → in_progress → kept | broken).
_Avoid_: Pledge, commitment, statement

**Constituency**:
A geographic region represented by a single Representative. A Representative belongs to exactly one Constituency.
_Avoid_: District, ward, area

**Civic Data**:
Structured public information about representatives, promises, voting records, and government proceedings.
_Avoid_: Political data, government data

### Technical Terms

**Agent**:
A request-scoped LangGraph execution that answers civic questions using RAG retrieval and synthesis.
_Avoid_: Bot, assistant, AI

**RAG**:
Retrieval-Augmented Generation — fetches relevant chunks from the embedded vector index before synthesizing an answer.
_Avoid_: Search, lookup

**Module**:
A Flask package with enforced boundaries (`promises`, `reps`, `rag`, `agents`). Modules communicate via DTOs through public facades.
_Avoid_: Service, layer, package

**DTO**:
Data Transfer Object — a Pydantic model that crosses module boundaries. Modules never share ORM rows or Chroma handles directly.
_Avoid_: Schema, model, payload

## Module Boundaries

```
core (shared infra — unrestricted)
    ↑
promises, reps (domain modules — siblings cannot import each other)
    ↑
   rag (retrieval)
    ↑
  agents (LangGraph orchestration)
```

## Example Dialogue

**User**: Did the MP from Varanasi keep their promise about building a hospital?

**System**: An Agent is spun up for this request. It queries the RAG module for relevant chunks about Varanasi MP's promises. The RAG module retrieves from the embedded Chroma index and may delegate synthesis to the agents module. The answer includes citations to source documents.

**Dev**: If we need to add voting records, where does it go?

**Architect**: It's a new domain module — `voting` — sitting alongside `promises` and `reps`. It can depend on `rag` but not its siblings.
