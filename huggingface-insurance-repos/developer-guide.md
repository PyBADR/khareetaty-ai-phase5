# Developer Guide - GCC Insurance Intelligence Lab

## Overview
This guide covers the development workflow, best practices, and governance requirements for building insurance AI applications in the GCC Insurance Intelligence Lab.

## Repository Structure

### Standard Template
Each repository follows this structure:
```
repository-name/
├── app.py                 # Main Gradio application
├── requirements.txt       # Dependencies
├── README.md             # Documentation
├── model_card.md         # Model governance
├── dataset_synthetic.csv # (Optional) Synthetic data
├── test_smoke.py         # Basic tests
├── .github/
│   └── workflows/
│       └── lab-ci-template.yml  # CI/CD automation
└── logs/                 # (Optional) Local logs
```

## Development Process

### 1. Creating New Use Cases
Use the automation system:
```bash
/add-usecase <use-case-name>
```

This generates all required files with proper governance and safety measures.

### 2. Application Development

#### Gradio Applications
- Use rule-based logic (no ML for core functionality)
- Implement synthetic-only data handling
- Include human-in-the-loop requirements
- Add clear disclaimers and governance notices

#### Example Structure:
```python
import gradio as gr
# Application logic here

# Always include governance:
with gr.Blocks() as demo:
    gr.Markdown("""
    # Application Title
    
    ## ⚠️ CRITICAL DISCLAIMER
    This application demonstrates fictional insurance logic using synthetic data only.
    No outputs shall be used for real underwriting, pricing, or policy decisions.
    """)
```

### 3. Data Handling
- Use 100% synthetic data
- No real insurance data allowed
- Fabricate all datasets for educational purposes
- Include appropriate data governance notices

## Governance Requirements

### Mandatory Elements
Every application must include:

1. **Disclaimer Banner** at top of UI
2. **Synthetic Data Notice** in documentation
3. **Human-in-the-Loop Warning** for all decisions
4. **No Production Use Statement** in model card
5. **Educational Purpose Only** in all documentation

### Example Disclaimer:
```
This application demonstrates fictional insurance logic using synthetic data only.
No outputs shall be used for actual underwriting, pricing, reserving, claim approval, or policy issuance.
All data is fabricated for educational purposes. Human-in-the-loop is mandatory for all decisions.
```

## Code Quality Standards

### Imports
- Sort imports alphabetically
- Group standard library, third-party, and local imports
- Use explicit imports over wildcard imports

### Naming Conventions
- Use descriptive variable names
- Follow snake_case for functions and variables
- Use PascalCase for classes
- Be consistent across all repositories

### Documentation
- Include docstrings for all functions
- Comment complex logic
- Maintain README.md with clear instructions
- Update model_card.md with governance details

## Testing

### Smoke Tests
Each repository must include `test_smoke.py`:
```python
def test_app_loads():
    """Test that the main app can be imported without errors"""
    try:
        import app  # Replace with your app filename
        assert hasattr(app, 'demo') or callable(getattr(app, 'main', None))
        print("✓ App loads successfully")
    except Exception as e:
        print(f"✗ App failed to load: {e}")
        raise

if __name__ == "__main__":
    test_app_loads()
```

### Validation Checks
- Import validation
- Basic functionality tests
- Documentation completeness
- Governance compliance

## CI/CD Integration

### GitHub Actions
All repositories use the shared workflow template:
`.github/workflows/lab-ci-template.yml`

This includes:
- Dependency installation
- Import validation
- Smoke testing
- Deployment to Hugging Face Spaces

### Deployment Process
1. Push to `main` branch triggers deployment
2. CI validates imports and runs smoke tests
3. Successful builds deploy to Hugging Face Space
4. Failures trigger notifications

## Security & Compliance

### Data Protection
- No real personal data
- No confidential business logic
- Synthetic data only
- Educational purpose only

### Access Control
- No API keys in code
- Environment variables for secrets
- Synthetic-only functionality
- Human review required

## Best Practices

### Application Design
- Simple, clear UI
- Transparent logic
- Explainable outputs
- Clear governance notices
- Human-in-the-loop enforcement

### Error Handling
- Graceful degradation
- Clear error messages
- No sensitive information disclosure
- Synthetic data fallbacks

### Performance
- Minimal dependencies
- Efficient computation
- No external API calls
- Local execution only

## Troubleshooting

### Common Issues
- Import errors: Check requirements.txt
- Deployment failures: Verify governance compliance
- Data issues: Ensure synthetic data is properly formatted
- UI problems: Test locally before deployment

### Debugging Tips
- Test locally first
- Check governance requirements
- Validate all required files exist
- Ensure synthetic data is properly formatted

## Getting Help

### Resources
- Lab automation playbook
- Governance requirements document
- Sample applications for reference
- Community guidelines

### Support Channels
Contact the GCC Insurance Intelligence Lab team for assistance with:
- Repository setup
- Governance compliance
- Deployment issues
- Best practices guidance

---

**Version**: 1.0  
**Last Updated**: January 2026