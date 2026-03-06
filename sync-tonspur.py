#!/usr/bin/env python3
"""Sync statically rendered TONSPUR items from audio-examples.json into index.html."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


START_MARKER = "<!-- TONSPUR:START -->"
END_MARKER = "<!-- TONSPUR:END -->"


def sanitize_with_br(value: str) -> str:
    escaped = html.escape(value, quote=False)
    return (
        escaped.replace("&lt;br&gt;", "<br>")
        .replace("&lt;br/&gt;", "<br>")
        .replace("&lt;br /&gt;", "<br>")
    )


def render_item(item: dict) -> str:
    bg_class = f" {html.escape(str(item.get('bgClass', '')), quote=True)}" if item.get("bgClass") else ""
    has_bg = bool(item.get("bgClass") or item.get("bgImage"))
    bg_data = ' data-has-bg="true"' if has_bg else ""
    bg_style = ""
    if item.get("bgImage"):
        bg_image = html.escape(str(item["bgImage"]), quote=True)
        bg_style = f' style="--bg-image: url(\'{bg_image}\')"'

    desc_tag = "div" if item.get("useWorkDesc") else "p"
    desc_class = "work-desc" if item.get("useWorkDesc") else "work-description"

    music_title = html.escape(str(item.get("musicTitle", "")), quote=False)
    work_meta = html.escape(str(item.get("workMeta", "")), quote=False)
    work_title = html.escape(str(item.get("workTitle", "")), quote=False)
    work_year = html.escape(str(item.get("workYear", "")), quote=False)
    description = sanitize_with_br(str(item.get("description", "")))
    audio_file = html.escape(str(item.get("audioFile", "")), quote=True)

    return (
        f'                <div class="work-item{bg_class}"{bg_data}{bg_style}>\n'
        f'                    <div class="music-title">{music_title}</div>\n'
        f'                    <div class="work-meta">{work_meta}</div>\n'
        f'                    <div class="work-title">{work_title}</div>\n'
        f'                    <div class="work-year">{work_year}</div>\n'
        f'                    <{desc_tag} class="{desc_class}">{description}</{desc_tag}>\n'
        '                    <button class="audio-btn" aria-label="Audio abspielen" aria-pressed="false">\n'
        '                        <img src="assets/lautsprecher.png" alt="Lautsprecher Icon" class="audio-ohr" />\n'
        "                    </button>\n"
        f'                    <audio src="{audio_file}" preload="metadata"></audio>\n'
        "                </div>"
    )


def main() -> None:
    root = Path(__file__).resolve().parent
    index_path = root / "index.html"
    data_path = root / "audio-examples.json"

    examples = json.loads(data_path.read_text(encoding="utf-8"))
    rendered_items = "\n".join(render_item(item) for item in examples)

    index_content = index_path.read_text(encoding="utf-8")
    replacement = f"{START_MARKER}\n{rendered_items}\n                {END_MARKER}"
    updated_content, replaced = re.subn(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        replacement,
        index_content,
        flags=re.DOTALL,
    )

    if replaced != 1:
        raise RuntimeError("TONSPUR marker block not found exactly once in index.html.")

    index_path.write_text(updated_content, encoding="utf-8")
    print(f"Synced {len(examples)} TONSPUR items into index.html")


if __name__ == "__main__":
    main()
