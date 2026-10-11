# Copyright 2026 The Spyre-Inference Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Downloads and unzips a run's junit-* and run-id/artifact-id artifacts, one subdir each."""

import argparse
import json
import os
import subprocess
from pathlib import Path

ID_ARTIFACTS = {"run-id", "artifact-id"}


def wanted(artifact: dict) -> bool:
    return artifact["name"].startswith("junit-") or artifact["name"] in ID_ARTIFACTS


def download_and_extract(repo: str, artifact: dict, out_dir: Path) -> None:
    zip_path = out_dir / f"{artifact['name']}.zip"
    result = subprocess.run(
        ["gh", "api", f"/repos/{repo}/actions/artifacts/{artifact['id']}/zip"],
        stdout=subprocess.PIPE,
        check=True,
    )
    zip_path.write_bytes(result.stdout)
    subprocess.run(
        ["unzip", "-o", str(zip_path), "-d", str(out_dir / artifact["name"])], check=True
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifacts",
        default=os.environ.get("ARTIFACTS", "[]"),
        help='JSON array of {"id", "name"} objects (default: $ARTIFACTS)',
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY"),
        help="owner/repo the artifacts belong to (default: $GITHUB_REPOSITORY)",
    )
    parser.add_argument("--out-dir", default="xml_artifacts", type=Path)
    args = parser.parse_args()
    if not args.repo:
        parser.error("--repo is required when $GITHUB_REPOSITORY is unset")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for a in filter(wanted, json.loads(args.artifacts)):
        print(f"Downloading: {a['name']} (id={a['id']})")
        download_and_extract(args.repo, a, args.out_dir)


if __name__ == "__main__":
    main()
