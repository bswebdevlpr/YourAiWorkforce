from functools import lru_cache

from src.libs.path import ROOT

# Phase 0: 기획·설계
PRODUCT_DISCOVERY = "phase-0/01-product-discovery"
SYSTEM_ARCHITECT = "phase-0/02-system-architect"
DOMAIN_EXPERT_GENERATOR = "phase-0/03-domain-expert-generator"

# Phase 1: 핵심 인프라
DATA_ENGINEER_P1 = "phase-1/04-data-engineer"
BACKEND_DEVELOPER_P1 = "phase-1/05-backend-developer"
DEVOPS_ENGINEER_P1 = "phase-1/09-devops-engineer"

# Phase 2: 기본 기능
FRONTEND_DEVELOPER_P2 = "phase-2/06-frontend-developer"
BACKEND_DEVELOPER_P2 = "phase-2/07-backend-developer"
DATA_ENGINEER_P2 = "phase-2/08-data-engineer"
QA_LEAD_P2 = "phase-2/10-qa-lead"

# Phase 3: 고급 기능
ALGORITHM_ENGINEER = "phase-3/11-algorithm-engineer"
FRONTEND_DEVELOPER_P3 = "phase-3/12-frontend-developer"
DATA_ENGINEER_P3 = "phase-3/13-data-engineer"

# Phase 4: 품질·보안
FRONTEND_DEVELOPER_P4 = "phase-4/14-frontend-developer"
SECURITY_COMPLIANCE = "phase-4/15-security-compliance"
TECHNICAL_WRITER_P4 = "phase-4/16-technical-writer"
QA_LEAD_P4 = "phase-4/17-qa-lead"

# Phase 5: 검증
DOMAIN_EXPERT_REVIEW = "phase-5/18-domain-expert-review"
QA_FINAL = "phase-5/19-qa-final"

# Phase 6: 배포·마무리
TECHNICAL_WRITER_P6 = "phase-6/20-technical-writer"
DEVOPS_ENGINEER_P6 = "phase-6/21-devops-engineer"
PROJECT_MANAGER = "phase-6/22-project-manager"

# Orchestrator
ORCHESTRATOR = "orchestrator"


@lru_cache
def load_persona(name: str) -> str:
    return (ROOT / "agents" / f"{name}.md").read_text()
