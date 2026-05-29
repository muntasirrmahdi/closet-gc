#!/usr/bin/env python3
"""
closetgc — Dead code detection for your wardrobe.
Find clothes you own but never wear. Like a linter for your closet.
"""

import argparse
import sqlite3
import os
import sys
import json
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path.home() / ".closetgc.db"


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'other',
            color TEXT,
            added_date TEXT NOT NULL,
            last_worn TEXT,
            wear_count INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS wear_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            worn_date TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.row_factory = sqlite3.Row
    return conn


CATEGORIES = ["tops", "bottoms", "outerwear", "shoes", "accessories", "formal", "other"]
COLORS = ["black", "white", "blue", "red", "green", "grey", "brown", "navy", "beige", "pink", "yellow", "orange", "purple", "other"]
DEAD_DAYS = 90


def cmd_add(conn, name, category, color):
    conn.execute(
        "INSERT INTO items (name, category, color, added_date) VALUES (?, ?, ?, ?)",
        (name.strip().lower(), category, color, date.today().isoformat())
    )
    conn.commit()
    print(f"Added: {name} ({category}, {color})")


def cmd_wear(conn, name_or_id):
    item = find_item(conn, name_or_id)
    if not item:
        print(f"Item not found: {name_or_id}")
        sys.exit(1)
    today = date.today().isoformat()
    conn.execute("UPDATE items SET last_worn = ?, wear_count = wear_count + 1 WHERE id = ?", (today, item["id"]))
    conn.execute("INSERT INTO wear_log (item_id, worn_date) VALUES (?, ?)", (item["id"], today))
    conn.commit()
    print(f"Worn: {item['name']} (wear #{item['wear_count'] + 1})")


def cmd_dead(conn, days=DEAD_DAYS):
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    dead = conn.execute("""
        SELECT * FROM items
        WHERE last_worn IS NULL OR last_worn < ?
        ORDER BY wear_count ASC, last_worn ASC
    """, (cutoff,)).fetchall()

    if not dead:
        print(f"No dead items found. Everything worn in the last {days} days.")
        return

    print(f"\nDead Code ({days}+ days unworn):")
    print("=" * 60)
    total = len(dead)
    for item in dead:
        last = item["last_worn"] or "never"
        count = item["wear_count"]
        marker = " NEVER WORN" if count == 0 else f" {count} wears"
        print(f"  [{item['category']:12s}] {item['name']:25s} | last: {last:10s} |{marker}")
    print("=" * 60)
    print(f"\n{total} dead items. {total} out of {count_total(conn)} total ({pct(total, count_total(conn))}%).")
    if total > 0:
        print("Run 'closetgc purge' to get donation suggestions.")


def cmd_stats(conn):
    total = count_total(conn)
    worn_30 = conn.execute(
        "SELECT COUNT(*) FROM items WHERE last_worn >= ?",
        ((date.today() - timedelta(days=30)).isoformat(),)
    ).fetchone()[0]
    never_worn = conn.execute("SELECT COUNT(*) FROM items WHERE wear_count = 0").fetchone()[0]
    most_worn = conn.execute("SELECT name, wear_count FROM items ORDER BY wear_count DESC LIMIT 5").fetchall()

    print(f"\nWardrobe Stats")
    print("=" * 40)
    print(f"  Total items:      {total}")
    print(f"  Worn in 30 days:  {worn_30} ({pct(worn_30, total)}%)")
    print(f"  Never worn:       {never_worn} ({pct(never_worn, total)}%)")

    by_cat = conn.execute("SELECT category, COUNT(*) as c FROM items GROUP BY category ORDER BY c DESC").fetchall()
    print(f"\n  By category:")
    for row in by_cat:
        dead_in_cat = conn.execute(
            "SELECT COUNT(*) FROM items WHERE category = ? AND (last_worn IS NULL OR last_worn < ?)",
            (row["category"], (date.today() - timedelta(days=DEAD_DAYS)).isoformat())
        ).fetchone()[0]
        print(f"    {row['category']:12s}: {row['c']:3d}  (dead: {dead_in_cat})")

    print(f"\n  Most worn:")
    for item in most_worn:
        print(f"    {item['name']:30s} {item['wear_count']}x")

    total_wears = conn.execute("SELECT SUM(wear_count) FROM items").fetchone()[0] or 0
    days_tracked = (date.today() - date.fromisoformat(
        conn.execute("SELECT MIN(added_date) FROM items").fetchone()[0] or date.today().isoformat()
    )).days or 1
    print(f"\n  Total wears: {total_wears} (avg {total_wears/max(days_tracked,1):.1f}/day)")


def cmd_list(conn, category=None):
    query = "SELECT * FROM items"
    params = ()
    if category:
        query += " WHERE category = ?"
        params = (category,)
    query += " ORDER BY wear_count DESC"
    items = conn.execute(query, params).fetchall()

    print(f"\nWardrobe ({len(items)} items):")
    print("=" * 60)
    for item in items:
        last = item["last_worn"] or "never"
        wc = item["wear_count"]
        status = "alive" if item["last_worn"] and item["last_worn"] >= (date.today() - timedelta(days=DEAD_DAYS)).isoformat() else "DEAD"
        print(f"  [{item['category']:12s}] {item['name']:25s} | {item['color'] or '--':8s} | {wc:2d}x | {last:10s} | {status}")


def cmd_purge(conn):
    cutoff = (date.today() - timedelta(days=DEAD_DAYS)).isoformat()
    dead = conn.execute(
        "SELECT * FROM items WHERE last_worn IS NULL OR last_worn < ? ORDER BY wear_count ASC",
        (cutoff,)
    ).fetchall()

    if not dead:
        print("No dead items to purge.")
        return

    print(f"\nDonation Candidates:")
    print("=" * 50)
    for i, item in enumerate(dead):
        print(f"  [{i+1}] {item['name']} ({item['category']}) - {item['wear_count']} wears, last: {item['last_worn'] or 'never'}")
    print(f"\n  Purge all {len(dead)}? Type 'yes' to confirm: ", end="")
    sys.stdout.flush()
    answer = sys.stdin.readline().strip()
    if answer.lower() == "yes":
        conn.execute("DELETE FROM items WHERE last_worn IS NULL OR last_worn < ?", (cutoff,))
        conn.commit()
        print(f"  Purged {len(dead)} items. Closet trimmed.")
    else:
        print("  Cancelled.")


def cmd_remove(conn, name_or_id):
    item = find_item(conn, name_or_id)
    if not item:
        print(f"Item not found: {name_or_id}")
        sys.exit(1)
    conn.execute("DELETE FROM wear_log WHERE item_id = ?", (item["id"],))
    conn.execute("DELETE FROM items WHERE id = ?", (item["id"],))
    conn.commit()
    print(f"Removed: {item['name']}")


def cmd_undo(conn):
    last = conn.execute("SELECT * FROM wear_log ORDER BY id DESC LIMIT 1").fetchone()
    if not last:
        print("Nothing to undo.")
        return
    conn.execute("DELETE FROM wear_log WHERE id = ?", (last["id"],))
    item = conn.execute("SELECT * FROM items WHERE id = ?", (last["item_id"],)).fetchone()
    conn.execute("UPDATE items SET wear_count = MAX(wear_count - 1, 0) WHERE id = ?", (last["item_id"],))
    prev = conn.execute("SELECT * FROM wear_log WHERE item_id = ? ORDER BY id DESC LIMIT 1", (last["item_id"],)).fetchone()
    if prev:
        conn.execute("UPDATE items SET last_worn = ? WHERE id = ?", (prev["worn_date"], last["item_id"]))
    else:
        conn.execute("UPDATE items SET last_worn = NULL WHERE id = ?", (last["item_id"],))
    conn.commit()
    print(f"Undo: {item['name']} wear removed.")


def cmd_export(conn):
    items = conn.execute("SELECT * FROM items ORDER BY category, name").fetchall()
    data = [dict(row) for row in items]
    print(json.dumps(data, indent=2))


def find_item(conn, name_or_id):
    try:
        item_id = int(name_or_id)
        return conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    except ValueError:
        return conn.execute("SELECT * FROM items WHERE name = ?", (name_or_id.strip().lower(),)).fetchone()


def count_total(conn):
    return conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]


def pct(part, total):
    if total == 0:
        return 0
    return round(part / total * 100)


def main():
    parser = argparse.ArgumentParser(
        prog="closetgc",
        description="Dead code detection for your wardrobe. Find clothes you own but never wear."
    )
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Add a clothing item")
    p_add.add_argument("name", help="Item name (e.g. 'blue nike hoodie')")
    p_add.add_argument("--category", "-c", choices=CATEGORIES, default="other")
    p_add.add_argument("--color", choices=COLORS, default="other")

    p_wear = sub.add_parser("wear", help="Mark item as worn today")
    p_wear.add_argument("item", help="Item name or ID")

    sub.add_parser("dead", help=f"List items not worn in {DEAD_DAYS}+ days")
    sub.add_parser("stats", help="Show wardrobe statistics")
    sub.add_parser("purge", help="Remove dead items (interactive)")

    p_list = sub.add_parser("list", help="List all items")
    p_list.add_argument("--category", "-c", choices=CATEGORIES)

    p_remove = sub.add_parser("remove", help="Remove an item")
    p_remove.add_argument("item", help="Item name or ID")

    sub.add_parser("undo", help="Undo last wear")
    sub.add_parser("export", help="Export all data as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    conn = get_db()

    try:
        if args.command == "add":
            cmd_add(conn, args.name, args.category, args.color)
        elif args.command == "wear":
            cmd_wear(conn, args.item)
        elif args.command == "dead":
            cmd_dead(conn)
        elif args.command == "stats":
            cmd_stats(conn)
        elif args.command == "list":
            cmd_list(conn, args.category)
        elif args.command == "purge":
            cmd_purge(conn)
        elif args.command == "remove":
            cmd_remove(conn, args.item)
        elif args.command == "undo":
            cmd_undo(conn)
        elif args.command == "export":
            cmd_export(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
