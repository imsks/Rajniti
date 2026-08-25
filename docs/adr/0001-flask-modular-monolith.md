# Flask Modular Monolith for Backend

The Rajniti backend is a Flask modular monolith with strict inter-module boundaries enforced by import-linter, not a collection of microservices.

**Context**: Political accountability features (promises, representatives, RAG, agents) are tightly coupled in practice — almost every user request touches multiple domains. Microservices would add operational complexity without clear scaling benefits at current traffic levels.

**Decision**: Single Flask application with modules (`promises`, `reps`, `rag`, `agents`) that communicate via DTOs through public facades. Module boundaries are enforced at CI time by `import-linter`. This gives us logical separation without the operational overhead of service meshes and distributed tracing.

**Dependency Direction**:
```
core (unrestricted)
    ↑
promises, reps (domain siblings — no cross-import)
    ↑
   rag
    ↑
  agents
```

**Consequences**: Deployments are atomic (good for consistency), but we can't scale individual modules independently. If we hit genuine scaling needs, we can extract a module to a separate service — the DTO boundaries make this straightforward.
