import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PREFLIGHT = ROOT / "deploy" / "preflight.py"


def run_preflight(tmp_path: Path, content: str) -> subprocess.CompletedProcess[str]:
    env_file = tmp_path / ".env"
    env_file.write_text(content, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(PREFLIGHT), str(env_file)],
        check=False,
        capture_output=True,
        text=True,
    )


def test_deploy_preflight_accepts_safe_pilot_configuration(tmp_path: Path) -> None:
    result = run_preflight(
        tmp_path,
        """
POSTGRES_PASSWORD=very-long-random-password-12345
ADMIN_API_KEY=very-long-random-admin-key-67890
CORS_ORIGINS=https://travel.example.com
ALLOW_TEST_FIXTURES=false
GOOGLE_PLACES_API_KEY=
OSRM_BASE_URL=https://router.project-osrm.org
NOMINATIM_BASE_URL=https://nominatim.openstreetmap.org
""".strip(),
    )

    assert result.returncode == 0
    assert "Production preflight passed." in result.stdout
    assert "Google coordinate resolver will be disabled" in result.stdout


def test_deploy_preflight_rejects_defaults_and_insecure_cors(tmp_path: Path) -> None:
    result = run_preflight(
        tmp_path,
        """
POSTGRES_PASSWORD=change-me
ADMIN_API_KEY=change-me
CORS_ORIGINS=http://travel.example.com
ALLOW_TEST_FIXTURES=true
""".strip(),
    )

    assert result.returncode == 2
    assert "POSTGRES_PASSWORD" in result.stdout
    assert "ADMIN_API_KEY" in result.stdout
    assert "https://" in result.stdout
    assert "ALLOW_TEST_FIXTURES" in result.stdout
