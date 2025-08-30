# 🎯 SenialSOLIDApp - Modernization Project

**Domain-Driven Design (DDD) Signal Processing Application with SOLID Principles**

---

## 📋 **Project Overview**

SenialSOLIDApp is a Python application for signal acquisition, processing, and visualization that serves as a practical example of:

- **SOLID Principles** implementation in Python
- **Domain-Driven Design (DDD)** architecture  
- **Clean Architecture** with clear separation of concerns
- **Modern Python development** practices and tools

This project is currently undergoing **comprehensive modernization** to update from legacy Python 3.4 to modern Python 3.11 LTS with enhanced security, testing, and maintainability.

---

## 🚀 **Modernization Status**

| Component | Current | Target | Status |
|-----------|---------|--------|---------|
| **Python Version** | 3.4 (EOL) | 3.11 LTS | 🔄 In Progress |
| **Security** | Critical vulnerabilities | Zero critical | 🔄 In Progress |  
| **Testing** | 0% coverage | 80%+ coverage | 📋 Planned |
| **CI/CD** | Manual | Automated | 📋 Planned |
| **Dependencies** | Manual | Modern management | 📋 Planned |

**Current Sprint:** [Sprint 1 - Infrastructure & Security](https://vvalotto.atlassian.net/wiki/spaces/~62acd5154639000068d60d4a/pages/147685404/)  
**Project Management:** [Jira Board](https://vvalotto.atlassian.net/jira/software/projects/SSA/boards/73)  
**Documentation:** [Confluence Workspace](https://vvalotto.atlassian.net/wiki/spaces/~62acd5154639000068d60d4a/pages/147685377/)

---

## 🏗️ **Architecture**

### Domain-Driven Design Structure

```
📦 SenialSOLIDApp/
├── 01_presentacion/          # Presentation Layer
│   ├── consola/             # Console Interface
│   └── webapp/              # Web Interface (Flask)
├── 03_aplicacion/           # Application Layer  
│   ├── contenedor/          # DI Container
│   ├── managers/            # Application Services
│   └── datos/               # Configuration
├── 04_dominio/              # Domain Layer
│   ├── modelo/              # Domain Entities
│   ├── adquisicion/         # Domain Services
│   ├── procesamiento/       # Domain Services
│   └── repositorios/        # Repository Interfaces
└── 05_Infraestructura/      # Infrastructure Layer
    ├── acceso_datos/        # Data Access
    └── utilidades/          # Cross-cutting Concerns
```

### SOLID Principles Implementation

- **Single Responsibility**: Each class has one clear responsibility
- **Open/Closed**: Factory patterns allow extension without modification  
- **Liskov Substitution**: Polymorphic signal hierarchies
- **Interface Segregation**: Specific, cohesive abstract interfaces
- **Dependency Inversion**: Dependencies on abstractions, not concretions

---

## 🛠️ **Development Setup**

### Prerequisites (Target Environment)

- **Python 3.11+** (LTS version)
- **Git** for version control
- **Virtual Environment** (venv/conda)

### Current Setup (Legacy - Being Modernized)

⚠️ **Note**: This setup is being modernized in Sprint 1. Check [SSA-6](https://vvalotto.atlassian.net/browse/SSA-6) for progress.

```bash
# Current legacy setup (Python 3.4)
git clone https://github.com/vvalotto/SenialSOLIDApp.git
cd SenialSOLIDApp

# Legacy dependencies (being updated)
# Manual installation currently required
```

### Target Modern Setup (Sprint 1 Goal)

```bash
# Modern setup (Coming in Sprint 1)
git clone https://github.com/vvalotto/SenialSOLIDApp.git
cd SenialSOLIDApp

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies (modern)
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# Run setup
python -m setup
```

---

## 🎯 **Usage**

### Console Interface

```bash
# Run console application
cd 01_presentacion/consola
python lanzador.py
```

### Web Interface  

```bash
# Run Flask web application
cd 01_presentacion/webapp  
python views.py
# Access: http://localhost:5000
```

### Signal Processing Pipeline

1. **Acquisition**: Generate or load signal data
   - Senoidal generator
   - File-based acquisition
   - Manual input

2. **Processing**: Apply signal processing algorithms
   - Basic amplification  
   - Threshold filtering
   - Custom processors

3. **Visualization**: Display processed results
   - Console output
   - Web dashboard
   - Data export

---

## 📊 **Project Management**

### Jira Integration

**Project Key:** SSA  
**Active Board:** [SenialSOLID Modernization](https://vvalotto.atlassian.net/jira/software/projects/SSA/boards/73)

#### Current Sprint 1 Issues:
- [SSA-6](https://vvalotto.atlassian.net/browse/SSA-6): Python 3.11 Migration  🔄
- [SSA-7](https://vvalotto.atlassian.net/browse/SSA-7): Security Vulnerabilities Fix 🔄  
- [SSA-8](https://vvalotto.atlassian.net/browse/SSA-8): Dependencies Management 🚫
- [SSA-9](https://vvalotto.atlassian.net/browse/SSA-9): Configuration Externalization 🚫

### Confluence Documentation

**Workspace:** [SenialSOLID Modernization](https://vvalotto.atlassian.net/wiki/spaces/~62acd5154639000068d60d4a/pages/147685377/)

- [📊 Current State Analysis](https://vvalotto.atlassian.net/wiki/spaces/~62acd5154639000068d60d4a/pages/147718145/)
- [📋 Modernization Strategy](https://vvalotto.atlassian.net/wiki/spaces/~62acd5154639000068d60d4a/pages/147718166/)  
- [🎯 Product Backlog](https://vvalotto.atlassian.net/wiki/spaces/~62acd5154639000068d60d4a/pages/147718187/)
- [🚀 Sprint 1 Tracking](https://vvalotto.atlassian.net/wiki/spaces/~62acd5154639000068d60d4a/pages/147685404/)

---

## 🔧 **Development Workflow**

### Branching Strategy

- **`master`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/SSA-X-description`**: Feature branches linked to Jira tickets
- **`hotfix/critical-fix`**: Critical fixes

### Commit Convention

```
type(scope): brief description

- More detailed explanation if needed
- Reference to Jira ticket and Confluence docs

Related: SSA-X (ticket link)
Confluence: [page link if applicable]
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

### Pull Request Process

1. Create feature branch from `develop`
2. Link to Jira ticket in PR title: `[SSA-X] Feature description`
3. Update Confluence documentation if needed
4. Ensure tests pass (coming in Sprint 4)
5. Request code review
6. Merge to `develop` after approval

---

## 🧪 **Testing** (Coming in Sprint 4)

### Test Structure (Planned)
```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests  
├── fixtures/          # Test data
└── conftest.py        # Pytest configuration
```

### Running Tests (Future)
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Coverage report
pytest --cov=. --cov-report=html
```

---

## 🚀 **Deployment** (Coming in Sprint 4)

### GitHub Actions CI/CD (Planned)

```yaml
# .github/workflows/ci.yml (Coming Soon)
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest
      - name: Security scan
        run: bandit -r .
```

---

## 🎓 **Educational Value**

This project serves as:

- **Case Study** for legacy code modernization
- **Practical Example** of SOLID principles in Python  
- **Teaching Material** for Software Engineering courses
- **Demonstration** of modern Python development practices
- **Reference Implementation** of Domain-Driven Design

### Learning Objectives

Students can learn:
- How to apply SOLID principles in real code
- Domain-Driven Design implementation
- Legacy code modernization strategies  
- Modern Python development workflow
- Integration of development tools (GitHub + Jira + Confluence)

---

## 📈 **Roadmap**

### Sprint 1: Infrastructure & Security (Current)
- [x] Python 3.11 migration (In Progress)
- [ ] Security vulnerabilities resolution  
- [ ] Modern dependency management
- [ ] Configuration externalization

### Sprint 2: Web Framework (Weeks 3-4)
- [ ] Flask modernization
- [ ] Bootstrap 5 UI upgrade
- [ ] Responsive design improvements

### Sprint 3: Code Quality (Weeks 5-6)  
- [ ] Structured logging implementation
- [ ] Error handling improvements
- [ ] Input validation
- [ ] Code quality metrics

### Sprint 4: Testing & Automation (Weeks 7-8)
- [ ] Unit test suite (80% coverage)
- [ ] Integration tests
- [ ] CI/CD pipeline
- [ ] Performance testing

### Sprint 5: Documentation & UX (Weeks 9-10)
- [ ] Complete technical documentation
- [ ] Educational materials
- [ ] User experience improvements
- [ ] Final optimizations

---

## 🤝 **Contributing**

### For Students and Developers

1. Check [current issues](https://vvalotto.atlassian.net/jira/software/projects/SSA/issues) in Jira
2. Read the [contributing guidelines](https://vvalotto.atlassian.net/wiki/spaces/~62acd5154639000068d60d4a/pages/147718208/) in Confluence
3. Fork the repository
4. Create a feature branch: `git checkout -b feature/SSA-X-description`
5. Make changes following our coding standards
6. Update documentation in Confluence if needed
7. Submit a pull request with Jira ticket reference

### For Educators

This project can be used for:
- Software Engineering courses
- Design Patterns workshops  
- Legacy code modernization case studies
- Agile development demonstrations

Contact: vvalotto@gmail.com for educational collaboration

---

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 **Links**

- **🎯 Project Management**: [Jira Board](https://vvalotto.atlassian.net/jira/software/projects/SSA/boards/73)
- **📚 Documentation**: [Confluence Workspace](https://vvalotto.atlassian.net/wiki/spaces/~62acd5154639000068d60d4a/pages/147685377/)
- **📊 Current Sprint**: [Sprint 1 Tracking](https://vvalotto.atlassian.net/wiki/spaces/~62acd5154639000068d60d4a/pages/147685404/)
- **📈 Metrics**: [Progress Dashboard](https://vvalotto.atlassian.net/wiki/spaces/~62acd5154639000068d60d4a/pages/147718229/)

---

## 📞 **Contact**

**Victor Valotto**  
📧 Email: vvalotto@gmail.com  
🎓 Institution: Universidad Adventista del Plata  
💼 Role: Profesor de Ingeniería de Software

---

*Last Updated: 30 August 2025*  
*Project Status: 🚀 Sprint 1 Active - Infrastructure & Security*