# Closet GC

Dead code detection for your wardrobe. Find clothes you own but never wear. Like a linter for your closet.

## What It Does

Closet GC tracks what you own and how often you wear each item. After 90 days, unworn clothes get flagged as "dead code." You get a clear list of donation candidates -- the hoodie you haven't touched in 8 months, the shoes still in their box.

**Web version** (recommended): A single HTML file -- open it in any browser. Data stays on your device (localStorage).

**CLI version**: Python command-line tool for terminal users.

## Quick Start

**Web (recommended):**
1. Open `src/index.html` in any browser
2. Click "Add Item" to start tracking
3. Click "Wear" to log daily use
4. Check "Dead Code" for unworn items (90+ days)
5. Export/Import to back up your data

**CLI:**
```bash
python3 src/closetgc.py add "Blue Hoodie" --category tops --color blue
python3 src/closetgc.py wear "Blue Hoodie"
python3 src/closetgc.py stats
python3 src/closetgc.py dead
```

Or install globally:
```bash
chmod +x src/closetgc.py
sudo cp src/closetgc.py /usr/local/bin/closetgc
```

## Features

- **Add items** with name, category, color
- **Log daily wear** with one click
- **Dead code detection**: items not worn in 90+ days
- **Stats dashboard**: wear frequency, category breakdown
- **Donut chart**: visual dead-to-alive ratio
- **Dark mode**: toggle on/off, preference remembered
- **Search and sort**: filter by name, category, status
- **Export/Import**: backup and restore your data as JSON
- **Demo data**: see how it works before adding your own
- **Offline-first**: no server, no account, no internet needed

## Project Structure

```
closet-gc/
  src/
    index.html        Web app (single file, zero dependencies)
    closetgc.py       Python CLI version
  tests/              Test files
  docs/               Documentation
  README.md
  LICENSE
```

## Tech

- Web: vanilla HTML/CSS/JavaScript, zero dependencies, localStorage
- CLI: Python 3, sqlite3, argparse (stdlib only)
- Deployed at: https://closetgc.vercel.app

## License

MIT. See [LICENSE](LICENSE).
