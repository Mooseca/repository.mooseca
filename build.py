#!/usr/bin/env python3
"""Rebuilds the Kodi repository that GitHub Pages serves.

    python3 build.py [add-on zip ...]

Copies each add-on zip into repo/<id>/, zips the repository add-on itself, then writes
repo/addons.xml (the newest version of every add-on), its .md5, and the index pages Kodi's
file manager browses."""
import hashlib
import os
import re
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ID = 'repository.mooseca'
DATA = os.path.join(HERE, 'repo')


def version_key(v):
    return [int(x) if x.isdigit() else x for x in re.split(r'[.\-~+]', v)]


def addon_xml(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        name = next(n for n in z.namelist() if n.count('/') == 1 and n.endswith('/addon.xml'))
        return z.read(name).decode('utf-8')


def meta(xml):
    m = re.search(r'<addon\b[^>]*?\bid="([^"]+)"[^>]*?\bversion="([^"]+)"', xml, re.S)
    return m.group(1), m.group(2)


def extract_assets(zip_path, dest):
    """Kodi shows a repository add-on's icon, fanart and screenshots from next to its zips."""
    xml = addon_xml(zip_path)
    aid, _ = meta(xml)
    wanted = re.findall(r'<(?:icon|fanart|banner|clearlogo|screenshot)>([^<]+)<', xml)
    with zipfile.ZipFile(zip_path) as z:
        for rel in wanted:
            try:
                data = z.read('%s/%s' % (aid, rel))
            except KeyError:
                continue
            out = os.path.join(dest, rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, 'wb') as fh:
                fh.write(data)


def add(zip_path):
    aid, ver = meta(addon_xml(zip_path))
    dest = os.path.join(DATA, aid)
    os.makedirs(dest, exist_ok=True)
    shutil.copy(zip_path, os.path.join(dest, '%s-%s.zip' % (aid, ver)))
    return aid, ver


def zip_repository_addon():
    src = os.path.join(HERE, REPO_ID)
    with open(os.path.join(src, 'addon.xml')) as fh:
        _, ver = meta(fh.read())
    out = os.path.join(DATA, REPO_ID, '%s-%s.zip' % (REPO_ID, ver))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(os.listdir(src)):
            z.write(os.path.join(src, name), '%s/%s' % (REPO_ID, name))
    shutil.copy(out, os.path.join(HERE, os.path.basename(out)))  # top level: what people install from zip
    for old in os.listdir(HERE):
        if old.startswith(REPO_ID + '-') and old.endswith('.zip') and old != os.path.basename(out):
            os.remove(os.path.join(HERE, old))
    return os.path.basename(out)


def index(folder, names):
    links = ''.join('<a href="%s">%s</a><br>\n' % (n, n) for n in names)
    with open(os.path.join(folder, 'index.html'), 'w') as fh:
        fh.write('<!DOCTYPE html>\n<html><head><meta charset="utf-8"><title>%s</title></head><body>\n%s</body></html>\n'
                 % (os.path.basename(folder), links))


LANDING = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mooseca Kodi repository</title>
<link rel="icon" href="repo/repository.mooseca/icon.png">
<style>
  body {{ margin: 0; font: 17px/1.55 system-ui, -apple-system, "Segoe UI", Inter, sans-serif; color: #e9e6ff;
         background: linear-gradient(160deg, #2e1e6e 0%, #0a081e 70%) fixed; }}
  main {{ max-width: 860px; margin: 0 auto; padding: 32px 20px 60px; }}
  .banner {{ width: 100%; border-radius: 14px; box-shadow: 0 10px 40px #0008; }}
  h2 {{ margin: 40px 0 12px; font-size: 22px; color: #fff; }}
  .url {{ display: flex; gap: 10px; align-items: center; background: #ffffff12; border: 1px solid #ffffff26;
          border-radius: 10px; padding: 14px 16px; font: 600 19px ui-monospace, monospace; color: #fff; word-break: break-all; }}
  .url button {{ margin-left: auto; font: 600 14px system-ui, sans-serif; color: #fff; background: #7c5cff;
                 border: 0; border-radius: 8px; padding: 8px 14px; cursor: pointer; }}
  ol {{ padding-left: 22px; }} li {{ margin: 6px 0; }}
  b {{ color: #fff; }} code {{ background: #ffffff18; padding: 1px 6px; border-radius: 5px; }}
  .card {{ display: flex; gap: 18px; align-items: center; background: #ffffff0d; border: 1px solid #ffffff1f;
           border-radius: 14px; padding: 16px; }}
  .card img {{ width: 84px; height: 84px; border-radius: 16px; }}
  .card h3 {{ margin: 0 0 4px; color: #fff; }} .card p {{ margin: 0; color: #c9c3f0; }}
  .shot {{ width: 100%; border-radius: 12px; margin-top: 14px; }}
  a {{ color: #b9a8ff; }}
  .zip a {{ display: inline-block; margin-top: 6px; padding: 10px 16px; border-radius: 9px; background: #7c5cff;
          color: #fff; text-decoration: none; font-weight: 600; }}
  footer {{ margin-top: 48px; color: #9d96c8; font-size: 14px; }}
</style></head><body><main>
<img class="banner" src="docs/banner.png" alt="Mooseca Repository">

<h2>Add this address to Kodi</h2>
<div class="url"><span id="u">https://mooseca.github.io/repository.mooseca/</span>
<button onclick="navigator.clipboard.writeText(document.getElementById('u').textContent);this.textContent='Copied'">Copy</button></div>

<h2>Install</h2>
<ol>
  <li><b>Settings &rarr; System &rarr; Add-ons</b>: turn on <b>Unknown sources</b>.</li>
  <li><b>Settings &rarr; File manager &rarr; Add source</b>: choose <code>&lt;None&gt;</code>, enter the address above and name it <code>mooseca</code>.</li>
  <li><b>Settings &rarr; Add-ons &rarr; Install from zip file &rarr; mooseca</b>: pick <code>{zip}</code>.</li>
  <li><b>Install from repository &rarr; Mooseca Repository</b>: pick an add-on and <b>Install</b>.</li>
</ol>
<p>Kodi then keeps the add-ons up to date by itself. Or download the repository zip and use <i>Install from zip file</i> on it:<br>
<span class="zip">
<a href="{zip}">{zip}</a>
</span></p>

<h2>Add-ons</h2>
<div class="card"><img src="repo/plugin.video.seerrhub/icon.png" alt="">
<div><h3>Seerr Hub</h3><p>Search everything, open it in the right streaming app, play it from Plex / Jellyfin / Emby, or request it in Seerr.
<a href="https://github.com/Mooseca/plugin.video.seerrhub">Read more on GitHub</a></p></div></div>
<img class="shot" src="docs/trending.jpg" alt="Seerr Hub in Kodi">

<footer>Source: <a href="https://github.com/Mooseca/repository.mooseca">Mooseca/repository.mooseca</a> &middot; MIT license</footer>
</main></body></html>
"""


def landing(repo_zip):
    """The page this address opens in a browser. Kodi's file manager reads the same page: it only takes links
    written exactly <a href="x">x</a> (href first, link text = file name), so it sees just the repository zip."""
    with open(os.path.join(HERE, 'index.html'), 'w') as fh:
        fh.write(LANDING.format(zip=repo_zip))


def main():
    for z in sys.argv[1:]:
        print('added %s %s' % add(z))
    repo_zip = zip_repository_addon()
    entries, dirs = [], []
    for aid in sorted(os.listdir(DATA)):
        folder = os.path.join(DATA, aid)
        if not os.path.isdir(folder):
            continue
        zips = sorted((f for f in os.listdir(folder) if f.endswith('.zip')),
                      key=lambda f: version_key(f[len(aid) + 1:-4]))
        if not zips:
            continue
        newest = os.path.join(folder, zips[-1])
        extract_assets(newest, folder)
        xml = re.sub(r'^<\?xml[^>]*\?>\s*', '', addon_xml(newest).strip())
        entries.append(xml)
        with open(newest, 'rb') as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        with open(newest + '.sha256', 'w') as fh:
            fh.write(digest)
        index(folder, zips)
        dirs.append(aid + '/')
        print('%s -> %s' % (aid, zips[-1]))
    body = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n%s\n</addons>\n' % '\n'.join(entries)
    with open(os.path.join(DATA, 'addons.xml'), 'w', encoding='utf-8') as fh:
        fh.write(body)
    with open(os.path.join(DATA, 'addons.xml.md5'), 'w') as fh:
        fh.write(hashlib.md5(body.encode('utf-8')).hexdigest())
    index(DATA, dirs + ['addons.xml', 'addons.xml.md5'])
    landing(repo_zip)
    open(os.path.join(HERE, '.nojekyll'), 'w').close()


if __name__ == '__main__':
    main()
