"""무음 릴스 + (릴리아 배경음) + (선택: 내레이션) → 최종 mp4.

- 배경음: 쇼츠공장 릴리아 뱅크 content/music_bank/on/*.mp3 (편 slug 로 안정적으로 고른다).
  뱅크가 비었으면 레포의 brand/sound/bed_*.m4a (온이 합성한 기본음).
- 내레이션: queue 항목의 narration=[{"t": 시작초, "text": "..."}] 이 있으면 쇼츠공장 voice.speak(Live 모델)로 녹음해
  그 시각에 놓는다. 목소리가 나오면 배경음을 사이드체인으로 낮춘다(쇼츠공장 tips/mix.py 방식).
- 결과 음량 -14 LUFS. 오디오 스트림이 없으면 예외(무음 릴스 발행 금지).
"""
import hashlib, json, subprocess, sys
from pathlib import Path
from .config import ROOT, MUSIC_BANK, SHORTS_ROOT, VOICE_MODEL, VOICE_NAME


def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise RuntimeError(f"ffmpeg 실패: {r.stderr[-400:]}")
    return r.stdout


def duration(p):
    return float(_run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]).strip())


def pick_bed(slug):
    tracks = sorted(MUSIC_BANK.glob("*.mp3")) if MUSIC_BANK.is_dir() else []
    if not tracks:
        tracks = sorted((ROOT / "brand" / "sound").glob("bed_*.m4a"))
    if not tracks:
        raise RuntimeError("배경음이 하나도 없다 (릴리아 뱅크·brand/sound 모두 비어 있음)")
    return tracks[int(hashlib.sha1(slug.encode()).hexdigest(), 16) % len(tracks)]


def narrate(lines, workdir):
    sys.path.insert(0, str(SHORTS_ROOT))
    from shared.pipeline.voice import speak
    outs = []
    for i, ln in enumerate(lines):
        p = Path(workdir) / f"n{i:02d}.mp3"
        if not p.exists():
            speak(ln["text"], p, voice=VOICE_NAME, lang="ko", model=VOICE_MODEL)
        outs.append((float(ln["t"]), p))
    return outs


def build(item):
    src = ROOT / item["files"][0]
    final = ROOT / "reels" / "final" / f"{item['slug']}.mp4"
    if final.exists():
        return final
    final.parent.mkdir(parents=True, exist_ok=True)
    work = ROOT / "state" / "audio_work" / item["slug"]
    work.mkdir(parents=True, exist_ok=True)
    dur = duration(src)
    bed = pick_bed(item["slug"])
    inputs = ["-i", str(src), "-stream_loop", "-1", "-i", str(bed)]
    filt = [f"[1:a]atrim=0:{dur:.2f},afade=t=in:d=0.4,afade=t=out:st={max(dur-1.2,0):.2f}:d=1.2,volume=0.55[bed]"]
    voice = item.get("narration") or []
    if voice:
        parts = narrate(voice, work)
        for k, (t, p) in enumerate(parts):
            inputs += ["-i", str(p)]
            filt.append(f"[{k+2}:a]adelay={int(t*1000)}|{int(t*1000)}[v{k}]")
        filt.append("".join(f"[v{k}]" for k in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0[vo]")
        filt.append("[vo]asplit=2[vo1][vo2]")
        filt.append("[bed][vo1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[duck]")
        filt.append("[duck][vo2]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[aout]")
    else:
        filt.append("[bed]loudnorm=I=-14:TP=-1.5:LRA=9[aout]")
    tmp = final.with_suffix(".tmp.mp4")
    _run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
          "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
          "-t", f"{dur:.2f}", "-movflags", "+faststart", str(tmp)])
    has_audio = _run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(tmp)]).strip()
    if not has_audio:
        tmp.unlink(missing_ok=True)
        raise RuntimeError("오디오 스트림 없음 - 무음 릴스는 발행하지 않는다")
    tmp.replace(final)
    return final
