# AI Portfolio Workspace

🚀 **Enterprise AI Engineering Portfolio** — 9 production-ready AI projects with governance, evaluation, and orchestration.

## Features

- **9 Core AI Projects**: Fraud Detection, ClaimsGPT, Underwriting, RAG Hub, E-commerce Returns, Fintech Spending, Logistics ETA
- **Streamlit Multipage App**: Interactive demos for all projects
- **Agent Orchestration**: YAML-based agent runner with audit hooks
- **Governance Suite**: Bias detection, drift monitoring, approval workflows
- **RAG Evaluation**: Citation coverage and groundedness metrics
- **Artifact Registry**: Semantic versioning with promotion gates
- **Prompt Snapshots**: Auto-save and rollback system
- **Demo Day**: One-click scenario simulations
- **Metrics Dashboard**: Grafana-style visualization
- **Live Orchestrator**: Real-time task routing simulation

## Quick Start

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate synthetic data
make data

# Launch Streamlit app
make run
```

## Project Structure

```
ai-portfolio/
├── libs/              # Shared utilities
├── services/          # Core AI services
├── agents/            # Agent orchestration
├── configs/           # Configuration files
├── playbooks/         # Agent YAML playbooks
├── apps/streamlit/    # Streamlit UI
├── scripts/           # Data generation
├── tests/             # Unit tests
├── artifacts/         # Model & prompt registry
├── data/              # Synthetic datasets
└── logs/              # Audit logs
```

## Built with VERCEPT

This workspace demonstrates enterprise AI engineering best practices.

## MongoDB + VS Code + GitHub

### Run MongoDB locally
```bash
docker compose up -d mongo
```
Set env vars in `.env` (copy from `.env.example`). Open MongoDB Compass and connect to `mongodb://localhost:27017`.

### Seed data into Mongo
```bash
make mongo-seed
```

### Streamlit with Mongo
Select **MongoDB** in the Data Classifier page sidebar. Train → manifest saved locally, mirrored to Mongo if available.

### VS Code
- `.vscode/launch.json` lets you run Streamlit with one click (Run and Debug panel).
- `.vscode/tasks.json` provides tasks for `make data` and `streamlit run`.

### GitHub (first time)
```bash
git init
git add .
git commit -m "feat: data-classifier with Mongo + Streamlit + VS Code"
git branch -M main
git remote add origin https://github.com/<YOUR_USER>/<YOUR_REPO>.git
git push -u origin main
```
> Never commit `.env` or secrets. We already ignore `.env`.

### Quick run (cheat sheet)
```bash
# 0) (Optional) start MongoDB locally
docker compose up -d mongo

# 1) Python env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) Seed local data (and Mongo if you want)
make data
make mongo-seed   # optional

# 3) Run Streamlit
make run
# Sidebar → Data Source: MongoDB
```
