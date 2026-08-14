# Deploying

## A single site

```bash
sphinx-vitepress build docs _site
```

Publish `_site/.vitepress/dist` with any static host. For GitHub project pages,
set the base path so asset URLs resolve:

```python
vitepress_base = "/my-repo/"
```

## Versioned documentation

```bash
sphinx-vitepress deploy docs \
    --deploy-dir _site \
    --release v1.2.3 \
    --repo-base /my-repo/
```

Each version is a **complete build of its own**, because `base` is baked into
every asset URL. The result:

```
_site/
├── stable/      # full site, base=/my-repo/stable/
├── v1/          # full site, base=/my-repo/v1/
├── dev/         # from an earlier --dev run
├── versions.js  # read by the navbar version picker
└── index.html   # redirects to stable/
```

`versions.js` and the root redirect are regenerated from whatever version
folders exist, so **older versions keep working without being rebuilt**. Copy
the previous tree into `--deploy-dir` before running, as the workflow below
does.

### Which folders a release updates

`--keep` decides how many aliases a tag maintains:

| `--keep` | `v1.2.3` updates |
| --- | --- |
| `breaking` (default) | `v1/`, `stable/` |
| `minor` | `v1.2/`, `v1/`, `stable/` |
| `patch` | `v1.2.3/`, `v1.2/`, `v1/`, `stable/` |

For a `0.x` release the minor is the breaking line, so `v0.3.2` updates `v0.3/`
and `stable/`.

Development builds use `--dev` and land in `dev/` (rename with `--devurl`).

## GitHub Actions

This workflow deploys `dev/` on every push to `main` and a versioned folder on
every tag:

```yaml
name: Docs
on:
  push:
    branches: [main]
    tags: ["v*"]
permissions:
  contents: write
concurrency:
  group: docs-deploy

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          python-version: "3.13"
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: uv sync

      # Keep previously deployed versions.
      - name: Load existing gh-pages tree
        run: |
          mkdir -p _site
          if git ls-remote --exit-code --heads origin gh-pages >/dev/null 2>&1; then
            git fetch origin gh-pages --depth=1
            git archive origin/gh-pages | tar -x -C _site
          fi

      - name: Build
        env:
          REPO_NAME: ${{ github.event.repository.name }}
        run: |
          if [[ "${GITHUB_REF}" == refs/tags/* ]]; then
            uv run sphinx-vitepress deploy docs --deploy-dir _site \
              --release "${GITHUB_REF_NAME}" --repo-base "/${REPO_NAME}/"
          else
            uv run sphinx-vitepress deploy docs --deploy-dir _site \
              --dev --repo-base "/${REPO_NAME}/"
          fi

      - uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: _site
```

Enable Pages for the repository with `gh-pages` as the source branch.

:::warning
Do not leave symlinks in the `gh-pages` branch. Delete them before deploying,
since they confuse the static-file server and the version picker.
:::

## Read the Docs

Read the Docs [supports VitePress projects](https://docs.readthedocs.com/platform/stable/intro/vitepress.html)
via a build command that ends with the site in `$READTHEDOCS_OUTPUT/html`.
