"""midterm.src.html에 글씨체를 필요한 글자만 잘라 넣어 midterm.html을 만든다.

사용법: python3 build_deck.py <PretendardVariable.ttf 경로> <Outfit[wght].ttf 경로>
결과 파일은 인터넷 없이도 같은 글씨체로 보인다.
"""
import base64
import io
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
SRC = HERE / "midterm.src.html"
OUT = HERE / "midterm.html"


def embed(font_path: str, text: str, family: str, weights: str) -> str:
    font = TTFont(font_path)
    opts = subset.Options()
    opts.flavor = "woff"
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff"
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    print(f"  {family}: {len(buf.getvalue()) / 1024:.0f}KB")
    return (
        f"@font-face {{ font-family: \"{family}\"; font-style: normal; font-display: block; "
        f"font-weight: {weights}; src: url(data:font/woff;base64,{b64}) format(\"woff\"); }}"
    )


def main(body_font: str, display_font: str) -> None:
    html = SRC.read_text(encoding="utf-8")
    # 화면에 나올 수 있는 모든 글자 + 기본 ASCII와 문장 부호
    chars = set(html) | set(chr(c) for c in range(0x20, 0x7F)) | set("…·–—“”‘’→←↑↓×①②③④")
    chars = {c for c in chars if ord(c) >= 0x20}
    face = embed(body_font, "".join(sorted(chars)), "Pretendard", "45 920")
    # 표지 로고(gapfuzz)용 영문 글씨체
    face += "\n" + embed(display_font, "gapfuz", "Outfit", "100 900")
    OUT.write_text(html.replace("/*@@FONTFACE@@*/", face), encoding="utf-8")
    print(f"{OUT.name}: 글자 {len(chars)}개, 전체 {OUT.stat().st_size / 1024:.0f}KB")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
