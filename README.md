# Mooseca Kodi repository

Install this once and Kodi installs and updates Mooseca's add-ons by itself.

| Add-on | What it does |
|---|---|
| [Seerr Hub](https://github.com/Mooseca/plugin.video.seerrhub) | Search everything, open it in the right streaming app, play it from Plex / Jellyfin / Emby, or request it in Seerr |

## Install

1. **Settings → System → Add-ons** → turn on **Unknown sources** (Kodi asks for this before installing any add-on from a zip).
2. **Settings → File manager → Add source** → `<None>` → enter
   ```
   https://mooseca.github.io/repository.mooseca/
   ```
   and name it `mooseca`.
3. **Settings → Add-ons → Install from zip file** → `mooseca` → `repository.mooseca-1.0.0.zip`.
4. **Install from repository → Mooseca Repository → Video add-ons → Seerr Hub → Install**.

Kodi then updates Seerr Hub on its own, like any other add-on.

If you'd rather not add a source, download [`repository.mooseca-1.0.0.zip`](https://mooseca.github.io/repository.mooseca/repository.mooseca-1.0.0.zip), copy it to the device and use *Install from zip file* on it.

## Maintaining

GitHub Pages serves this repo's `main` branch. To publish a new add-on version:

```sh
python3 build.py ../seerrhub/plugin.video.seerrhub-2.1.0.zip
git add -A && git commit -m "Seerr Hub 2.1.0" && git push
```

`build.py` copies the zip into `repo/<id>/`, pulls out its artwork, rebuilds the repository add-on's own zip, and writes `repo/addons.xml`, its `.md5`, the `.sha256` of every zip, and the `index.html` pages Kodi's file manager browses. Bump the version in `repository.mooseca/addon.xml` only when its URLs change.
