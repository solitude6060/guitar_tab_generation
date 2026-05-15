from __future__ import annotations

from pathlib import Path


def test_compose_declares_required_profiles_and_services() -> None:
    compose = Path("docker-compose.yml")
    assert compose.exists()
    text = compose.read_text(encoding="utf-8")

    for service in ["app:", "ai-gpu:", "ollama:", "cloud-backup:"]:
        assert service in text
    for profile in ['"dev"', '"gpu-ai"', '"llm"', '"cloud-backup"']:
        assert profile in text
    assert "docker/Dockerfile.dev" in text
    assert "docker/Dockerfile.gpu" in text
    assert "INSTALL_HEAVY_AI" in text
    assert "NVIDIA_VISIBLE_DEVICES" in text
    assert "MINIMAX_API_KEY" in text
    assert "source: ./src" in text
    assert "source: ./tests" in text
    assert "target: /workspace\n" not in text
    assert ".omx" not in text
    assert ".venv" not in text


def test_dockerignore_excludes_local_state_and_secrets() -> None:
    dockerignore = Path(".dockerignore")
    assert dockerignore.exists()
    ignored = set(dockerignore.read_text(encoding="utf-8").splitlines())

    for required in [".omx", ".venv", ".env", ".pytest_cache", "__pycache__", "out", ".git"]:
        assert required in ignored


def test_env_example_uses_placeholders_only() -> None:
    env_example = Path(".env.example")
    assert env_example.exists()
    text = env_example.read_text(encoding="utf-8")

    assert "MINIMAX_API_KEY=" in text
    assert "your_minimax_api_key_here" in text
    assert "INSTALL_HEAVY_AI=false" in text
    assert "sk-" not in text
    assert "Bearer " not in text


def test_docker_docs_have_traditional_chinese_version() -> None:
    english = Path("docs/docker.md")
    zh_tw = Path("docs/docker.zh-TW.md")

    assert english.exists()
    assert zh_tw.exists()
    zh_text = zh_tw.read_text(encoding="utf-8")
    for required in ["Docker Compose", "繁體中文", "gpu-ai", "MiniMax", ".omx"]:
        assert required in zh_text
