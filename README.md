# Check Dependency Tool

## Overview
`checkdepend.py` is a helper script designed to analyze commit dependencies between a user-provided kernel repository and the upstream Linux kernel (Torvalds' tree). It helps backport maintainers identify whether a commit in their local tree depends on other commits already present in the stable kernel.

## Features
- Records logs:
  - `.stable_log` → full `git log` from the stable repo
  - `.user_log` → one-line `git log` from the user repo
- Resolves each user-provided commit to its full hash and subject.
- Queries the stable repo for commits that mention the user commit’s short hash (7 chars).
- Filters out:
  - Commented occurrences (lines with `#` before the short hash).
  - Self-matches (same commit in both repos).
- Writes dependency entries into `.dep_log` as: <14char-hash> <subject>
- Checks whether each dependency subject is already present in the user repo.
- Prints **PASS/FAIL** results:
- **PASS** → no dependencies found or all dependencies already fixed.
- **FAIL** → missing dependency commits need to be backported.

## Usage
1. Run the script:
```bash
 ./checkdepend.py
```
2. Provide:
    Path to your kernel source (user repo).
    Path to Torvalds' kernel source (stable repo).
    List of commits (one per line).
    Type done when finished.

The script will generate .stable_log, .user_log, .full_commits, and .dep_log in the current directory.

## Example
```bash
$ ./checkdepend.py
Enter path to your kernel source: /home/user/my-kernel
Enter path to Torvalds kernel source: /home/user/linux-stable
Enter commits (one per line). Type 'done' when finished:
abc1234
def5678
done
```
### Output:
```bash
Commit: abc123456789ab - Fix memory leak in driver
  PASS -> No dependencies found

Commit: def56781234567 - Add new feature to subsystem
  FAIL -> new bugfix needed
    * 1234567890abcd Dependency commit subject
```

