import sys
from pathlib import Path

source_route = Path(__file__).parent.absolute()
lib_dir = source_route.parent / "lib"
sys.path.append(str(source_route))
sys.path.append(str(lib_dir))
