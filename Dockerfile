# 1. 가벼운 파이썬 3.14 슬림 버전 사용 (16GB RAM 배려)
FROM python:3.13-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필수 OS 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git && rm -rf /var/lib/apt/lists/*

# 4. uv 설치 (가장 최신 버전)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 5. [핵심] 의존성 파일만 먼저 복사하여 '도커 캐시' 극대화
COPY pyproject.toml ./

# 6. uv sync로 초고속 설치 (자동으로 .venv 가상환경을 만들고 설치함)
# --no-dev 옵션으로 개발용 패키지(pytest 등)는 빼고 가볍게 설치
RUN uv sync --no-dev

# 7. 소스 코드 복사 (컴포즈에서 볼륨 연결을 하므로 초기 빌드용)
COPY . .

# 8. 파이썬 실행 성능 최적화 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 9. LangGraph 개발 서버 포트 (기본 8123)
EXPOSE 8123

# 10. 'uv run'을 통해 가상환경(.venv) 내부의 langgraph 명령어를 바로 실행!
CMD ["uv", "run", "langgraph", "dev", "--host", "0.0.0.0", "--port", "8123"]