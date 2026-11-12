"""Plugin tests: manifest (K1.1), hook wiring and launcher (K1.2), contents (no code_guard, no private data)."""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
RESERVED_PREFIXES = ("claude-", "anthropic-", "anthropics-", "cc-plugin-")
RESERVED_NAMES = {"claude", "anthropic", "anthropics", "claude-code", "claude-mods"}


def load_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_k1_1_manifest_fields():
    """K1.1: plugin.json is valid JSON with name, version 1.0.0, MIT license and references to skills and hooks."""
    m = load_manifest()
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", m["name"])
    assert m["name"] == "homebase"
    assert m["version"] == "1.0.0"
    assert m["license"] == "MIT"
    assert m["author"]["name"]
    assert m["description"].strip()
    assert "antonioblago.com/skills/claude-code-starter-set" in m["description"]
    for key in ("skills", "hooks"):
        assert key in m
    assert (ROOT / m["hooks"]).is_file()
    skills = m["skills"] if isinstance(m["skills"], list) else [m["skills"]]
    for s in skills:
        assert (ROOT / s).is_dir()


def test_k1_1_name_is_not_reserved():
    """K1.1: Claude Code rejects names that pass as Anthropic's own (claude-*, anthropic-*, ...)."""
    name = load_manifest()["name"].lower()
    assert not name.startswith(RESERVED_PREFIXES)
    assert name not in RESERVED_NAMES


def test_k1_1_license_file_is_mit():
    assert "MIT License" in (ROOT / "LICENSE").read_text(encoding="utf-8")


def test_k1_1_skills_have_frontmatter():
    """K1.1: every skill folder has a SKILL.md whose frontmatter name matches the folder."""
    for d in sorted((ROOT / "skills").iterdir()):
        text = (d / "SKILL.md").read_text(encoding="utf-8")
        fm = re.match(r"---\n(.*?)\n---\n", text, re.S)
        assert fm, d
        assert re.search(rf"^name: {re.escape(d.name)}$", fm.group(1), re.M)
        assert re.search(r"^description: .+", fm.group(1), re.M)
    assert {d.name for d in (ROOT / "skills").iterdir()} == {"homebase", "handoff"}


@pytest.mark.skipif(shutil.which("claude") is None, reason="claude CLI not installed")
def test_k1_1_claude_plugin_validate():
    """K1.1: the official validator passes (warnings, e.g. a missing directory icon, are allowed)."""
    r = subprocess.run(["claude", "plugin", "validate", str(ROOT)], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr


def test_k1_2_hooks_use_plugin_root_and_two_events():
    """K1.2: SessionStart and UserPromptSubmit call the launcher through ${CLAUDE_PLUGIN_ROOT}."""
    hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    assert set(hooks) == {"SessionStart", "UserPromptSubmit"}
    flags = {"SessionStart": "--start", "UserPromptSubmit": "--prompt"}
    for event, flag in flags.items():
        cmd = hooks[event][0]["hooks"][0]["command"]
        assert "${CLAUDE_PLUGIN_ROOT}/hooks/run.sh" in cmd and cmd.endswith(flag)
        assert hooks[event][0]["hooks"][0]["timeout"] > 0
    assert (ROOT / "hooks" / "context_guard.py").is_file()


@pytest.mark.skipif(sys.version_info < (3, 10), reason="sys.stdlib_module_names needs 3.10")
def test_k1_2_context_guard_is_stdlib_only():
    """K1.2: no packages beyond the standard library."""
    src = (ROOT / "hooks" / "context_guard.py").read_text(encoding="utf-8")
    mods = set(re.findall(r"^(?:import|from) (\w+)", src, re.M))
    assert mods <= set(sys.stdlib_module_names) | {"__future__"}


@pytest.mark.skipif(shutil.which("sh") is None, reason="sh not available")
def test_k1_3_launcher_runs_hook_and_survives_missing_python(tmp_path):
    """K1.3: the launcher forwards stdin to context_guard.py, and exits 0 silently when no Python is found."""
    run = ROOT / "hooks" / "run.sh"
    env = dict(os.environ, HOME=str(tmp_path), USERPROFILE=str(tmp_path))
    low = tmp_path / "t.jsonl"
    low.write_text(json.dumps({"type": "assistant", "message": {"usage": {"input_tokens": 10}}}) + "\n",
                   encoding="utf-8")
    hook_in = json.dumps({"transcript_path": str(low), "session_id": "s"})
    r = subprocess.run(["sh", str(run), "--prompt"], input=hook_in, capture_output=True, text=True, env=env,
                       timeout=60)
    assert r.returncode == 0 and r.stdout.strip() == ""  # below the threshold: silent
    # Above the threshold the hook answers with JSON.
    big = tmp_path / "big.jsonl"
    big.write_text(json.dumps({"type": "assistant", "message": {"usage": {
        "input_tokens": 10, "cache_read_input_tokens": 400_000}}}) + "\n", encoding="utf-8")
    hook_in = json.dumps({"transcript_path": str(big), "session_id": "s2"})
    r = subprocess.run(["sh", str(run), "--prompt"], input=hook_in, capture_output=True, text=True, env=env,
                       timeout=60)
    assert r.returncode == 0 and "systemMessage" in json.loads(r.stdout)
    # No Python on PATH: still exit 0, no output.
    empty = tmp_path / "bin"
    empty.mkdir()
    sh = shutil.which("sh")
    r = subprocess.run([sh, str(run), "--start"], input="{}", capture_output=True, text=True,
                       env=dict(env, PATH=str(empty)), timeout=60)
    assert r.returncode == 0 and r.stdout == ""


def test_no_code_guard_in_plugin():
    """F1: the safety hook code_guard is not part of the free plugin."""
    names = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*")
             if not {".git", "__pycache__", ".pytest_cache"} & set(p.parts) and p.is_file()]
    assert not [n for n in names if "code_guard" in n.lower()]
    own = Path(__file__).resolve()
    needle = "code" + "_guard"
    for n in names:
        p = ROOT / n
        if p == own or p.suffix in {".png", ".gif"}:
            continue
        assert needle not in p.read_text(encoding="utf-8", errors="ignore").lower(), n
    hooks = (ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8")
    assert "PreToolUse" not in hooks


def test_readme_install_section():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Install as a plugin" in readme
    assert "/plugin marketplace add AntonioBlago/claude-code-seo-starter" in readme
    assert "/plugin install homebase@antonioblago" in readme
    assert "Marketplaces" in readme and "auto-update" in readme.lower()
