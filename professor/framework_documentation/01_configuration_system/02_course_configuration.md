---
title: "Course Configuration Parser"
type: "note"
date: 2025-01-21
author: "Framework Team"
summary: "Technical documentation for course.yml parsing and metadata handling"
difficulty: "medium"
tags: ["configuration", "parsing", "course-metadata"]
---

# Course Configuration Parser

The course configuration parser (`professor/framework_code/parsers/course_parser.py`) handles class offering metadata stored in `professor/course.yml`.

## Overview

The course parser provides:
- **Nested data structure** validation with dataclasses
- **Course metadata** management (professor info, resources)
- **Type-safe parsing** with proper error handling
- **Integration** with Hugo site generation

## Architecture

### Data Classes

```python
@dataclass
class ProfessorInfo:
    name: str
    email: str
    office_hours: str
    office_location: str

@dataclass
class CourseResources:
    repository: str
    shared_drive: str
    syllabus: str
    announcements_feed: str

@dataclass
class CourseConfig:
    course_name: str
    course_code: str
    semester: str
    professor: ProfessorInfo
    resources: CourseResources
    contact_policy: str
    unknown_fields: Dict[str, Any]
```

### CourseParser Class

The parser validates:
- **Required top-level fields**: course_name, course_code, semester
- **Nested structures**: professor and resources sections
- **Email validation**: Basic email format checking
- **Unknown fields**: Captures unrecognized keys for extensibility

## Usage

### Basic Usage

```python
from professor.framework_code.parsers.course_parser import load_course_config

# Load and validate course configuration
config = load_course_config()
print(f"Course: {config.course_name}")
print(f"Professor: {config.professor.name}")
```

### Error Handling

```python
from professor.framework_code.parsers.course_parser import CourseParser, CourseParserError

try:
    parser = CourseParser()
    config = parser.parse()
except CourseParserError as e:
    print(f"Course configuration error: {e}")
```

### Accessing Nested Data

```python
# Professor information
prof = config.get_professor_info()
print(f"Email: {prof.email}")
print(f"Office: {prof.office_location}")

# Course resources
resources = config.get_resources()
print(f"Repository: {resources.repository}")
print(f"Syllabus: {resources.syllabus}")
```

## Validation Rules

### Required Fields
- `course_name`: Full name of the course
- `course_code`: Course identifier (e.g., "CS101")
- `semester`: Semester and year
- `professor`: Nested professor information
- `resources`: Nested resource information
- `contact_policy`: Communication guidelines

### Professor Section Validation
- `name`: Professor's full name
- `email`: Valid email address (basic format check)
- `office_hours`: Office hours description
- `office_location`: Office location/address

### Resources Section Validation
- `repository`: Course repository URL
- `shared_drive`: Shared drive URL
- `syllabus`: Syllabus file name
- `announcements_feed`: Announcements file name

## Integration Points

### Hugo Integration
- Course metadata populates Hugo site parameters
- Professor information used in content attribution
- Resources linked in navigation and footers

### Theme System
- Course name appears in site title
- Professor contact info in theme components
- Resource links in navigation menus

### Content Generation
- Author field defaults to professor name
- Course information in generated indices
- Contact policy in footer components

## Error Messages

The parser provides specific error messages for:
- Missing required fields at any level
- Invalid nested structure (non-dictionary)
- Email format validation failures
- Type validation errors

## Example Configuration

```yaml
course_name: "Introduction to Data Science"
course_code: "DS101"
semester: "Fall 2025"
professor:
  name: "Dr. Jane Doe"
  email: "jane.doe@example.edu"
  office_hours: "Tue 14:00-16:00, Room 123"
  office_location: "Building A, Room 123"
resources:
  repository: "github.com/university/ds101"
  shared_drive: "https://drive.example.com/ds101"
  syllabus: "syllabus.pdf"
  announcements_feed: "announcements.md"
contact_policy: "Email within 24h."
```

## Future Extensions

The unknown fields mechanism supports future additions:

```yaml
# Future course.yml extensions
schedule:
  - day: "Monday"
    time: "10:00-11:30"
    location: "Room 205"
grading:
  homework: 40
  midterm: 25
  final: 25
  participation: 10
```

## Testing

Test the parser:
```bash
cd professor/framework_code/parsers
python3 course_parser.py
```

Expected output shows successful parsing of current `professor/course.yml` configuration. 