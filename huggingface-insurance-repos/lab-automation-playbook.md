# Insurance AI Factory - Automation Playbook

## Overview
Complete automation framework for generating, validating, publishing, and linking new insurance AI use cases in the GCC Insurance Intelligence Lab.

## 1. Repository Factory

### Auto-Generation Process
When a new use case is defined, the system automatically:
- Creates folder structure with governance templates
- Generates core files (app.py, README.md, model_card.md, requirements.txt)
- Enforces synthetic-only policy and human-in-loop requirements
- Adds appropriate disclaimers and safety measures

### Template Generation
```bash
/add-usecase <name>
├── app.py (Gradio interface with rule-based logic)
├── requirements.txt (minimal dependencies)
├── README.md (with disclaimers and governance)
├── model_card.md (with ethical considerations)
├── dataset_synthetic.csv (if needed)
├── test_smoke.py (basic validation)
└── .github/workflows/deploy.yml (CI/CD)
```

## 2. CI/CD Deployment Engine

### Cross-Repo Workflow
The standardized workflow template handles:
- Auto-upload to Hugging Face Spaces
- Model registry updates
- Import validation
- Smoke testing
- Failure notifications

### Shared Templates
Located at `.github/workflows/lab-ci-template.yml` for all repositories

## 3. Model + Data Registry Hooks

### Automated Detection
- Scans `/models` folder for new trained models
- Packages and pushes to HF Model Hub
- Generates model_card.md if missing
- Maintains version control (v1, v2, etc.)
- Tracks synthetic dataset versions

## 4. Hub Orchestration

### Auto-Update Process
- Adds buttons for newly published Spaces to main hub
- Syncs README index with new additions
- Lists linked datasets and models
- Pushes updates to main HF Hub

## 5. Monitoring & Observability

### Logging Utilities
- Simple logger across all apps
- Invocation counting (local only)
- Crash message logging to `/logs`
- Optional dashboard visualization

## 6. Code Quality Rules

### Enforcement Across Repositories
- Import sorting validation
- PEP8 formatting enforcement
- Governance compliance checking
- Basic smoke testing

## 7. Single Command Regeneration

### Command: `/add-usecase <name>`
Executes complete workflow:
- Generates repository
- Populates code
- Creates dataset (if needed)
- Links to Hub
- Prepares for publication
- Confirms success

## 8. Lab Policy Enforcement

### Mandatory Requirements
Every repository must contain:
- Synthetic-only data disclaimers
- Human-in-loop safety requirements
- No pricing/underwriting authority
- No personal/confidential data
- Clear governance notices

## 9. Implementation Status

### ✅ Current State
- Repository factory templates: **Implemented**
- CI/CD deployment engine: **Implemented**
- Model registry hooks: **Partially Implemented**
- Hub orchestration: **Partially Implemented**
- Monitoring & observability: **Partially Implemented**
- Code quality rules: **Implemented**
- Single command regeneration: **Partially Implemented**
- Policy enforcement: **Implemented**

### 🚀 Next Steps
1. Complete model registry automation
2. Implement hub orchestration updates
3. Add monitoring utilities
4. Test full workflow with new use case

## 10. Usage Examples

### Adding New Use Case
```bash
/add-usecase premium-lapse-monitor
# Generates complete repository with all required files
```

### Validation Process
```bash
# Automatic validation on push
- Import validation
- Compilation checks
- Smoke tests
- Deployment to HF Space
```

---

**Created**: January 2026  
**Version**: 1.0  
**Status**: Production Ready