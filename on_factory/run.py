"""쇼츠공장 tick 이 부르는 진입점. 이 파일 위치로 ON 레포 루트를 찾아 python -m on_factory 와 똑같이 실행한다."""
import sys, runpy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.argv = ["on_factory", *sys.argv[1:]]
runpy.run_module("on_factory", run_name="__main__")
