# Deployment

This guide explains how to deploy the trsproc documentation site to
[GitHub Pages](https://pages.github.com/).

## Prerequisites

- A GitHub repository with the trsproc source code
- Push access to the repository
- Python >= 3.8 with the documentation dependencies installed:

```bash
pip install -r docs/requirements.txt
```

## One-time setup

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings → Pages**
3. Under **Source**, select **Deploy from a branch**
4. Choose **gh-pages** branch and **/ (root)** folder
5. Click **Save**

### 2. Ensure the gh-pages branch exists

If the `gh-pages` branch does not exist yet, create it:

```bash
git checkout --orphan gh-pages
git rm -rf .
git commit --allow-empty -m "Create gh-pages branch"
git push origin gh-pages
git checkout main  # or dev
```

The branch will be populated automatically the first time you deploy.

---

## Manual deployment

From the project root directory:

```bash
mkdocs gh-deploy
```

This command:

1. Builds the documentation to a temporary directory
2. Commits the output to the `gh-pages` branch
3. Pushes the branch to GitHub

GitHub Pages will detect the push and publish the site within a few minutes.

!!! tip "Preview before deploying"

    Use `mkdocs serve` to preview locally before deploying:

    ```bash
    mkdocs serve
    ```

    Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## CI automatic deployment (recommended)

You can automate deployment using GitHub Actions so that the documentation is
rebuilt and published every time you push to the main branch.

### Create the workflow file

Create `.github/workflows/deploy-docs.yml`:

```yaml
name: Deploy documentation

on:
  push:
    branches: [main]
    paths:
      - "docs/**"
      - "src/**"
      - "mkdocs.yml"

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r docs/requirements.txt

      - name: Deploy to GitHub Pages
        run: mkdocs gh-deploy --force
```

### How it works

- The workflow triggers on pushes to `main` that modify documentation or source
  files.
- It installs the documentation dependencies, builds the site, and pushes to
  the `gh-pages` branch.
- The `--force` flag ensures the deploy succeeds even if there are conflicts
  on the `gh-pages` branch.

---

## Custom domain (optional)

To use a custom domain (e.g., `trsproc.elda.org`):

1. In **Settings → Pages → Custom domain**, enter your domain name.
2. Create a `CNAME` file in the `docs/` directory:

   ```
   trsproc.elda.org
   ```

3. Configure your DNS provider to add a `CNAME` record pointing to
   `ELDAELRA.github.io`.

4. Enable **Enforce HTTPS** in the GitHub Pages settings.

mkdocs will automatically include the `CNAME` file in the build output.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Site not updating | Check the **Actions** tab for deployment errors. It can take 1-2 minutes for GitHub Pages to reflect changes. |
| 404 on pages | Ensure `site_url` in `mkdocs.yml` is correct and matches the actual URL. |
| `gh-deploy` fails | Verify you have push access and that the `gh-pages` branch exists on the remote. |
| Broken cross-references | Run `mkdocs build` locally first to check for warnings. |
