---
title: "DNA Configuration Parser"
type: "note"
date: 2025-01-21
author: "Framework Team"
summary: "Technical documentation for dna.yml parsing, validation, and extensibility system"
difficulty: "medium"
tags: ["configuration", "parsing", "validation"]
---

# DNA Configuration Parser

The DNA configuration parser (`professor/framework_code/parsers/dna_parser.py`) handles framework-level metadata stored in `dna.yml` at the repository root.

## Overview

The DNA parser provides:
- **Type-safe parsing** with `DNAConfig` dataclass
- **Validation** of required and optional fields
- **Extensibility** through unknown field handling
- **Clear error reporting** with `DNAParserError`

## Architecture

### DNAConfig Dataclass

```python
@dataclass
class DNAConfig:
    # Required fields
    professor_profile: str
    
    # Optional fields with defaults
    theme: str = "default"
    search_mode: str = "simple"
    index_generation: bool = True
    sync_mode: str = "additive"
    authoring_tools: List[str] = field(default_factory=lambda: ["agent"])
    license: str = "CC-BY-4.0"
    
    # Extensibility support
    unknown_fields: Dict[str, Any] = field(default_factory=dict)
```

### DNAParser Class

The parser validates:
- **Required fields**: `professor_profile`
- **Enum values**: `sync_mode` (additive, force), `search_mode` (simple, advanced)
- **Data types**: Ensures proper types for all fields
- **Unknown fields**: Captures unrecognized keys for future extensibility

## Usage

### Basic Usage

```python
from professor.framework_code.parsers.dna_parser import load_dna_config

# Load and validate DNA configuration
config = load_dna_config()
print(f"Professor: {config.professor_profile}")
print(f"Theme: {config.theme}")
```

### Error Handling

```python
from professor.framework_code.parsers.dna_parser import DNAParser, DNAParserError

try:
    parser = DNAParser()
    config = parser.parse()
except DNAParserError as e:
    print(f"Configuration error: {e}")
```

### Extensibility

```python
# Access unknown fields for future features
if config.has_unknown_field("calendar_integration"):
    calendar_enabled = config.get_unknown_field("calendar_integration")
```

## Validation Rules

### Required Fields
- `professor_profile`: GitHub username of the professor

### Optional Field Validation
- `sync_mode`: Must be "additive" or "force"
- `search_mode`: Must be "simple" or "advanced"
- `authoring_tools`: Must be a list
- `index_generation`: Must be boolean

### File Location
- Must be at repository root as `dna.yml`
- Must be valid YAML format
- Must contain at least the required fields

## Integration Points

### Hugo Integration
- `theme` parameter maps to Hugo theme configuration
- `search_mode` controls search implementation
- Professor profile used for content attribution

### Synchronization System
- `sync_mode` controls update strategy (additive vs force)
- `professor_profile` determines directory handling

### Theme System
- `theme` parameter selects active theme from `framework_code/themes/`
- Unknown fields can extend theme configuration

## Error Messages

The parser provides specific error messages:
- Missing required fields
- Invalid enum values
- Type validation errors
- File not found or invalid YAML

## Future Extensibility

The unknown fields mechanism allows adding new configuration options without breaking existing installations:

```yaml
# Current dna.yml
professor_profile: uumami
theme: default

# Future extensions (handled automatically)
calendar_integration: true
build_notifications: slack
content_validation_level: strict
```

## Testing

Run the parser test:
```bash
cd professor/framework_code/parsers
python3 dna_parser.py
```

Expected output shows successful parsing of current `dna.yml` configuration. 