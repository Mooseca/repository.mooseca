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
    index(HERE, [repo_zip])
    open(os.path.join(HERE, '.nojekyll'), 'w').close()


if __name__ == '__main__':
    main()
