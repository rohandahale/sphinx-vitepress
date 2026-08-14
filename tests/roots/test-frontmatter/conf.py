project = "frontmatter"
extensions: list[str] = []
exclude_patterns = ["_build"]

vitepress_frontmatter = {
    "index": {
        "layout": "home",
        "hero": {"name": "Demo", "tagline": "Nested values & unicode: café ✨"},
        "features": [{"title": "One", "details": "First"}],
    }
}
