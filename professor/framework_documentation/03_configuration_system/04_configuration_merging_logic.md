---
author: Framework Team
date: '2024-01-15'
difficulty: medium
estimated_time: 8
slug: 2024-01-15-documentation-configuration-merging-log
slug_locked: true
slug_source: creation_context
summary: How generate_hugo_config.py merges course.yml and config.yml into hugo.toml
tags:
- configuration
- hugo
- merging
title: Configuration Merging Logic
type: documentation
---


This document explains how the `generate_hugo_config.py` script merges configuration from multiple sources to create the final `hugo.toml` file.

## Merge Order

The configuration system reads files in this order:

1. **course.yml** - Course metadata (base layer)
2. **config.yml** - Rendering preferences (override layer)

## Merge Behavior

When the same key exists in both files:
- `config.yml` values **override** `course.yml` values
- This allows course-specific customization of framework defaults

## Example Merge

**course.yml:**
```yaml
course_name: "Data Science 101"
professor_name: "Dr. Jane Smith"
theme:
  name: "default"
```

**config.yml:**
```yaml
theme:
  name: "evangelion"
accessibility:
  default_font: "opendyslexic"
```

**Result:**
```yaml
course_name: "Data Science 101"
professor_name: "Dr. Jane Smith"
theme:
  name: "evangelion"  # config.yml override
accessibility:
  default_font: "opendyslexic"  # config.yml addition
```

This merging strategy enables flexible course customization while maintaining consistent base metadata. 