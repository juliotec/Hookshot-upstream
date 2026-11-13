"""Quads with 8-bit indices are drawn on a device without uint8 index support.

draw() skipped every indexed draw with 8-bit indices (d.itype == 0) when the device has no VK_EXT_index_type_uint8,
before the quads path. Quads do not need it: their indices are read on the CPU (one byte each for 8-bit ones) and the
draw binds 32-bit indices made in the stream. Now only draws that give 8-bit indices to the GPU are skipped.

python -I -B tests/test_uint8_quads.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VK = ROOT / "gpu" / "vk"


def main():
    src = (VK / "vk_draw.cpp").read_text(encoding="utf-8")
    quads = src.find("if (d.prim == NVN_DRAW_PRIMITIVE_QUADS) {")
    if quads < 0:
        raise SystemExit("the quads path in draw() is gone: this test needs updating")
    body = src[quads:src.index("\n        return;\n    }\n", quads)]
    if "unit = d.itype == 0 ? 1" not in body or "VK_INDEX_TYPE_UINT32" not in body:
        raise SystemExit("the quads path no longer reads 8-bit indices on the CPU into 32-bit ones: this test needs updating")
    before = src[src.rfind("\n", 0, src.rfind("SKIP_HERE();", 0, quads)) + 1:quads]
    skip = [line for line in before.splitlines() if "!dev.index_uint8" in line and "SKIP_HERE();" in line]
    if not skip:
        raise SystemExit("the skip of 8-bit index draws without uint8 support is gone: this test needs updating")
    if "d.prim != NVN_DRAW_PRIMITIVE_QUADS" not in skip[-1]:
        raise SystemExit("quads with 8-bit indices are skipped without uint8 support, though they draw with 32-bit indices")
    print("quads with 8-bit indices are drawn without uint8 index support")


if __name__ == "__main__":
    main()
