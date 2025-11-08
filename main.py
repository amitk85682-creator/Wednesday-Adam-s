#!/usr/bin/env python3
"""
main.py - Single-file Python CLI utility

Features:
- Text analysis: compute basic statistics for a text file or stdin
- Fetch summary: GET a URL and show headers and a safe preview of content
- Games:
  - plot-novel: quick collaborative fiction outline generator
  - name-poison-trivia: safe, historical trivia about poisonous plants (non-actionable)

Usage examples:
    python main.py stats --file story.txt
    echo "Some text" | python main.py stats
    python main.py fetch https://example.com
    python main.py plot-novel --tone "gothic" --protagonist "Evelyn"
    python main.py name-poison-trivia

This script uses only the Python standard library.
"""

from __future__ import annotations
import argparse
import sys
import logging
import textwrap
import random
import urllib.request
import urllib.error
import html
from typing import Tuple, Dict, List

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("singlefile-cli")


# -----------------------
# Text analysis utilities
# -----------------------
def analyze_text(text: str) -> Dict[str, float]:
    """
    Analyze text and return simple statistics.
    This is intentionally basic and safe (no external deps).

    Returns dict with:
      - chars: int
      - words: int
      - sentences: int (heuristic)
      - avg_word_length: float
      - reading_time_minutes: float (approx, 200 wpm)
    """
    if not text:
        return {"chars": 0, "words": 0, "sentences": 0, "avg_word_length": 0.0, "reading_time_minutes": 0.0}

    chars = len(text)
    words_list = [w for w in text.split() if w.strip()]
    words = len(words_list)
    # naive sentence split on .!? — good enough for a CLI tool
    sentences = max(1, sum(text.count(p) for p in ".!?"))
    avg_word_length = sum(len(w) for w in words_list) / words if words else 0.0
    reading_time_minutes = words / 200.0  # crude 200 wpm

    return {
        "chars": chars,
        "words": words,
        "sentences": sentences,
        "avg_word_length": round(avg_word_length, 2),
        "reading_time_minutes": round(reading_time_minutes, 2),
    }


def pretty_stats(stats: Dict[str, float]) -> str:
    return (
        f"Characters: {stats['chars']}\n"
        f"Words: {stats['words']}\n"
        f"Sentences (heuristic): {stats['sentences']}\n"
        f"Average word length: {stats['avg_word_length']}\n"
        f"Estimated reading time: {stats['reading_time_minutes']} minutes\n"
    )


# -----------------------
# Fetch URL utilities
# -----------------------
def fetch_url_summary(url: str, preview_chars: int = 800) -> Dict[str, str]:
    """
    Fetch the given URL and return a safe summary.
    The content preview is HTML-escaped and truncated to avoid accidental execution/display issues.
    """
    req = urllib.request.Request(url, headers={"User-Agent": "singlefile-cli/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            info = resp.info()
            content_type = info.get_content_type()
            content_length = resp.getheader("Content-Length") or ""
            raw = resp.read(preview_chars + 1)
            # decode best-effort
            try:
                text = raw.decode("utf-8", errors="replace")
            except Exception:
                text = raw.decode(errors="replace")
            preview = html.escape(text[:preview_chars])
            truncated = len(text) > preview_chars
            return {
                "url": url,
                "status": str(resp.status),
                "content_type": content_type,
                "content_length": content_length,
                "preview": preview + ("...\n[truncated]" if truncated else ""),
            }
    except urllib.error.HTTPError as e:
        logger.error("HTTP error: %s", e)
        return {"url": url, "status": f"HTTPError {e.code}", "content_type": "", "content_length": "", "preview": ""}
    except urllib.error.URLError as e:
        logger.error("URL error: %s", e.reason)
        return {"url": url, "status": f"URLError {e.reason}", "content_type": "", "content_length": "", "preview": ""}
    except Exception as e:
        logger.exception("Unexpected error fetching URL")
        return {"url": url, "status": f"Error {e}", "content_type": "", "content_length": "", "preview": ""}


# -----------------------
# Fiction: Plot My Novel
# -----------------------
def generate_novel_plot(tone: str, setting: str, protagonist: str, length: int = 3) -> str:
    """
    Create a short multi-act outline. This is purely fictional content generator.
    """
    tones = {
        "gothic": [
            "ancient houses with creaking floorboards",
            "unrelenting fog",
            "a family secret that sours the bloodline",
        ],
        "noir": [
            "rain-slick streets and neon bruises",
            "a protagonist with a poker face and unspoken debts",
            "moral compromise and a slow burn of consequences",
        ],
        "comedic": [
            "absurd misunderstandings and wry asides",
            "a cheerful subversion of dark tropes",
            "an ultimately warm, if dry, resolution",
        ],
        "default": [
            "a quiet town with things that shouldn't be quiet",
            "objects that hold memory",
            "an intersecting cast with small betrayals",
        ],
    }
    chosen = tones.get(tone.lower(), tones["default"])
    acts = []
    for i in range(1, length + 1):
        act_lines = []
        act_lines.append(f"Act {i}:")
        if i == 1:
            act_lines.append(f"Introduce {protagonist} and the world: {random.choice(chosen)}.")
            act_lines.append("A small unsettling event hints at deeper rot.")
        elif i == length:
            act_lines.append("Confrontation and revelation: truths are unearthed, consequences unfold.")
            act_lines.append("A bittersweet denouement that leaves a lingering chill.")
        else:
            act_lines.append("Rising complications and moral choices deepen the mystery.")
            act_lines.append("An ally proves false; a new clue reframes everything.")
        acts.append("\n".join(act_lines))
    palette = f"Tone: {tone}. Setting: {setting}."
    return palette + "\n\n" + "\n\n".join(acts)


# -----------------------
# Safe trivia: Name That Poison (educational)
# -----------------------
_POISON_TRIVIA = [
    {
        "name": "Belladonna (Atropa belladonna)",
        "clue": "Historically noted for causing dilated pupils and delirium; used in small doses as cosmetic in certain eras.",
        "fact": "Belladonna is a toxic plant historically associated with folklore and cosmetic use; discussion here is historical and non-actionable.",
    },
    {
        "name": "Aconite (Aconitum napellus)",
        "clue": "A plant whose historical accounts describe numbness and cardiac disturbance after ingestion; featured in medicinal folklore with a dangerous reputation.",
        "fact": "Aconite has a long history in herb lore; this entry is educational only.",
    },
    {
        "name": "Oleander (Nerium oleander)",
        "clue": "A common ornamental shrub whose parts are toxic; historical anecdotes caution against use in poultry feed and folkloric remedies.",
        "fact": "Oleander is widely cultivated for flowers but contains compounds that can be toxic to animals and humans; this is a safety note, not an instruction.",
    },
]


def run_poison_trivia() -> None:
    """
    Run a short interactive trivia quiz. All content is historical/educational and non-actionable.
    """
    print("Name That Poison - a brief historical trivia quiz (educational, non-actionable)\n")
    q = random.choice(_POISON_TRIVIA)
    print("Clue:")
    print(textwrap.fill(q["clue"], width=78))
    print("\nOptions:")
    options = random.sample(_POISON_TRIVIA, k=len(_POISON_TRIVIA))
    for idx, opt in enumerate(options, start=1):
        print(f"  {idx}. {opt['name']}")
    try:
        choice = input("\nYour guess (enter number): ").strip()
        if not choice:
            print("No answer given. The correct answer was:")
            print(f"  {q['name']}\n")
        else:
            idx = int(choice) - 1
            selected = options[idx]
            if selected["name"] == q["name"]:
                print("\nCorrect. A tasteful, academic nod.\n")
            else:
                print("\nIncorrect. The correct answer was:")
                print(f"  {q['name']}\n")
    except (ValueError, IndexError):
        print("\nInput not understood. The correct answer was:")
        print(f"  {q['name']}\n")
    print("Contextual note:")
    print(textwrap.fill(q["fact"], width=78))
    print("\nReminder: this quiz is for historical knowledge only; do not attempt to handle or use toxic substances.")


# -----------------------
# CLI wiring
# -----------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="singlefile-cli", description="Single-file Python CLI demo")
    # Do not set required=True so the parser won't error when invoked with no arguments.
    # We'll handle the no-command case explicitly in main().
    sub = p.add_subparsers(dest="command")

    # stats
    pst = sub.add_parser("stats", help="Analyze text from a file or stdin")
    pst.add_argument("--file", "-f", help="Path to a text file (if omitted, reads stdin)")

    # fetch
    pf = sub.add_parser("fetch", help="Fetch a URL and show a safe preview")
    pf.add_argument("url", help="HTTP/HTTPS URL to fetch")

    # plot-novel
    pp = sub.add_parser("plot-novel", help="Generate a short fictional novel outline")
    pp.add_argument("--tone", "-t", default="gothic", help="Tone (gothic, noir, comedic)")
    pp.add_argument("--setting", "-s", default="an unnamed town", help="Setting description")
    pp.add_argument("--protagonist", "-p", default="Your protagonist", help="Protagonist name")
    pp.add_argument("--acts", "-a", type=int, default=3, help="Number of acts (default: 3)")

    # name-poison-trivia
    sub.add_parser("name-poison-trivia", help="Run a short, safe trivia about historically-noted poisonous plants")

    return p


def cmd_stats(args: argparse.Namespace) -> int:
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                text = fh.read()
        except Exception as e:
            logger.error("Failed to read file: %s", e)
            return 2
    else:
        if sys.stdin.isatty():
            print("Reading from stdin. Type/paste text and press Ctrl-D (or Ctrl-Z on Windows) when done.")
        text = sys.stdin.read()

    stats = analyze_text(text)
    print(pretty_stats(stats))
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    summary = fetch_url_summary(args.url)
    print(f"URL: {summary.get('url')}")
    print(f"Status: {summary.get('status')}")
    print(f"Content-Type: {summary.get('content_type')}")
    if summary.get("content_length"):
        print(f"Content-Length: {summary.get('content_length')}")
    print("\nPreview (escaped HTML, truncated):\n")
    print(summary.get("preview") or "[no preview available]")
    return 0


def cmd_plot_novel(args: argparse.Namespace) -> int:
    outline = generate_novel_plot(tone=args.tone, setting=args.setting, protagonist=args.protagonist, length=args.acts)
    print("\n" + outline + "\n")
    return 0


def cmd_name_poison_trivia(_: argparse.Namespace) -> int:
    run_poison_trivia()
    return 0


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # If no subcommand was provided, print help and exit with success.
    if getattr(args, "command", None) is None:
        parser.print_help()
        return 0

    # Dispatch
    if args.command == "stats":
        return cmd_stats(args)
    elif args.command == "fetch":
        return cmd_fetch(args)
    elif args.command == "plot-novel":
        return cmd_plot_novel(args)
    elif args.command == "name-poison-trivia":
        return cmd_name_poison_trivia(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
        raise SystemExit(130)
