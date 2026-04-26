from __future__ import annotations

from typing import Any

from _common import ROOT, fetch_json, iso_now, load_yaml, raw_output_path, write_json


def latest_commit_info(commits: list[dict[str, Any]]) -> tuple[str, list[dict[str, str]]]:
    if not commits:
        return "", []

    normalized: list[dict[str, str]] = []
    for item in commits:
        commit = item.get("commit", {})
        author = commit.get("author", {})
        message = (commit.get("message") or "").splitlines()[0]
        normalized.append(
            {
                "sha": (item.get("sha") or "")[:12],
                "date": author.get("date", ""),
                "message": message,
                "url": item.get("html_url", ""),
            }
        )

    return normalized[0].get("date", ""), normalized


def main() -> None:
    cfg = load_yaml(ROOT / "config" / "sources.yaml")
    src = cfg["github"]

    api_base = src["api_base"].rstrip("/")
    max_commits = int(src.get("max_commits_per_repo", 20))

    repos_out: list[dict[str, Any]] = []
    raw_repos: list[dict[str, Any]] = []

    for full_name in src["repos"]:
        repo_api = f"{api_base}/repos/{full_name}"
        commits_api = f"{repo_api}/commits?per_page={max_commits}"

        repo_meta = fetch_json(repo_api)
        commits = fetch_json(commits_api)

        latest_commit_date, recent_commits = latest_commit_info(commits)

        repos_out.append(
            {
                "repo": full_name,
                "html_url": repo_meta.get("html_url", ""),
                "updated_at": repo_meta.get("updated_at", ""),
                "pushed_at": repo_meta.get("pushed_at", ""),
                "default_branch": repo_meta.get("default_branch", "main"),
                "open_issues_count": repo_meta.get("open_issues_count", 0),
                "stargazers_count": repo_meta.get("stargazers_count", 0),
                "latest_commit_date": latest_commit_date,
                "recent_commits": recent_commits,
            }
        )

        raw_repos.append(
            {
                "repo": full_name,
                "repo_meta": repo_meta,
                "commits": commits,
            }
        )

    normalized = {
        "collected_at": iso_now(),
        "source": "github",
        "repos": repos_out,
        "stats": {
            "repos": len(repos_out),
            "total_commits_collected": sum(len(r["recent_commits"]) for r in repos_out),
        },
    }

    raw = {
        "collected_at": normalized["collected_at"],
        "source": "github",
        "repos": raw_repos,
    }

    write_json(raw_output_path("github"), raw)
    write_json(ROOT / "data" / "normalized" / "github.json", normalized)
    print(
        "github: repos="
        f"{len(repos_out)} commits={sum(len(r['recent_commits']) for r in repos_out)}"
    )


if __name__ == "__main__":
    main()
