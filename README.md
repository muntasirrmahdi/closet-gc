# Closet GC

[![GitHub stars](https://img.shields.io/github/stars/muntasirrmahdi/closet-gc?style=social)](https://github.com/muntasirrmahdi/closet-gc/stargazers)
[![GitHub license](https://img.shields.io/github/license/muntasirrmahdi/closet-gc)](https://github.com/muntasirrmahdi/closet-gc/blob/main/LICENSE)
[![HTML](https://img.shields.io/badge/Web-HTML%2FCSS%2FJS-E34F26.svg)](https://developer.mozilla.org/en-US/docs/Web)
[![Python](https://img.shields.io/badge/CLI-Python-3776AB.svg)](https://www.python.org/)

Dead code detection for your wardrobe. Find clothes you own but never wear. Like a linter, but for your closet.

Closet GC tracks every clothing item you own and how often you wear each one. If something goes unworn for 90 days, it gets flagged as dead code -- a clear signal that it might be time to donate or sell. The web version is a single HTML file that runs entirely in your browser. Data never leaves your device. No accounts, no cloud, no install.

Try it live: [closetgc.vercel.app](https://closetgc.vercel.app)

---

## The TL;DR

**Pros:**
* **Zero Install**: Open a single HTML file in any browser. That's it.
* **Offline-First**: localStorage keeps your data on your device. No cloud dependency.
* **Visual Feedback**: Donut chart shows dead-to-alive ratio at a glance.
* **CLI Option**: Python terminal version for developers who prefer the command line.
* **Export/Import**: Backup your data as JSON. Restore anytime.
* **Dark Mode**: Browser remembers your preference.

**Cons:**
* **Browser LocalStorage**: Clear your browser data, lose your wardrobe. Export regularly.
* **Single Device**: Data doesn't sync across browsers or devices automatically.
* **No Mobile App**: Web version works on mobile browsers but has no native app.

---

## Version History

| Version | Status  | Notes |
|---------|---------|-------|
| 1.4     | Current | Single-file web app with dark mode, demo data, search/sort |
| 1.0     | Previous | Initial CLI-only release with sqlite3 backend |

**Current Version**: 1.4 (stable)

---

## Quick Start

### Web Version (Recommended)

1. Clone or download this repo.
2. Open `src/index.html` in any browser.
3. Click **Load Demo** to see how it works with sample data.
4. Click **Add Item** to start adding your own clothes.
5. Click **Wear** to log daily use on any item.

That's the entire setup. No build step, no `npm install`.

### CLI Version

```bash
# Add items
python3 src/closetgc.py add "Blue Hoodie" --category tops --color blue
python3 src/closetgc.py add "Black Jeans" --category bottoms --color black

# Log daily wear
python3 src/closetgc.py wear "Blue Hoodie"

# Check your stats
python3 src/closetgc.py stats

# Find dead code (90+ days unworn)
python3 src/closetgc.py dead
```

Global install (optional):
```bash
chmod +x src/closetgc.py
sudo cp src/closetgc.py /usr/local/bin/closetgc
```

---

## Available Commands (CLI)

### Item Management
```bash
closetgc add <name> --category <cat> --color <color>    # Add a clothing item
closetgc wear <name-or-id>                              # Mark item as worn today
closetgc remove <name-or-id>                            # Remove an item
```

### Analysis
```bash
closetgc dead                                           # List items not worn in 90+ days
closetgc stats                                          # Show wardrobe statistics
closetgc list                                           # List all items
closetgc list --category tops                           # Filter by category
```

### Data
```bash
closetgc export                                         # Export all data as JSON
closetgc undo                                           # Undo last wear action
closetgc purge                                          # Interactively remove dead items
```

### Categories
`tops | bottoms | outerwear | shoes | accessories | formal | other`

### Colors
`black | white | blue | red | green | grey | brown | navy | beige | pink | yellow | orange | purple | other`

---

## Project Structure

```
closet-gc/
  src/
    index.html          Web app (1927 lines, single file, zero dependencies)
    closetgc.py         Python CLI (287 lines, stdlib only)
  tests/                Test files
  docs/                 Documentation
  README.md
  LICENSE
  CONTRIBUTING.md
```

---

## Tech

| Component | Stack | Why |
|-----------|-------|-----|
| Web App | HTML, CSS, JavaScript (vanilla) | Zero-dependency, works offline, opens in any browser |
| CLI Tool | Python 3, sqlite3, argparse | Stdlib only, no pip install needed |
| Charts | SVG donut chart (CSS-animated) | No chart library, renders natively |
| Storage | localStorage (web), SQLite (CLI) | No backend, no database server |
| Deployment | Vercel (static hosting) | Free tier, instant deploys |

---

## Known Limitations

1. **LocalStorage is Volatile**: If a user clears browser data, wardrobe is lost. Export backups are the only safety net.
2. **No Cross-Device Sync**: Web and CLI versions store data independently. No sync between them.
3. **Minimal Error Handling**: The CLI uses basic input validation. Edge cases like corrupt SQLite databases may crash.
4. **Desktop-Centric Design**: The web UI is optimized for desktop. Mobile works but with reduced layout.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Bug reports and feature requests are welcome via the issue templates.

---

## License

MIT. See [LICENSE](LICENSE).
