from __future__ import annotations

import re
from pathlib import Path

from cffi import FFI


LIB_DIR = Path(__file__).resolve().parent.parent / "CMacmon.xcframework" / "macos-arm64"
HEADER_PATH = LIB_DIR / "Headers" / "macmon.h"


def _sanitize_header(header_text: str) -> str:
    without_block_comments = re.sub(r"/\*.*?\*/", "", header_text, flags=re.S)
    lines = []
    for line in without_block_comments.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if stripped == 'extern "C" {':
            continue
        if stripped == "}":
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def build_ffi() -> FFI:
    if not HEADER_PATH.exists():
        raise FileNotFoundError(
            f"Expected {HEADER_PATH} to exist. Place CMacmon.xcframework "
            "in the repository root before building."
        )

    ffi = FFI()
    ffi.cdef(_sanitize_header(HEADER_PATH.read_text()))
    ffi.set_source(
        "macmon._api",
        '#include "macmon.h"',
        include_dirs=[str(HEADER_PATH.parent)],
        library_dirs=[str(LIB_DIR)],
        libraries=["macmon"],
        extra_compile_args=["-arch", "arm64"],
        extra_link_args=["-arch", "arm64", f"-Wl,-rpath,{LIB_DIR}"],
    )
    return ffi


ffi = build_ffi()


if __name__ == "__main__":
    ffi.compile(verbose=True)
