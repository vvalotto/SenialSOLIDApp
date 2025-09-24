# Contributing to SenialSOLIDApp

**Epic:** SSA-3 [EPIC-QUALITY] Mejoras de Calidad y Mantenibilidad
**Ticket:** SSA-27 - Code Documentation Standards
**Fecha:** 2025-09-24
**Versión:** 1.0

---

## 🎯 **Overview**

Welcome to SenialSOLIDApp! This guide outlines our contribution standards, with special emphasis on code documentation requirements established in **SSA-27**. We follow Domain-Driven Design (DDD) principles and maintain high code quality standards.

---

## 📋 **Table of Contents**

1. [Getting Started](#getting-started)
2. [Development Workflow](#development-workflow)
3. [Code Documentation Standards](#code-documentation-standards)
4. [Code Quality Requirements](#code-quality-requirements)
5. [Testing Guidelines](#testing-guidelines)
6. [Pull Request Process](#pull-request-process)
7. [Architecture Guidelines](#architecture-guidelines)
8. [Style Guides](#style-guides)

---

## 🚀 **Getting Started**

### Prerequisites

- Python 3.8+
- Flask framework knowledge
- Understanding of DDD principles
- Familiarity with SOLID principles

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd SenialSOLIDApp
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Review documentation:**
   - Read `docs/SSA-27_DOCUMENTATION_STANDARDS.md`
   - Review `docs/DOCSTRING_TEMPLATES.md`
   - Check `DEVELOPER_ONBOARDING.md`

---

## 🔄 **Development Workflow**

### Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/SSA-XX-description`: Feature branches
- `hotfix/description`: Critical fixes

### Commit Standards

```bash
git commit -m "feat(SSA-XX): Brief description of change

Detailed description explaining:
- What was changed and why
- Business impact or technical rationale
- Any breaking changes or migration steps

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 📝 **Code Documentation Standards**

> **IMPORTANT:** Following SSA-27 implementation, ALL code must meet our documentation standards.

### 1. **Documentation Coverage Requirements**

| Code Type | Coverage Target | Docstring Style | Type Hints |
|-----------|-----------------|-----------------|-------------|
| **Domain Models** | 100% | Google Style | Required |
| **Application Services** | 100% | Google Style | Required |
| **Infrastructure** | 90% | Google Style | Required |
| **Presentation Layer** | 85% | Google Style | Required |
| **Utilities** | 80% | Google Style | Recommended |

### 2. **Google Style Docstrings**

**All functions and classes MUST use Google Style docstrings:**

```python
def domain_operation(self, param: str, optional: int = 0) -> bool:
    """Brief description of the domain operation.

    Longer description explaining business purpose, DDD context,
    and any important implementation details.

    Args:
        param: Description with business meaning
        optional: Optional parameter with default behavior

    Returns:
        bool: Description of return value and business significance

    Raises:
        DomainException: When business rules prevent operation
        ValidationException: When input validation fails

    Example:
        >>> entity.domain_operation("valid_input", 5)
        True

    Note:
        Important considerations about business rules or usage.
    """
```

### 3. **Required Sections by Context**

| Context | Brief | Args/Returns | Raises | Example | Note |
|---------|-------|--------------|--------|---------|------|
| **Public APIs** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Domain Logic** | ✅ | ✅ | ✅ | 🔶 | ✅ |
| **Infrastructure** | ✅ | ✅ | ✅ | 🔶 | 🔶 |
| **Private Methods** | ✅ | 🔶 | 🔶 | ❌ | 🔶 |

**Legend:** ✅ Required | 🔶 Recommended | ❌ Optional

### 4. **Type Hints**

**All public APIs and domain logic MUST include comprehensive type hints:**

```python
from typing import List, Dict, Optional, Union, Any

def process_signals(
    signals: List[Senial],
    config: Dict[str, Any]
) -> Optional[ProcessingResult]:
    """Process multiple signals with configuration."""
```

### 5. **Domain-Specific Documentation**

**Emphasize business language and DDD concepts:**

```python
class Senial(SenialBase):
    """Domain entity representing a signal in the signal processing system.

    A Senial encapsulates signal data and behavior following DDD principles.
    It maintains signal values, metadata, and provides operations for
    signal manipulation within domain constraints.

    Business Rules:
        - Signal capacity cannot exceed configured maximum (tamanio)
        - All values must be numeric (int or float)
        - Signal ID must be unique within the system
    """
```

---

## 🔍 **Code Quality Requirements**

### Quality Gates

Before submitting a PR, ensure your code passes:

```bash
# Documentation linting
pydocstyle src/

# Type checking (if configured)
mypy src/

# Code formatting
black src/

# Import sorting
isort src/
```

### Documentation Quality Metrics

| Metric | Target | Tool |
|--------|--------|------|
| **Docstring Coverage** | 90%+ | pydocstyle |
| **Type Hint Coverage** | 85%+ | mypy |
| **Documentation Lint Score** | 9.0/10 | pydocstyle |

---

## 🧪 **Testing Guidelines**

### Test Documentation

**Test functions MUST be documented:**

```python
def test_signal_capacity_enforcement(self):
    """Test that signal capacity limits are properly enforced.

    Verifies business rule: signals cannot exceed their configured
    maximum capacity (tamanio) to prevent memory issues.

    Test Scenarios:
        1. Adding values within capacity succeeds
        2. Exceeding capacity raises ValidationException
        3. Capacity validation includes proper error context

    This test validates critical business constraint enforcement.
    """
```

### Test Coverage Requirements

- **Unit Tests:** 90%+ coverage for domain logic
- **Integration Tests:** 80%+ coverage for application services
- **API Tests:** 100% coverage for public endpoints

---

## 📤 **Pull Request Process**

### 1. **Pre-PR Checklist**

- [ ] All new code has Google Style docstrings
- [ ] Type hints added to public APIs
- [ ] pydocstyle passes without errors
- [ ] Tests written and passing
- [ ] Documentation updated if needed
- [ ] Commit messages follow standards

### 2. **PR Description Template**

```markdown
## 📋 Summary

Brief description of changes and ticket reference (SSA-XX).

## 🔍 Changes Made

- **Domain:** Changes to business logic
- **Application:** Changes to use cases/services
- **Infrastructure:** Changes to data access/external services
- **Presentation:** Changes to web interface/API

## 📝 Documentation Updates

- [ ] Added docstrings to new functions/classes
- [ ] Updated existing documentation
- [ ] Added examples and usage notes
- [ ] Type hints comprehensive

## 🧪 Testing

- [ ] Unit tests added/updated
- [ ] Integration tests passing
- [ ] Manual testing completed

## ✅ Quality Gates

- [ ] pydocstyle: ✅ No errors
- [ ] Type checking: ✅ Passing
- [ ] Code coverage: ✅ Meets targets
- [ ] Architecture compliance: ✅ Verified

## 📸 Screenshots (if applicable)

[Add screenshots for UI changes]
```

### 3. **Review Criteria**

**Code will be reviewed for:**

- **Documentation Quality:** Complete, accurate docstrings
- **Business Language:** Proper domain terminology usage
- **Architecture Compliance:** Adherence to DDD patterns
- **Error Handling:** Integration with SSA-26 patterns
- **Security:** Input validation and sanitization
- **Performance:** No obvious performance regressions

---

## 🏗️ **Architecture Guidelines**

### DDD Layer Organization

```
senialsolidapp/
├── dominio/           # Domain Layer
│   ├── modelo/        # Entities, Value Objects
│   └── servicios/     # Domain Services
├── aplicacion/        # Application Layer
│   ├── managers/      # Application Services
│   └── validation/    # Use Case Validation
├── infraestructura/   # Infrastructure Layer
│   ├── acceso_datos/ # Repositories, Data Access
│   └── externa/       # External Services
└── presentacion/      # Presentation Layer
    ├── webapp/        # Web Interface
    └── api/           # REST API
```

### Documentation by Layer

| Layer | Documentation Focus |
|-------|-------------------|
| **Domain** | Business rules, entities, domain language |
| **Application** | Use cases, orchestration, transaction boundaries |
| **Infrastructure** | Technical implementation, external integration |
| **Presentation** | API contracts, user interaction patterns |

---

## 🎨 **Style Guides**

### Python Code Style

- **PEP 8** compliance for code formatting
- **Google Style** docstrings (mandatory)
- **Type hints** for all public APIs
- **Meaningful names** using domain language

### Documentation Style

- **Business-first language** in domain layer
- **Clear examples** for public APIs
- **Error scenarios** documented with context
- **Performance notes** where relevant

### File Organization

```python
"""Module-level docstring explaining purpose and context."""

from typing import List, Dict, Optional
import standard_library
import third_party
from local_imports

logger = get_logger(__name__)

class DomainEntity:
    """Class-level docstring with business context."""

    def public_method(self) -> ReturnType:
        """Method docstring with complete documentation."""
```

---

## 🔗 **References**

### Documentation Standards

- **Primary:** `docs/SSA-27_DOCUMENTATION_STANDARDS.md`
- **Templates:** `docs/DOCSTRING_TEMPLATES.md`
- **Examples:** See implemented docstrings in domain layer

### External Resources

- [Google Style Python Docstrings](https://google.github.io/styleguide/pyguide.html)
- [PEP 484 Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [Domain-Driven Design Patterns](https://martinfowler.com/tags/domain%20driven%20design.html)

---

## ❓ **Getting Help**

### Communication Channels

- **Technical Questions:** Create GitHub issue with `question` label
- **Documentation Issues:** Reference SSA-27 ticket
- **Architecture Decisions:** Discuss in team meetings

### Common Issues

1. **pydocstyle errors:** Check `docs/DOCSTRING_TEMPLATES.md`
2. **Type hint issues:** Review existing examples in codebase
3. **Business language:** Consult domain expert or documentation

---

## 🎯 **Success Criteria**

Your contribution is ready when:

- ✅ **Documentation:** All code has Google Style docstrings
- ✅ **Quality:** Passes all linting and quality gates
- ✅ **Testing:** Comprehensive test coverage
- ✅ **Architecture:** Follows DDD principles
- ✅ **Review:** Approved by team members

---

## 📝 **Changelog**

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-09-24 | 1.0 | Initial CONTRIBUTING.md creation with SSA-27 standards | Victor Valotto |

---

**Thank you for contributing to SenialSOLIDApp! 🚀**

*This document is part of SSA-27 implementation and will be updated as standards evolve.*