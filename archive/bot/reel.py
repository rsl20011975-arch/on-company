"""텍스트 모션 릴스 렌더러: 장면 리스트 -> 1080x1920 mp4 (H.264, 30fps, 무음)
사용: python3 reel.py scenes.json out.mp4
scenes.json: [{"text":"...", "dur":2.0, "size":120, "accent":false}, ...]
"""
import json, sys, os, subprocess, pathlib
scenes = json.load(open(sys.argv[1])); out = sys.argv[2]
work = pathlib.Path(out).with_suffix(""); work.mkdir(exist_ok=True)
FPS = 30
subprocess.run(["node", str(pathlib.Path(__file__).parent/"reel_frames.js"), sys.argv[1], str(work)], check=True)
# ffmpeg: 각 장면을 dur초, 0.25초 페이드 전환
inputs=[]; filt=[]; n=len(scenes)
for i,s in enumerate(scenes):
    inputs += ["-loop","1","-t",str(s.get("dur",2)),"-i",str(work/f"s{i:02d}.png")]
    filt.append(f"[{i}:v]format=yuv420p,fade=t=in:st=0:d=0.25,fade=t=out:st={s.get('dur',2)-0.25}:d=0.25,setsar=1[v{i}]")
filt.append("".join(f"[v{i}]" for i in range(n))+f"concat=n={n}:v=1:a=0[out]")
subprocess.run(["ffmpeg","-y",*inputs,"-filter_complex",";".join(filt),"-map","[out]","-r",str(FPS),"-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart",out],check=True,capture_output=True)
print("ok", out)
