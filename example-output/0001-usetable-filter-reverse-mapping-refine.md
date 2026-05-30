---
id: "0001"
title: "useTable Filter Reverse Mapping for syncWithLocation"
status: accepted
date: 2026-05-30
deciders: Jaspreet Singh
issue: "https://github.com/refinedev/refine/issues/7338"
---

## Context

`useTable` with `syncWithLocation: true` serializes filters into the URL on every state
change (`packages/core/src/hooks/useTable/index.ts:337-350`). On page load or browser
back navigation, those URL params are parsed back into `CrudFilter[]` via `parseTableParams`
(`packages/core/src/definitions/table/index.ts:20-32`) and restored into the hook's filter
state correctly.

The gap is the **search form**: the hook has no mechanism to hydrate form fields from the
restored `CrudFilter[]`. Developers are forced to write `useEffect` watchers that call
`form.setFieldsValue(...)` manually, producing render-timing bugs where the form flashes
with empty values before the effect fires.

Two concrete pain points from the issue:

1. **Type coercion** — URL params arrive as strings; form components like `<InputNumber>`
   or `<Select mode="multiple">` expect numbers. No automatic conversion exists.
2. **Split-filter reconstruction** — `onSearch` typically splits a `DatePicker.RangePicker`
   value into two filters (`gte`/`lte`). On reload, no mechanism recombines them into the
   `[Dayjs, Dayjs]` array the picker requires.

**Prior art found in the codebase:**

- `packages/react-table/src/utils/crud-filters-to-column-filters/index.ts:9` —
  `crudFiltersToColumnFilters()` already performs reverse mapping for TanStack Table's
  column filter format. This is the exact pattern needed for forms.
- `packages/antd/src/definitions/filter-mappers/index.ts:31` —
  `rangePickerFilterMapper` handles bidirectional transformation per-column via a
  `mapValue` prop on `<FilterDropdown>`. The pattern is opt-in and per-field.
- `packages/core/src/definitions/table/index.ts:185` — `getDefaultFilter()` extracts
  a single filter's value by field+operator but is never called automatically.

**Constraints:**
- `packages/core` must remain framework-agnostic — no `dayjs`, AntD, or form library imports
- Any solution must be additive — zero breaking changes to existing `useTable` consumers
- The `CrudFilter` discriminated union (`LogicalFilter | ConditionalFilter`) must be handled
  in both the auto-derive and custom-mapper paths

## Decision

We will implement **`onParse` callback in framework-specific wrappers** (Approach B),
supplemented by **automatic `filterValues` derivation** (from Approach A) as a zero-config
baseline.

Concretely:

1. Add `filterValues: Record<string, unknown>` to `useTableReturnType` in
   `packages/core/src/hooks/useTable/index.ts`. Auto-derived from scalar `LogicalFilter`
   entries — no configuration required. Covers the simple case (string, number, boolean
   equality filters) with zero developer effort.

2. Add `onParse?: (filters: CrudFilter[]) => TSearchVariables` to the
   framework-specific `useTable` wrappers in `packages/antd` and `packages/react-hook-form`.
   When provided, the computed `searchFormProps.initialValues` (antd) or
   `defaultValues` (react-hook-form) is set from `onParse(filters)` instead of
   `filterValues`. This covers complex cases: date range reconstruction, custom type
   coercion, multi-field joins.

The combined API is:

```ts
// Zero-config: works for scalar filters automatically
const { searchFormProps, filters, filterValues } = useTable({ syncWithLocation: true });
// filterValues: { status: "active", categoryId: "5" } — use to seed simple forms

// Full control: developer owns the transformation
const { searchFormProps } = useTable({
  syncWithLocation: true,
  onSearch: (values) => [
    { field: "createdAt", operator: "gte", value: values.createdAt[0].toISOString() },
    { field: "createdAt", operator: "lte", value: values.createdAt[1].toISOString() },
    { field: "categoryId", operator: "eq", value: Number(values.categoryId) },
  ],
  onParse: (filters) => ({
    createdAt: [
      dayjs(filters.find(f => "field" in f && f.field === "createdAt" && f.operator === "gte")?.value),
      dayjs(filters.find(f => "field" in f && f.field === "createdAt" && f.operator === "lte")?.value),
    ],
    categoryId: Number(getDefaultFilter("categoryId", filters)),
  }),
});
```

## Approaches Considered

### Approach A — `filterValues` computed property (core hook)

Add `filterValues: Record<string, unknown>` to `useTableReturnType` — auto-derived
from `filters` state, scalar fields only, no type coercion.

**Why not chosen as the only solution:** Doesn't help for split filters (date ranges,
multi-value joins). Type coercion is still manual. The 20% of complex cases — which
are exactly the ones causing the most pain — remain unsolved.

**Kept as:** The zero-config baseline in the final solution.

### Approach B — `onParse` callback in framework wrappers (chosen)

`onParse: (filters: CrudFilter[]) => TSearchVariables` mirrors `onSearch` exactly.
Developer provides the reverse transformation. Framework wrapper calls it and sets
`searchFormProps.initialValues` or `defaultValues` automatically.

**Why chosen:** Perfect API symmetry with `onSearch` — any developer who understands
the forward direction will immediately understand the reverse. No auto-magic that
surprises users. Type-safe — the generic `TSearchVariables` flows through both directions.

### Approach C — Auto-derive + per-field `filterMappers`

Accept `filterMappers?: Record<string, FilterMapper>` at the hook level. Auto-derive
scalars; apply mappers for complex fields.

**Why not chosen:** Introduces a second mapper concept alongside the existing
`rangePickerFilterMapper` / `mapValue` pattern — two similar but different APIs for the
same problem. The `onParse` escape hatch in the chosen approach covers the same power
use case with a simpler mental model.

## Trade-Off Table

| Criterion          | A — filterValues | B — onParse | C — filterMappers |
|--------------------|-----------------|-------------|-------------------|
| Ship speed         | High            | High        | Medium            |
| Covers 80% case   | Partial         | No          | **Yes**           |
| Covers 100% case  | No              | **Yes**     | Yes               |
| API consistency    | Medium          | **High**    | Medium            |
| Breaking changes   | None            | None        | None              |
| Learning curve     | Low             | Medium      | Low               |

## Consequences

**Positive:**
- `filterValues` solves the common case (scalar filters) with zero code change for
  existing consumers — opt-in by reading the new return value
- `onParse` is symmetric with `onSearch` — existing docs and mental model transfer
  directly
- No changes to `parseTableParams` or the URL serialization layer — purely additive
- Framework packages (antd, react-hook-form) get the full solution; core stays clean

**Negative / watch for:**
- `filterValues` auto-derivation only handles `LogicalFilter` entries — `ConditionalFilter`
  (`and`/`or`) entries are ignored. Document this clearly to avoid confusion.
- `onParse` runs on every `filters` state change, not just on page load. Consumers
  with expensive transformations should memoize the callback with `useCallback`.
- If `onParse` is provided, `filterValues` is still computed — two sources of truth for
  "current form values." Antd and react-hook-form wrappers must prefer `onParse` result
  when both are present.

## Key Files

- `packages/core/src/hooks/useTable/index.ts` — add `filterValues` derivation + return
- `packages/core/src/hooks/useTable/index.ts:142-163` — extend `useTableReturnType`
- `packages/antd/src/hooks/table/useTable/index.ts` — add `onParse` prop + wire to `searchFormProps.initialValues`
- `packages/react-hook-form/src/useTable/index.ts` — add `onParse` prop + wire to `defaultValues`
- `packages/core/src/definitions/table/index.ts:185` — `getDefaultFilter` is a useful
  building block for `onParse` implementations; add to public docs
- `packages/react-table/src/utils/crud-filters-to-column-filters/index.ts` — reference
  implementation of reverse mapping (same pattern, different target format)

## Related ADRs

- None (first ADR in this project)
