"""Download redistributable audio from original publishers; keep provenance."""

import hashlib
import html
import io
import array
import json
from pathlib import Path
import re
import urllib.request
import zipfile
import wave

ROOT = Path(__file__).resolve().parents[1]


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "DarknessLiesAhead/0.1"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def links(url):
    return [html.unescape(x) for x in re.findall(r"href=['\"]([^'\"]+)['\"]", fetch(url).decode())]


def main():
    dest = ROOT / "assets" / "audio"
    dest.mkdir(parents=True, exist_ok=True)
    records = []
    for name in ("impact-sounds", "rpg-audio", "interface-sounds"):
        page = "https://kenney.nl/assets/" + name
        url = next(x for x in links(page) if ".zip" in x)
        archive = ROOT / "downloads" / (name + ".zip")
        archive.parent.mkdir(exist_ok=True)
        archive.write_bytes(fetch(url))
        with zipfile.ZipFile(archive) as z:
            for member in z.namelist():
                if Path(member).suffix.lower() in (".ogg", ".wav", ".mp3"):
                    target = dest / name / Path(member).name
                    target.parent.mkdir(exist_ok=True)
                    target.write_bytes(z.read(member))
            licenses = [m for m in z.namelist() if "license" in m.lower() and m.endswith(".txt")]
            if licenses:
                (dest / name / "LICENSE.txt").write_bytes(z.read(licenses[0]))
        records.append(
            {
                "pack": name,
                "author": "Kenney",
                "license": "CC0-1.0",
                "source": page,
                "download": url,
                "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            }
        )
        print("Downloaded", name)
    for name, page, extension in (
        ("midnight", "https://opengameart.org/content/midnight", ".mp3"),
        ("wind", "https://opengameart.org/content/wind1", ".wav"),
    ):
        candidates = [x for x in links(page) if "/files/" in x and extension in x.lower()]
        if name == "midnight":
            candidates = [x for x in candidates if "lq" not in x.lower()]
        if not candidates:
            raise RuntimeError(f"No audio download found for {page}")
        url = candidates[0]
        data = fetch(url)
        (dest / (name + extension)).write_bytes(data)
        records.append(
            {
                "pack": name,
                "author": "Anton Revin" if name == "midnight" else "Luke.RUSTLTD",
                "license": "CC0-1.0",
                "source": page,
                "download": url,
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
        print("Downloaded", name, len(data))
    (dest / "provenance.json").write_text(json.dumps(records, indent=2), encoding="utf-8")


def combat():
    dest = ROOT / "assets" / "audio"
    page = "https://opengameart.org/content/gunshot-sounds"
    url = next(x for x in links(page) if "/files/" in x and x.endswith(".zip"))
    data = fetch(url)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        print(archive.namelist())
        candidate = next(x for x in archive.namelist() if "cz" in x.lower() and x.endswith(".wav"))
        original = archive.read(candidate)
        with wave.open(io.BytesIO(original)) as source:
            channels, rate = source.getnchannels(), source.getframerate()
            samples = array.array("h", source.readframes(source.getnframes()))
        starts = []
        index = 0
        while index < len(samples):
            if abs(samples[index]) > 10000:
                starts.append(max(0, index // channels - int(rate * 0.025)))
                index += int(rate * channels * 1.1)
            else:
                index += channels
        for number, start in enumerate(starts):
            clip = samples[start * channels : (start + int(rate * 1.1)) * channels]
            fade = int(rate * 0.08) * channels
            for index in range(len(clip) - fade, len(clip)):
                clip[index] = int(clip[index] * (len(clip) - index) / fade)
            with wave.open(str(dest / f"pistol_{number:03}.wav"), "wb") as output:
                output.setnchannels(channels)
                output.setsampwidth(2)
                output.setframerate(rate)
                output.writeframes(clip.tobytes())
    reload_page = "https://opengameart.org/content/gun-reload-sounds"
    reload_url = next(x for x in links(reload_page) if x.endswith("/gunreload1.wav"))
    (dest / "reload.wav").write_bytes(fetch(reload_url))
    records = json.loads((dest / "provenance.json").read_text(encoding="utf-8"))
    records = [r for r in records if r["pack"] not in ("pistol", "reload")]
    records.extend(
        [
            {
                "pack": "pistol",
                "author": "Tabasco",
                "license": "CC0-1.0",
                "source": page,
                "download": url,
                "archive_member": candidate,
                "changes": "Separated four recorded shots with 80ms tail fades",
            },
            {
                "pack": "reload",
                "author": "SpringySpringo",
                "license": "CC0-1.0",
                "source": reload_page,
                "download": reload_url,
            },
        ]
    )
    (dest / "provenance.json").write_text(json.dumps(records, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
    combat()
