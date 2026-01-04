# Shift Roaster 📅

A modern, containerized Flask application for managing team shifts, featuring a premium glassmorphism UI, PostgreSQL persistence, and Prometheus monitoring.

## ✨ Features

- **Shift Management**: Weekly and Monthly views for assigning and viewing member shifts.
- **Team Management**: Admin interface for managing members with full profiles (Full Name, Member ID, Email).
- **Premium UI**: Stunning glassmorphism design with dynamic background images and branded watermarks.
- **Microservices Ready**:
  - **Dockerized**: Multi-stage Dockerfile for optimized production images.
  - **Kubernetes**: Comprehensive Helm chart with StatefulSet for PostgreSQL.
  - **GitOps**: Ready for Argo CD deployment.
- **Security**:
  - **Trivy**: Automated security scanning for secrets and vulnerabilities.
  - **Hashing**: Secure password management using Werkzeug.
- **Observability**:
  - **Prometheus**: Metrics export via `/metrics`.
  - **Health Checks**: Specialized `/health` endpoint for Kubernetes probes.

## 🚀 Getting Started

### Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run Tests**:
   ```bash
   python -m pytest tests/test_app.py
   ```
3. **Start Application**:
   ```bash
   python app.py
   ```
   *Note: Defaults to SQLite for local development.*

### Kubernetes Deployment (Kustomize)

1. **Build & Push Image**: (Same as Helm)
2. **Deploy Base**:
   ```bash
   kubectl apply -k k8s/base
   ```
3. **Deploy Production Overlay**:
   ```bash
   kubectl apply -k k8s/overlays/production
   ```
4. **Deploy Preview Environment**:
   ```bash
   kubectl apply -k k8s/overlays/preview
   ```
5. **Deploy Post-Production Environment**:
   ```bash
   kubectl apply -k k8s/overlays/post_prod
   ```

### Unified Deployment (Helm + Kustomize + Argo CD)

For professional GitOps workflows, use the **Combined Application** pattern:
1. **Argo CD Combined**: Use [application-combined.yaml](file:///c:/Users/C5304531/Desktop/New%20folder1/argocd/application-combined.yaml).
   - It pulls the base logic from the **Helm Chart**.
   - It applies environment-specific overrides (replicas, labels) via **Kustomize Overlays**.

## 🛠 Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Database**: PostgreSQL (StatefulSet) / SQLite (Local)
- **Monitoring**: Prometheus
- **Deployment**: Helm, Kustomize, Kubernetes, GitHub Actions
- **Security**: Trivy

---
*Created with ❤️ for professional team management.*
