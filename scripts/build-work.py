#!/usr/bin/env python3
"""
build-work.py — regenerate the Page Lab "The Work" marquee from source folders.

WHERE YOUR WORK LIVES (the source of truth — just drop files here):
  services/Statics/          static creatives (png/jpg/jpeg/webp)  -> bottom row
  services/Pages/            page screenshots (png/jpg/jpeg/webp)  -> top row
  services/Pages/pages.txt   OR live page URLs, one per line ("url | Label"),
                             screenshotted automatically at mobile width.

WHAT IT GENERATES (safe to delete, always regenerated):
  services/assets/page-lab/statics/*.jpg   web-optimized copies
  services/assets/page-lab/pages/*.jpg     web-optimized copies
  ...then rewrites the two marquee tracks in services/page-lab/index.html
  between the <!-- PL:PAGES --> and <!-- PL:STATICS --> marker comments.

RUN:
  python3 services/scripts/build-work.py

Requires macOS `sips` (built in) and Google Chrome (only if pages.txt lists URLs).
Everything is ordered alphabetically by filename, so prefix names (01-, 02-) to
control order in the marquee.
"""
import os, re, glob, subprocess, sys

SERVICES = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")

# card dimensions per row (must match the CSS in page-lab/index.html)
PAGE_W, PAGE_H = 208, 300      # portrait page screenshots
STATIC_W, STATIC_H = 256, 320  # 4:5 static creatives


def slugify(name):
    base = os.path.splitext(os.path.basename(name))[0].lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", base)).strip("-") or "item"


def sips_jpg(src, dst, longest=1000, quality=82):
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(quality),
         "-Z", str(longest), src, "--out", dst],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def clean_dir(d):
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, "*.jpg")):
        os.remove(f)


def capture_url(url, dst_png):
    if not os.path.exists(CHROME):
        sys.exit("Google Chrome not found — needed to screenshot URLs in pages.txt.")
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=2", "--window-size=430,640",
         f"--screenshot={dst_png}", url],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def images_in(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(f for f in os.listdir(folder)
                  if f.lower().endswith(IMG_EXT) and not f.startswith("."))


def build_statics():
    src, out = os.path.join(SERVICES, "Statics"), os.path.join(SERVICES, "assets/page-lab/statics")
    clean_dir(out)
    items = []
    for f in images_in(src):
        s = slugify(f)
        sips_jpg(os.path.join(src, f), os.path.join(out, s + ".jpg"))
        items.append((f"../assets/page-lab/statics/{s}.jpg", "Static creative by ClickDose Labs"))
    return items


def build_pages():
    src, out = os.path.join(SERVICES, "Pages"), os.path.join(SERVICES, "assets/page-lab/pages")
    clean_dir(out)
    os.makedirs(src, exist_ok=True)
    items, used = [], set()

    def add(slug, src_path, alt, is_url=False):
        s, n = slug, 2
        while s in used:            # avoid collisions
            s, n = f"{slug}-{n}", n + 1
        used.add(s)
        dst = os.path.join(out, s + ".jpg")
        if is_url:
            tmp = os.path.join(out, "_tmp.png")
            capture_url(src_path, tmp)
            sips_jpg(tmp, dst)
            os.remove(tmp)
        else:
            sips_jpg(src_path, dst)
        items.append((f"../assets/page-lab/pages/{s}.jpg", alt))

    # 1) image files dropped straight into Pages/
    for f in images_in(src):
        add(slugify(f), os.path.join(src, f), "Landing page by ClickDose Labs")

    # 2) live URLs in Pages/pages.txt
    txt = os.path.join(src, "pages.txt")
    if os.path.exists(txt):
        for line in open(txt, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            url, _, label = line.partition("|")
            url, label = url.strip(), (label.strip() or "Landing page by ClickDose Labs")
            slug = slugify(url.rstrip("/").split("/")[-1] or "page")
            add(slug, url, label, is_url=True)
    return items


def track_html(items, w, h, indent="            "):
    if not items:
        return f"{indent}<!-- no items found; drop files in the source folder and re-run -->"

    def card(src, alt, hidden):
        attr = ' aria-hidden="true"' if hidden else ""
        text = "" if hidden else alt
        return (f'{indent}<div class="mq-card"{attr}>'
                f'<img src="{src}" alt="{text}" loading="lazy" width="{w}" height="{h}"></div>')

    first = [card(s, a, False) for s, a in items]   # visible set
    dupe = [card(s, a, True) for s, a in items]     # duplicate for the seamless -50% loop
    return "\n".join(first + dupe)


def inject(html, tag, inner):
    start, end = f"<!-- PL:{tag}:START -->", f"<!-- PL:{tag}:END -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if not pattern.search(html):
        sys.exit(f"Marker PL:{tag} not found in index.html")
    replacement = f"{start}\n{inner}\n            {end}"
    return pattern.sub(lambda _m: replacement, html)


def main():
    statics = build_statics()
    pages = build_pages()
    print(f"optimized {len(pages)} page(s) and {len(statics)} static(s)")
    if not pages or not statics:
        print("warning: a row is empty — the marquee will show a placeholder comment.")

    html_path = os.path.join(SERVICES, "page-lab/index.html")
    html = open(html_path, encoding="utf-8").read()
    html = inject(html, "PAGES", track_html(pages, PAGE_W, PAGE_H))
    html = inject(html, "STATICS", track_html(statics, STATIC_W, STATIC_H))
    open(html_path, "w", encoding="utf-8").write(html)
    print("page-lab/index.html marquee updated.")


if __name__ == "__main__":
    main()
