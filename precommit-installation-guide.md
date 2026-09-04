## Setup

### Requirements

* Git
* Python
* pre-commit

### Install pre-commit

If pre-commit is not already installed:

```powershell
pip install pre-commit
```

Install the pre-commit hooks after cloning the repository:

```powershell
pre-commit install
```
> Note: This assumes the developer has internet access.
Run all hooks manually:

```powershell
pre-commit run --all-files
```

After installation, the hooks run automatically during normal commits:

```powershell
git add .
git commit -m "Your commit message"
```

```text
Git
  ↓
Python
  ↓
pre-commit
  ↓
pre-commit install
  ↓
pre-commit reads .pre-commit-config.yaml
  ↓
Gitleaks hook is prepared
  ↓
git commit
  ↓
Gitleaks runs
```

## Important Limitation

The pre-commit configuration is intended to prevent **new secrets from being introduced through normal commits**, it does not perform a scan of the repository for old commit.