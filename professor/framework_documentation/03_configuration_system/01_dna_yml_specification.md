---
title: "DNA.yml Specification"
type: "documentation"
date: "2024-01-15"
author: "Framework Team"
summary: "Complete specification for dna.yml meta-process configuration file"
difficulty: "medium"
estimated_time: 10
tags: ["configuration", "dna.yml", "meta-process"]
---


The `dna.yml` file at the repository root contains **meta-process controls only** - it manages framework behavior and automation settings but **never contains rendering preferences**.

## Purpose and Scope

`dna.yml` controls:
- Framework automation behavior
- CI/CD pipeline settings
- Repository-wide operational flags
- Cross-directory meta-process coordination

`dna.yml` does **NOT** control:
- Visual appearance (belongs in `config.yml`)
- Course content (belongs in `course.yml`)
- Theme selection (belongs in `config.yml`)
- Hugo rendering settings (belongs in `config.yml`)

## Required Fields

### `professor_profile`
```yaml
professor_profile: uumami
```
**Purpose**: Identifies the professor's directory for sync operations and automation.
**Type**: String
**Required**: Yes
**Example**: The professor's GitHub username

## Framework Meta-Process Settings

### `sync_mode`
```yaml
sync_mode: additive
```
**Purpose**: Controls how sync operations behave
**Type**: String (enum)
**Options**: `additive`, `selective`, `forced`
**Default**: `additive`

### `authoring_tools`
```yaml
authoring_tools: ["agent"]
```
**Purpose**: Specifies which authoring tools are enabled
**Type**: Array of strings
**Options**: `["agent"]`, `["manual"]`, `["agent", "manual"]`

### `license`
```yaml
license: CC-BY-4.0
```
**Purpose**: Default license for framework content
**Type**: String
**Common values**: `CC-BY-4.0`, `MIT`, `GPL-3.0`

## Build and CI/CD Settings

### `hugo_auto_config`
```yaml
hugo_auto_config: true
```
**Purpose**: Enable automatic Hugo configuration generation
**Type**: Boolean
**Default**: `true`

### `accessibility_enabled`
```yaml
accessibility_enabled: true
```
**Purpose**: Enable framework-level accessibility features
**Type**: Boolean
**Default**: `true`

### `index_generation`
```yaml
index_generation: true
```
**Purpose**: Enable automatic index file generation
**Type**: Boolean
**Default**: `true`

## Advanced Meta-Process Options

### `strict_validation`
```yaml
strict_validation: false
```
**Purpose**: Control whether validation failures abort builds
**Type**: Boolean
**Default**: `false`

### `content_validation`
```yaml
content_validation: true
```
**Purpose**: Enable/disable content metadata validation
**Type**: Boolean
**Default**: `true`

### `auto_deploy`
```yaml
auto_deploy: true
```
**Purpose**: Enable automatic deployment workflows
**Type**: Boolean
**Default**: `true`

## File Location and Access

- **Location**: Repository root (`/dna.yml`)
- **Read by**: Framework scripts, CI/CD workflows
- **Modified by**: Framework maintainers, repository administrators
- **Frequency**: Rarely (only for operational changes)

The `dna.yml` file ensures consistent framework behavior across all directories while maintaining the self-contained principle for rendering operations. 