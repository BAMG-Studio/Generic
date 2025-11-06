"""Generate a sample ForgeTrace audit in ./sample_audit.""""""Generate a sample ForgeTrace audit in ./sample_audit.""""""Generate a sample ForgeTrace audit in ./sample_audit."""

from __future__ import annotations

from __future__ import annotationsfrom __future__ import annotations

import shutil

import tempfile

from pathlib import Path

from textwrap import dedentimport shutilimport shutil



import yamlimport tempfileimport tempfile

from git import Repo

from pathlib import Pathfrom pathlib import Path

from forgetrace.audit import AuditEngine

from textwrap import dedent



APP_PY = dedent(import yaml

    """

    """Demo application that exercises dependencies."""from git import Repoimport yaml



    import requestsfrom git import Repo



from forgetrace.audit import AuditEngine

    def fetch(url: str) -> str:

        response = requests.get(url, timeout=5)from forgetrace.audit import AuditEngine

        response.raise_for_status()

        return response.text[:80]APP_PY = """""Demo application that exercises dependencies."""





    if __name__ == "__main__":

        print(fetch("https://example.com"))import requestsdef main() -> None:

    """

).strip() + "\n"    base_dir = Path(tempfile.mkdtemp(prefix="forgetrace_sample_"))



README_MD = """# Sample Repo    repo_dir = base_dir / "sample_repo"



Generated for ForgeTrace executive summary smoke test.def fetch(url: str) -> str:    repo_dir.mkdir()

"""

    response = requests.get(url, timeout=5)



def main() -> None:    response.raise_for_status()    repo = Repo.init(repo_dir)

    base_dir = Path(tempfile.mkdtemp(prefix="forgetrace_sample_"))

    repo_dir = base_dir / "sample_repo"    return response.text[:80]    with repo.config_writer() as cfg:

    repo_dir.mkdir()

        cfg.set_value("user", "name", "Sample User")

    repo = Repo.init(repo_dir)

    with repo.config_writer() as cfg:        cfg.set_value("user", "email", "sample@example.com")

        cfg.set_value("user", "name", "Sample User")

        cfg.set_value("user", "email", "sample@example.com")if __name__ == "__main__":



    (repo_dir / "README.md").write_text(README_MD)    print(fetch("https://example.com"))    (repo_dir / "README.md").write_text("""# Sample Repo

    (repo_dir / "app.py").write_text(APP_PY)

    (repo_dir / "requirements.txt").write_text("requests==2.28.0\npyyaml>=6.0\n")"""



    repo.index.add(["README.md", "app.py", "requirements.txt"])Generated for ForgeTrace executive summary smoke test.

    repo.index.commit("Initial commit")

README_MD = """# Sample Repo""")

    config = yaml.safe_load(Path("config.yaml").read_text())

    config.setdefault("output", {})["include_pdf"] = Truedef fetch(url: str) -> str:\n    response = requests.get(url, timeout=5)\n    response.raise_for_status()\n    return response.text[:80]\n\n\nif __name__ == "__main__":\n    print(fetch("https://example.com"))\n"""



    out_dir = Path("sample_audit")Generated for ForgeTrace executive summary smoke test.    (repo_dir / "app.py").write_text(

    if out_dir.exists():

        shutil.rmtree(out_dir)"""        dedent(



    try:            """

        AuditEngine(str(repo_dir), str(out_dir), config).run()

        print(f"✓ Sample audit generated at {out_dir}/")            """Demo application that exercises dependencies."""

    finally:

        shutil.rmtree(base_dir, ignore_errors=True)def main() -> None:



    base_dir = Path(tempfile.mkdtemp(prefix="forgetrace_sample_"))            import requests

if __name__ == "__main__":

    main()    repo_dir = base_dir / "sample_repo"


    repo_dir.mkdir()

            def fetch(url: str) -> str:

    repo = Repo.init(repo_dir)                response = requests.get(url, timeout=5)

    with repo.config_writer() as cfg:                response.raise_for_status()

        cfg.set_value("user", "name", "Sample User")                return response.text[:80]

        cfg.set_value("user", "email", "sample@example.com")



    (repo_dir / "README.md").write_text(README_MD)            if __name__ == "__main__":

    (repo_dir / "app.py").write_text(APP_PY)                print(fetch("https://example.com"))

    (repo_dir / "requirements.txt").write_text("requests==2.28.0\npyyaml>=6.0\n")            """

        ).strip()

    repo.index.add(["README.md", "app.py", "requirements.txt"])        + "\n"

    repo.index.commit("Initial commit")    )

    (repo_dir / "requirements.txt").write_text("requests==2.28.0\npyyaml>=6.0\n")

    config = yaml.safe_load(Path("config.yaml").read_text())

    config.setdefault("output", {})["include_pdf"] = True    repo.index.add(["README.md", "app.py", "requirements.txt"])

    repo.index.commit("Initial commit")

    out_dir = Path("sample_audit")

    if out_dir.exists():    config = yaml.safe_load(Path("config.yaml").read_text())

        shutil.rmtree(out_dir)    config.setdefault("output", {})["include_pdf"] = True



    try:    out_dir = Path("sample_audit")

        AuditEngine(str(repo_dir), str(out_dir), config).run()    if out_dir.exists():

        print(f"✓ Sample audit generated at {out_dir}/")        shutil.rmtree(out_dir)

    finally:

        shutil.rmtree(base_dir, ignore_errors=True)    try:

        AuditEngine(str(repo_dir), str(out_dir), config).run()

        print(f"✓ Sample audit generated at {out_dir}/")

if __name__ == "__main__":    finally:

    main()        shutil.rmtree(base_dir, ignore_errors=True)



if __name__ == "__main__":
    main()
