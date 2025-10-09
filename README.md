# Backport Contribution Tool

## 📘 About

The **backport_contribution** is a command-line tool that analyzes commits across multiple Git branches to determine contributor activity based on `Signed-off-by` tags. It generates a structured and formatted Excel report showing how many commits each contributor has signed off in different branches.

---

## 🚀 Features

- ✅ Checks **Signed-off-by** lines in commit messages across specified branches.  
- ✅ Supports **multiple contributor email IDs** at once.  
- ✅ Handles **date ranges** using `--since` and `--until` filters.  
- ✅ Ensures that **each commit counts for only the first matching Signed-off-by email** (to avoid double-counting).  
- ✅ Exports a **formatted Excel report** with branch-level and total commit counts.  
- ✅ Works safely with **non-UTF-8 commit messages** (no decode errors).  
- ✅ Auto-validates email and branch existence.  

---

## 🧩 Clone this repository (if applicable):
```bash
git clone https://github.com/SelamHemanth/infobellit-backport-tools.git
cd backport_contribution
git checkout backport_contribution
```

## 🔧 Install:
```bash
./installer
```
## ⚙️ How to Use

1. **Open a terminal** inside your Git repository.

2. **Run the tool** (after installing via your provided installer):
    ```bash
    backport_contribution
    ```
3. Follow the prompts:

    * Enter contributor email addresses
    (comma, space, or line-separated — type done when finished)

    * Optionally specify a date range:
    Start date (YYYY-MM-DD):
    End date (YYYY-MM-DD or 'now'):
    
    * Provide one or more branch names:
    origin/main
    origin/feature_update
    done
    
    * Confirm to start analysis:
    Proceed with analysis? (y/n): y

4. After completion, an Excel report will be saved in the same directory:
    backport_contribution_<timestamp>.xlsx

## 📊 Example Output

```bash
============================================================
Git Backport Contribution Checker
============================================================

Paste all email IDs (one per line or space-separated).
Type 'done' on a new line when finished:

dev.alpha@example.com
dev.beta@example.com
done

✓ Total emails added: 2

Enter date range for commit search (optional - press Enter to skip):
Start date (YYYY-MM-DD): 2025-01-01
End date (YYYY-MM-DD or 'now'): now
  ✓ Date range: 2025-01-01 to now

Paste all branch names (one per line or space-separated).
Type 'done' on a new line when finished:

origin/stable_release
origin/dev_branch
done

✓ Total branches added: 2

============================================================
Summary:
  Emails: 2
  Branches: 2
  Date range: 2025-01-01 to now
Proceed with analysis? (y/n): y

============================================================
Processing commits...
============================================================

Analyzing branch: origin/stable_release...
Analyzing branch: origin/dev_branch...

============================================================
Analysis Complete!
============================================================

✓ Report saved to: backport_contribution_20251009_164722.xlsx

Summary:
          Mail ID         origin/stable_release  origin/dev_branch  Total commits
  dev.alpha@example.com                        12                  8              20
  dev.beta@example.com                          3                  5               8
```

The resulting Excel file includes:

- Contributor emails as columns
- Branch names as rows
- Total commits at the bottom
- Professional formatting (colored headers, borders, auto-sized columns)

## 💡 Tip:
For large repositories, the tool may take a few seconds to analyze all commits per branch.
You can safely cancel anytime with `Ctrl + C`.

Version: 1.1
License: MIT
Maintainer: SelamHemanth
