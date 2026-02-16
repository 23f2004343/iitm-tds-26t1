# Q11: Configure a Codespace DevContainer

## Repository
**https://github.com/aloktripathi1/q-github-codespaces-devcontainer**

## DevContainer Configuration ✅

The `.devcontainer/devcontainer.json` file has been created with all required specifications:

```json
{
  "name": "ga2-f2ed3f",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {
    "ghcr.io/devcontainers/features/python:1": {}
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "astral-sh.uv",
        "ms-python.python"
      ]
    }
  },
  "postCreateCommand": "uv pip install fastapi"
}
```

### Configuration Details:
- ✅ **Name**: `ga2-f2ed3f`
- ✅ **Python Feature**: `ghcr.io/devcontainers/features/python:1`
- ✅ **VS Code Extensions**: `astral-sh.uv` and `ms-python.python`
- ✅ **Post Create Command**: `uv pip install fastapi`

## Setup Completed ✅

The repository has been initialized and pushed:
```bash
git init
git add .
git commit -m "Add devcontainer configuration for ga2-f2ed3f"
git remote add origin https://github.com/aloktripathi1/q-github-codespaces-devcontainer.git
git branch -M main
git push -u origin main
```

## Next Steps

1. **Launch a Codespace**:
   - Visit: https://github.com/aloktripathi1/q-github-codespaces-devcontainer
   - Click the green **"Code"** button
   - Select **"Codespaces"** tab
   - Click **"Create codespace on main"**

2. **Wait for initialization** (automatic installation of Python and FastAPI via `uv`)

3. **In the Codespace terminal, run**:
   ```bash
   echo $GITHUB_REPOSITORY $GITHUB_TOKEN
   ```

4. **Copy and submit** the output (repository slug and token)

## Notes
- `GITHUB_REPOSITORY` contains the repository slug (e.g., `username/repo`)
- `GITHUB_TOKEN` is an authenticated PAT valid for the Codespace session duration
- Both variables are automatically provided by GitHub Codespaces
- These values are **only available inside GitHub Codespaces**, not locally
