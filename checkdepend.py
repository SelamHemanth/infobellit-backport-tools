#!/usr/bin/env python3
"""
checkdepend.py

For each user-provided commit (from user repo) this script:
 1) records .stable_log (git log from stable repo) and .user_log (git log --oneline from user repo)
 2) for each user commit, queries stable repo for commits that mention the user commit's short7
 3) filters out commented occurrences (lines where '#' appears before short7)
 4) ignores self-matches (stable commit == user commit)
 5) writes dependencies as "<14char-hash> <subject>" into .dep_log
 6) checks whether dependency subject is present in user repo one-line log and prints PASS/FAIL
"""
import subprocess
import re
from typing import List, Tuple

# ---------- utils ----------
def run_cmd(cmd: str, cwd: str = None) -> str:
    """Run shell command and return stdout as latin-1 string (safe for kernel logs)."""
    result = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True)
    return result.stdout.decode("latin-1", errors="replace")

def write_file(path: str, content: str):
    with open(path, "w", encoding="latin-1", errors="replace") as f:
        f.write(content)

def append_file(path: str, content: str):
    with open(path, "a", encoding="latin-1", errors="replace") as f:
        f.write(content)

def file_read(path: str) -> str:
    with open(path, "r", encoding="latin-1", errors="replace") as f:
        return f.read()

# ---------- git helpers ----------
def git_show_full_commit(user_repo: str, commitish: str) -> Tuple[str, str]:
    """
    Return (full_hash, subject) for a commit-ish in user_repo.
    If lookup fails, return (None, None).
    """
    out = run_cmd(f'git show --pretty=format:"%H%n%s" --no-patch {commitish}', cwd=user_repo)
    if not out:
        return (None, None)
    parts = out.splitlines()
    if len(parts) >= 2:
        return (parts[0].strip(), parts[1].strip())
    elif len(parts) == 1:
        return (parts[0].strip(), "")
    return (None, None)

def git_find_stable_commits_mentioning(short7: str, stable_repo: str) -> List[Tuple[str,str,str]]:
    """
    Returns a list of tuples for stable commits that mention short7:
      [(stable_full_hash, subject, body), ...]
    Uses `git log --all --grep=short7 -i` to get candidate commits, then parses them.
    """
    # Use an unambiguous separator so we can split results safely.
    fmt = '%H%x01%s%x01%b%x02'
    cmd = f"git log --all --grep={short7} -i --pretty=format:'{fmt}'"
    out = run_cmd(cmd, cwd=stable_repo)
    if not out:
        return []

    entries = out.split('\x02')
    results = []
    for e in entries:
        if not e.strip():
            continue
        parts = e.split('\x01')
        if len(parts) < 3:
            continue
        full_hash = parts[0].strip()
        subject = parts[1].strip()
        body = parts[2]
        results.append((full_hash, subject, body))
    return results

# ---------- matching helpers ----------
def short7_in_text_non_commented(short7: str, text: str) -> bool:
    """
    Return True if short7 occurs in text on a line where it is not preceded by '#'
    (i.e., not commented out).
    """
    for line in text.splitlines():
        if short7 in line:
            pos = line.find(short7)
            # if there's a '#' BEFORE pos on the same line, treat as commented-out
            if '#' in line[:pos]:
                continue
            return True
    return False

# ---------- main logic ----------
def main():
    user_repo = input("\033[1mEnter path to your kernel source:\033[0m ").strip()
    stable_repo = input("\033[1mEnter path to Torvalds kernel source:\033[0m ").strip()

    print("\033[1mEnter commits (one per line). Type 'done' when finished:\033[0m")
    commits = []
    while True:
        ln = input().strip()
        if ln.lower() == "done":
            break
        if ln:
            commits.append(ln)

    # output files
    stable_log_path = ".stable_log"
    user_log_path = ".user_log"
    full_commits_path = ".full_commits"
    dep_log_path = ".dep_log"

    print("\n\033[1mGenerating logs\033[0m\033[5m...\033[0m")

    # 1) save stable repo full git log (for reference)
    stable_log = run_cmd("git log", cwd=stable_repo)
    write_file(stable_log_path, stable_log)

    # 2) save user repo one-line log
    user_log = run_cmd("git log --oneline", cwd=user_repo)
    write_file(user_log_path, user_log)
    user_log_txt = user_log  # Keep in memory for checking

    # 3) resolve each provided commit in user repo to full hash+subject
    write_file(full_commits_path, "")
    resolved = []
    for c in commits:
        full_hash, subject = git_show_full_commit(user_repo, c)
        if not full_hash:
            print(f"Warning: couldn't resolve commit '{c}' in user repo. Skipping.")
            continue
        append_file(full_commits_path, f"{full_hash} {subject}\n")
        resolved.append((full_hash, subject))

    # clear dep log
    write_file(dep_log_path, "")

    print("\n\033[1mChecking dependencies\033[0m\033[5m...\033[0m\n")

    for full_hash, subject in resolved:
        short7 = full_hash[:7]
        short14 = full_hash[:14]
        print(f"\033[34mCommit:\033[0m {short14} - {subject}")

        # Query stable repo for commits that mention short7
        candidates = git_find_stable_commits_mentioning(short7, stable_repo)

        deps_found = []
        for st_full, st_subject, st_body in candidates:
            # ignore exact self-match (same commit)
            if st_full.lower() == full_hash.lower():
                continue

            # Check that the occurrence is not commented out:
            combined_text = st_subject + "\n" + st_body
            if not short7_in_text_non_commented(short7, combined_text):
                continue

            deps_found.append((st_full, st_subject))

        # deduplicate by full hash
        unique = []
        seen = set()
        for h, s in deps_found:
            if h not in seen:
                seen.add(h)
                unique.append((h, s))

        if not unique:
            print("  \033[32mPASS\033[0m -> No dependencies found\n")
            continue

        # Check each dependency and track if all are fixed
        all_fixed = True
        dep_status = []
        for st_full, st_subject in unique:
            dep14 = st_full[:14]
            dep_entry = f"{dep14} {st_subject}"
            append_file(dep_log_path, dep_entry + "\n")
            
            # Check if this dependency is already fixed in user repo
            is_fixed = bool(re.search(re.escape(st_subject), user_log_txt))
            dep_status.append((dep_entry, is_fixed))
            if not is_fixed:
                all_fixed = False
        
        # Print result based on whether all dependencies are fixed
        if all_fixed:
            print("  \033[32mPASS\033[0m -> No dependencies found\n")
        else:
            print("  \033[31mFAIL\033[0m -> new bugfix needed")
            for dep_entry, is_fixed in dep_status:
                if is_fixed:
                    print(f"    \033[35m*\033[0m \033[1;33m{dep_entry}\033[0m \033[32m-> Fixed\033[0m")
                else:
                    print(f"    \033[35m*\033[0m \033[1,33m{dep_entry}\033[0m")
            print()

    print("\033[1,32mDone.\033[0m\n")


if __name__ == "__main__":
    main()
