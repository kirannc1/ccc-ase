# CCC / ASE Technical Stack (Azure-First, ALZ/CAF Aligned)

This document defines the recommended technology stack for the Cognitive Command Center (CCC) and Autonomous Strategy Engine (ASE), derived from:

- `solution.md`
- `architecture.md`
- `data_architecture.md`
- `infrastructure_landscape.md`
- `decision_standards.md`

The default posture is: **Azure-first, hybrid by design, multi-agent execution model, replay/audit first**.

## 1. Experience Layer (UI)

- **Web framework**: `Next.js (React + TypeScript)`
- **UI components**: `Fluent UI` (or equivalent enterprise design system)
- **Visualization**:
  - graph visualization: `Cytoscape.js` (or `Sigma.js`)
  - charts: `ECharts` (or `Plotly`)
- **Auth**: `MSAL` with `Microsoft Entra ID` (OIDC)

## 2. Edge, API, and Access

- **API Gateway**: `Azure API Management (APIM)`
- **Identity**: `Microsoft Entra ID` (RBAC + optional ABAC, PIM for privileged roles)
- **Service-to-service auth**: `Managed Identity` where supported; otherwise federated workload identity
- **Secrets**: `Azure Key Vault` (no hardcoded credentials)

## 3. Runtime and Compute

- **Primary runtime**: `Azure Kubernetes Service (AKS)`
  - separate node pools: API, ingestion, simulation/optimization, AI inference (GPU when needed)
- **Container registry**: `Azure Container Registry (ACR)` (no anonymous pull)
- **Workflows / orchestration (ASE control plane)**:
  - recommended: `Durable Functions` (orchestration-as-a-service) **or** `Temporal` on AKS for long-running workflows
  - command queue: `Azure Service Bus` (reliable commands, approvals, retries)
  - event stream: `Azure Event Hubs` (streaming ingestion, event-driven triggers)

## 4. Backend Services (Microservices)

- **Service framework**: `Python + FastAPI` (agent services, simulation, optimization, decisioning)
- **High-throughput ingestion** (optional where needed): `C#/.NET` or `Java` consumers for Event Hubs
- **Async jobs**: `Kubernetes Jobs` / `KEDA` autoscaling for simulation bursts

## 5. Data Plane (Governed Stores)

- **Raw + curated data lake**: `ADLS Gen2` (raw immutable landing + curated/lakehouse zones)
- **Curated analytics**: lakehouse format on ADLS (e.g., `Delta Lake`), or Azure analytics service chosen by enterprise standard
- **Operational metadata**: `Azure SQL Database`
- **Document store** (scenario registry, decision payloads when appropriate): `Azure Cosmos DB (NoSQL)`
- **Enterprise Knowledge Graph**: `Azure Cosmos DB for Apache Gremlin` (or approved enterprise graph service)
- **Search / retrieval**: `Azure AI Search` (keyword + hybrid + vector where applicable)
- **Caching**: `Azure Cache for Redis`

### 5.1 Decision Ledger (Immutable)

To satisfy replay/audit requirements, implement:

- **Ledger entries**: append-only records (e.g., Cosmos DB container with no updates, only inserts)
- **Artifacts** (SDA snapshots, evidence packs, pareto frontiers, sensitivity reports): immutable blobs in `ADLS/Blob` with hash addressing and retention policy

## 6. Integration and Ingestion

- **Batch ingestion / ELT**: `Azure Data Factory`
- **Streaming ingestion**: `Azure Event Hubs` (Kafka compatibility optional)
- **Workflow messaging**: `Azure Service Bus`
- **Connectors / glue**: `Azure Functions` and/or `Logic Apps` for SaaS integrations
- **Document extraction**: containerized parsing service on AKS (OCR optional)

## 7. AI/ML and LLM Layer

- **MLOps and model governance**: `Azure Machine Learning`
  - model registry + versioning
  - offline evaluation pipelines (promotion gates)
  - managed endpoints for inference (optional)
- **LLM**: `Azure OpenAI`
  - used for explanation/narration derived from structured SDA (DS-001)
  - prompt/template versioning controlled by policy and recorded in ledger
- **Embedding + retrieval** (if required): `Azure OpenAI embeddings` + `Azure AI Search` vector index

## 8. Observability, Security Posture, and Governance

- **Metrics/logs/traces**: `Azure Monitor` + `Log Analytics`
- **App performance**: `Application Insights` + `OpenTelemetry` instrumentation
- **SIEM/SOAR** (optional/enterprise): `Microsoft Sentinel`
- **Cloud security posture**: `Microsoft Defender for Cloud`
- **Policy**: `Azure Policy` (diagnostics, private endpoints, allowed SKUs/regions, tagging)

## 9. DevOps and IaC

- **IaC**: `Bicep` (default) or `Terraform` (if enterprise standard) aligned to ALZ patterns
- **Packaging**: `Helm` for AKS deployments
- **CI/CD**: `GitHub Actions` or `Azure DevOps Pipelines`
- **Secrets in CI/CD**: OIDC federation to Azure; no long-lived secrets in pipelines

## 10. Recommended Libraries / Engines (by capability)

- **Knowledge graph access**: Gremlin client + graph traversal utilities
- **Simulation**:
  - probabilistic modeling: `NumPy`, `SciPy`, `PyMC` (optional)
  - time series: `statsmodels`, `prophet` (optional)
- **Optimization**:
  - linear/constraint programming: `OR-Tools`
  - general optimization: `SciPy optimize`
- **Explainability/attribution**:
  - feature attribution: `SHAP` (where applicable)
  - always derived from structured artifacts (SDA) + evidence pack

## 11. Environment Strategy (ALZ)

- `Platform-Management`, `Platform-Connectivity`, optional `Platform-SharedServices`
- Workload landing zones: `CCC-DevTest`, `CCC-Prod`
- Private endpoints for data plane services in `Prod` by default
- Separate AKS clusters for prod vs non-prod (or at minimum separate namespaces + policies if constrained)

## 12. MVP Stack (Hackathon-Ready Subset)

Minimum set that still proves differentiators (KG + what-if + optimization + explainability + override + replay):

- `AKS`, `ACR`, `APIM`
- `Event Hubs`, `Service Bus`, `Data Factory` (batch can be simulated if needed)
- `ADLS Gen2`, `Azure SQL`, `Cosmos DB` (+ `Gremlin` if possible)
- `Azure AI Search`, `Redis`
- `Azure Machine Learning` (can be minimal), `Azure OpenAI`
- `Key Vault`, `Azure Monitor` (+ Log Analytics)

