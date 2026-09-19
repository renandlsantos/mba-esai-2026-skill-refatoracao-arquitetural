"""Run isolated test suites, verify every legacy route, and smoke real loopback servers."""

import hashlib, json, os, re, socket, subprocess, tempfile, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
BASE = json.loads((REPORTS / "baseline-validation.json").read_text())


def run(command, cwd, env=None):
    started = time.monotonic()
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    return {
        "command": command,
        "exitCode": result.returncode,
        "durationSeconds": round(time.monotonic() - started, 3),
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def normalized(rule):
    return re.sub(r"<[^>]+>|:[A-Za-z_]+", "{id}", rule)


def matches(route, call):
    expression = re.escape(normalized(route["rule"])).replace(
        re.escape("{id}"), r"[0-9]+"
    )
    return (
        route["method"] == call["method"]
        and re.fullmatch(expression, call["path"].split("?")[0]) is not None
    )


def smoke(name, command, cwd, path, extra_env):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    with tempfile.TemporaryDirectory() as temp:
        env = {
            **os.environ,
            **extra_env,
            "PORT": str(port),
            "FLASK_SKIP_DOTENV": "1",
            "DATABASE_PATH": str(Path(temp) / "shop.db"),
            "DATABASE_URL": "sqlite:///" + str(Path(temp) / "tasks.db"),
        }
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        status = None
        try:
            for _ in range(100):
                if process.poll() is not None:
                    break
                try:
                    with urllib.request.urlopen(
                        f"http://127.0.0.1:{port}{path}", timeout=1
                    ) as response:
                        status = response.status
                        break
                except urllib.error.HTTPError as error:
                    status = error.code
                    break
                except (urllib.error.URLError, TimeoutError):
                    time.sleep(0.1)
            if status not in (200, 403):
                raise RuntimeError(f"{name} boot failed: status={status}")
        finally:
            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
        if "dotenv" in (stdout + stderr).lower():
            raise RuntimeError("Implicit dotenv loading detected in smoke output")
        return {
            "project": name,
            "boundHost": "127.0.0.1",
            "endpoint": path,
            "status": status,
            "stdout": stdout,
            "stderr": stderr,
            "processStopped": process.poll() is not None,
        }


def main():
    os.chdir(ROOT)
    REPORTS.mkdir(exist_ok=True)
    suite = []
    coverage = []
    for name, project, python in [
        ("shop", "code-smells-project", ".work/venv-shop/bin/python"),
        ("tasks", "task-manager-api", ".work/venv-tasks/bin/python"),
        ("lms", "ecommerce-api-legacy", None),
    ]:
        output = ROOT / ".work" / f"covered-{name}.json"
        env = {**os.environ, "COVERAGE_OUTPUT": str(output)}
        cmd = (
            [
                str(ROOT / python),
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-p",
                f"test_{name}.py",
                "-v",
            ]
            if python
            else ["node", "--test", "test/api.test.js"]
        )
        result = run(cmd, ROOT if python else ROOT / project, env)
        suite.append({"project": name, **result})
        (REPORTS / f"tests-{name}.txt").write_text(result["stdout"] + result["stderr"])
        if result["exitCode"]:
            raise RuntimeError(f"{name} tests failed; see reports/tests-{name}.txt")
        calls = json.loads(output.read_text())
        baseline = next(i for i in BASE["projects"] if i["project"] == name)
        absent = [
            route
            for route in baseline["routes"]
            if not any(matches(route, call) for call in calls)
        ]
        if absent:
            raise RuntimeError(f"Unexercised {name} routes: {absent}")
        if python:
            inv = run([str(ROOT / python), "scripts/flask_inventory.py", project], ROOT)
            if inv["exitCode"]:
                raise RuntimeError(inv["stderr"])
            current = json.loads(inv["stdout"])
        else:
            code = "require('./src/app').createApp().then(async b=>{console.log(JSON.stringify(b.app._router.stack.filter(x=>x.name==='router').flatMap(x=>x.handle.stack.filter(y=>y.route).flatMap(y=>Object.keys(y.route.methods).map(m=>({method:m.toUpperCase(),rule:y.route.path}))))));await b.repository.close();})"
            inv = run(["node", "-e", code], ROOT / project)
            if inv["exitCode"]:
                raise RuntimeError(inv["stderr"])
            current = json.loads(inv["stdout"])
        before = {(x["method"], normalized(x["rule"])) for x in baseline["routes"]}
        after = {(x["method"], normalized(x["rule"])) for x in current}
        if before != after:
            raise RuntimeError(f"Changed route inventory {name}: {before ^ after}")
        coverage.append(
            {
                "project": name,
                "originalRoutes": len(before),
                "currentRoutes": len(after),
                "coveredRoutes": len(before),
                "calls": calls,
            }
        )
    smoke_results = [
        smoke(
            "shop",
            [str(ROOT / ".work/venv-shop/bin/python"), "app.py"],
            ROOT / "code-smells-project",
            "/health",
            {},
        ),
        smoke(
            "tasks",
            [str(ROOT / ".work/venv-tasks/bin/python"), "app.py"],
            ROOT / "task-manager-api",
            "/health",
            {},
        ),
        smoke(
            "lms",
            ["node", "src/app.js"],
            ROOT / "ecommerce-api-legacy",
            "/api/admin/financial-report",
            {},
        ),
    ]
    master = ROOT / "code-smells-project/.agents/skills/refactor-arch"
    hashes = {
        str(f.relative_to(master)): hashlib.sha256(f.read_bytes()).hexdigest()
        for f in master.rglob("*")
        if f.is_file()
    }
    for project in ["ecommerce-api-legacy", "task-manager-api"]:
        copy = ROOT / project / ".agents/skills/refactor-arch"
        assert {
            str(f.relative_to(copy)): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in copy.rglob("*")
            if f.is_file()
        } == hashes
    report = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tests": suite,
        "routeCoverage": coverage,
        "smoke": smoke_results,
        "skillCopiesIdentical": True,
        "skillFiles": hashes,
        "totalOriginalRoutes": sum(x["originalRoutes"] for x in coverage),
        "totalCoveredRoutes": sum(x["coveredRoutes"] for x in coverage),
    }
    (REPORTS / "after-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2).replace(str(ROOT), "$REPO")
        + "\n"
    )
    print(
        json.dumps(
            {
                "testsPassed": len(suite),
                "routesCovered": report["totalCoveredRoutes"],
                "smokePassed": len(smoke_results),
                "skillCopiesIdentical": True,
            }
        )
    )


if __name__ == "__main__":
    main()
