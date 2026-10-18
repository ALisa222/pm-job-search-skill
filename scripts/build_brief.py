#!/usr/bin/env python3
"""Собирает бриф: подставляет JSON с данными в HTML-шаблон.

Usage: python3 build_brief.py brief-data.json brief.html
"""
import html
import json
import pathlib
import sys

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "templates" / "brief.html"
MARK = "/*__BRIEF_DATA__*/null"
REQUIRED = ["title", "date", "insight", "companies"]


def check(data):
    """Возвращает список проблем в данных; пустой — всё ок."""
    problems = [f"нет поля «{k}»" for k in REQUIRED if k not in data]
    for i, c in enumerate(data.get("companies", []), 1):
        name = c.get("name", f"#{i}")
        if c.get("tier") not in (1, 2, 3):
            problems.append(f"{name}: tier должен быть 1, 2 или 3")
        if not c.get("sources"):
            problems.append(f"{name}: нет источников")
    for r in data.get("openRoles", []):
        if not r.get("posted"):
            problems.append(f"вакансия {r.get('company', '?')}: нет даты публикации")
    return problems


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: build_brief.py brief-data.json brief.html")
    data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    problems = check(data)
    if problems:
        sys.exit("Бриф не собран:\n- " + "\n- ".join(problems))

    page = TEMPLATE.read_text(encoding="utf-8")
    if MARK not in page:
        sys.exit(f"в шаблоне нет метки {MARK}")
    # Внутри <script> строки "</" и "<!--" ломают разбор — экранируем.
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")
    page = page.replace(MARK, payload, 1)
    page = page.replace("<title>Продуктовый бриф</title>", f"<title>{html.escape(data['title'])}</title>", 1)

    out = pathlib.Path(sys.argv[2])
    out.write_text(page, encoding="utf-8")
    tiers = {t: sum(1 for c in data["companies"] if c.get("tier") == t) for t in (1, 2, 3)}
    print(f"ok: {out} — открытых ролей {len(data.get('openRoles', []))}, "
          f"компаний {len(data['companies'])} (тир 1: {tiers[1]}, тир 2: {tiers[2]}, тир 3: {tiers[3]})")


if __name__ == "__main__":
    main()
