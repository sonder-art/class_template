---
title: "{{ replace .Name "-" " " | title }}"
type: "note"
date: {{ .Date }}
author: "{{ .Site.Params.professor_name }}"
summary: "Brief summary of this content"
draft: false

# Optional metadata fields
difficulty: "medium"  # easy | medium | hard
prerequisites: []     # array of slugs
estimated_time: 15    # minutes
tags: []             # list of tags
agent: false         # mark agent-specific docs
---

# {{ replace .Name "-" " " | title }}

Brief introduction to this content.

## Overview

Content overview goes here.

## Main Content

Your main content goes here.

## Summary

Key takeaways and summary. 