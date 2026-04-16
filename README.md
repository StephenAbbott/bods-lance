# bods-lance: BODS v0.4 → Lance columnar format converter

Convert beneficial ownership data published in line with version 0.4 of the [Beneficial Ownership Data Standard (BODS)](https://standard.openownership.org/en/0.4.0/) into the [Lance](https://lance.org) columnar storage format.

Lance is an open-source, Arrow-native format designed for analytical and AI/ML workloads, with built-in support for vector search, versioning, and cloud storage. Converting BODS data to Lance enables fast columnar analytics over ownership structures — filtering by jurisdiction, querying share percentages, identifying PEP-linked chains — without loading entire datasets into memory.

## Output

Three Lance datasets are written, one per BODS statement type:

```
output/
  entity_statements/          # Legal entities and arrangements
  person_statements/          # Natural persons
  ownership_or_control_statements/   # Interests linking persons/entities to entities
```

Each dataset uses a typed [PyArrow](https://arrow.apache.org/docs/python/) schema. Complex nested fields (names, identifiers, interests, addresses) are preserved as Arrow struct/list columns. High-value fields are promoted to top-level columns for easy filtering:

| Promoted column | Source BODS field |
|---|---|
| `primary_name` | First `legal` or `trading` entry in `names[]` |
| `jurisdiction_code` | `incorporatedInJurisdiction.code` |
| `registered_address` | First `registered` entry in `addresses[]` |
| `has_beneficial_ownership_interest` | Any `interests[].beneficialOwnershipOrControl == true` |
| `max_share_exact` | Highest `interests[].share.exact` across all interests |

## Installation

```bash
pip install bods-lance
```

To also install [LanceDB](https://lancedb.com) (the database layer on top of Lance, useful for queries):

```bash
pip install "bods-lance[lancedb]"
```

Requires Python ≥ 3.9.

## Usage

### Command line

```bash
# Convert a BODS JSON or JSONL file
bods-lance convert gleif.jsonl --output-dir ./gleif-lance

# Overwrite an existing output directory
bods-lance convert gleif.jsonl --output-dir ./gleif-lance --mode overwrite

# Append to existing Lance datasets
bods-lance convert new-statements.jsonl --output-dir ./gleif-lance --mode append

# Print the PyArrow schemas
bods-lance schema
bods-lance schema --type entity
bods-lance schema --type relationship
```

### Python API

```python
from bods_lance.pipeline import BODSLancePipeline

pipeline = BODSLancePipeline(
    input_path="gleif.jsonl",
    output_dir="./gleif-lance",
    mode="create",   # "create" | "overwrite" | "append"
)
counts = pipeline.run()
# {"entity_statements": 2600000, "person_statements": 0, "ownership_or_control_statements": 1800000}
```

### Querying with lance

```python
import lance

# Open a dataset directly
entities = lance.dataset("./gleif-lance/entity_statements")

# Filter to UK entities with a known founding date
uk = entities.to_table(
    filter="jurisdiction_code = 'GB' AND founding_date IS NOT NULL"
)

# Scan only selected columns
names = entities.to_table(columns=["statement_id", "primary_name", "jurisdiction_code"])
```

### Querying with LanceDB

```python
import lancedb

db = lancedb.connect("./gleif-lance")

# List available tables
print(db.table_names())

# Open and query
tbl = db.open_table("entity_statements")
uk_entities = tbl.search().where("jurisdiction_code = 'GB'").limit(100).to_pandas()

# Ownership-or-control: find all BO interests above 25%
ooc = db.open_table("ownership_or_control_statements")
bo_interests = (
    ooc.search()
    .where("has_beneficial_ownership_interest = true AND max_share_exact > 25")
    .to_pandas()
)
```

## Input format

Accepts BODS v0.4 data as:

- **JSON** — a single top-level array of statement objects (`[{...}, {...}]`)
- **JSONL** — one statement object per line (newline-delimited JSON)

The file format is detected automatically from the file extension (`.json` / `.jsonl` / `.ndjson`) or by sniffing the first character.

BODS datasets can be sourced from:

- [OpenOwnership BODS data explorer](https://bods-data.openownership.org/) — includes GLEIF Level 1 & 2 in BODS 0.4
- Any of the BODS conversion pipelines in the [OpenOwnership GitHub organisation](https://github.com/orgs/openownership/repositories)
- Stephen Abbott Pugh's mapping repositories: [bods-brightquery](https://github.com/StephenAbbott/bods-brightquery), [bods-icij-offshoreleaks](https://github.com/StephenAbbott/bods-icij-offshoreleaks), [bods-opencorporates](https://github.com/StephenAbbott/bods-opencorporates), [bods-kyckr](https://github.com/StephenAbbott/bods-kyckr)

## Schema reference

Run `bods-lance schema` to print full column listings. Key schema decisions:

- `share_exact`, `share_minimum`, `share_maximum` are `float64` columns (not nested inside a struct) to allow direct range filtering
- `source_type` is `list<string>` — BODS allows multiple source types per statement
- `replaces_statements` is `list<string>` — links to prior statement IDs for temporal versioning
- `annotations` is a `list<struct>` preserving the full BODS annotation model

## Architecture

```
src/bods_lance/
  schema.py          PyArrow schema definitions (ENTITY_SCHEMA, PERSON_SCHEMA, OOC_SCHEMA)
  pipeline.py        BODSLancePipeline — orchestrates reading, transforming, writing
  cli.py             Click CLI (bods-lance convert / schema)
  ingestion/
    reader.py        BODSReader — streams JSON or JSONL, yields statement dicts
  transform/
    common.py        Shared helpers (build_names, build_identifiers, build_addresses, …)
    entities.py      transform_entity() — entity statement → Lance row
    persons.py       transform_person() — person statement → Lance row
    relationships.py transform_relationship() — OOC statement → Lance row
  output/
    writer.py        LanceWriter — buffers rows, writes Lance datasets via pylance
  utils/
    common.py        get(), coerce_float(), pick_primary_name()
```

## Development

```bash
git clone https://github.com/StephenAbbott/bods-lance.git
cd bods-lance
pip install -e ".[dev]"
pytest
```

## Related projects

- [BODS specification](https://standard.openownership.org/en/0.4.0/) — Beneficial Ownership Data Standard
- [bodsdata](https://github.com/openownership/bodsdata) — BODS to CSV, SQLite, Parquet
- [lib-cove-bods](https://github.com/openownership/lib-cove-bods) — BODS validation
- [LanceDB](https://lancedb.com) — database layer for Lance datasets
- [Lance format specification](https://lance.org/format/)

## License

MIT — see [LICENSE](LICENSE).
