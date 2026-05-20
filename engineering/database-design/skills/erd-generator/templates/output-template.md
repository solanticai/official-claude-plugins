# ERD — {{schema_name}}

**Source:** {{narrative_or_live}}
**Generated:** {{date}}

---

## Entity List

| Entity | PK | Key columns | Notes |
|--------|-----|------------|-------|
| {{name}} | id (uuid) | {{cols}} | {{notes}} |

---

## Mermaid ERD

```mermaid
erDiagram
  {{ENTITY_A}} ||--o{ {{ENTITY_B}} : "has"
  {{ENTITY_A}} {
    uuid id PK
    text name
  }
  {{ENTITY_B}} {
    uuid id PK
    uuid a_id FK
  }
```

---

## DBML

```dbml
Table {{entity_a}} {
  id uuid [pk, default: `gen_random_uuid()`]
  name text [not null]
}

Table {{entity_b}} {
  id uuid [pk, default: `gen_random_uuid()`]
  a_id uuid [ref: > {{entity_a}}.id]
}
```

---

## Notation Legend

- `||--o{` : one-to-many (left side mandatory, right side optional)
- `||--||` : one-to-one (both mandatory)
- `}o--o{` : many-to-many (both optional)
- `PK` : Primary key
- `FK` : Foreign key
- `"nullable"` annotation on columns that can be null

---

## Open Questions

1. {{question_1}}
2. {{question_2}}
