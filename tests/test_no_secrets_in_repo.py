from pathlib import Path


FORBIDDEN_LITERALS = [
    "coolcookiesd267",
    "keyd3214",
]


def test_no_known_hardcoded_auth_secrets():
    repo_root = Path(__file__).resolve().parents[1]
    files = list(repo_root.rglob("*.py")) + list(repo_root.rglob("*.md"))

    for file_path in files:
        if ".git" in file_path.parts or "__pycache__" in file_path.parts:
            continue
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        for literal in FORBIDDEN_LITERALS:
            assert literal not in content, f"Found forbidden literal in {file_path}"
