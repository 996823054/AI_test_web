from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def tracked_markdown_files() -> list[Path]:
    result = subprocess.run(
        ("git", "ls-files", "--cached", "--others", "--exclude-standard", "*.md"),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        ROOT / path
        for path in result.stdout.splitlines()
        if path == "README.md" or path.startswith("docs/")
    ]


def main() -> int:
    broken: list[str] = []
    checked = 0

    for document in tracked_markdown_files():
        if not document.exists():
            continue
        for line_number, line in enumerate(
            document.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            for match in LINK_PATTERN.finditer(line):
                target = match.group(1).strip().split(maxsplit=1)[0].strip("<>")
                if (
                    not target
                    or target.startswith(("#", "http://", "https://", "mailto:"))
                ):
                    continue
                relative_path = unquote(target.split("#", 1)[0])
                if not relative_path:
                    continue
                checked += 1
                resolved = (document.parent / relative_path).resolve()
                if not resolved.exists():
                    broken.append(
                        f"{document.relative_to(ROOT)}:{line_number}: {target}"
                    )

    if broken:
        print("发现无效文档链接：")
        print("\n".join(broken))
        return 1

    print(f"文档链接检查通过：{checked} 个本地链接")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
