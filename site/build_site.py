"""site/index.src.html에 Pretendard·Outfit을 필요한 글자만 잘라 넣어 site/index.html을 만든다.

사용법: python3 site/build_site.py <PretendardVariable.ttf> <Outfit[wght].ttf>
발표자료(presentation/build_deck.py)와 같은 방식이다. 결과 파일 하나로 GitHub Pages에 그대로 올릴 수 있다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "presentation"))
from build_deck import embed  # noqa: E402

HERE = Path(__file__).resolve().parent
SRC, OUT = HERE / "index.src.html", HERE / "index.html"


def main(body_font: str, display_font: str) -> None:
    html = SRC.read_text(encoding="utf-8")
    data = (HERE / "data.json").read_text(encoding="utf-8").replace("</", "<\\/")
    chars = set(html) | set(data) | set(chr(c) for c in range(0x20, 0x7F)) | set("…·–—“”‘’→←↑↓×")
    chars = {c for c in chars if ord(c) >= 0x20}
    face = embed(body_font, "".join(sorted(chars)), "Pretendard", "45 920")
    face += "\n" + embed(display_font, "gapfuz0123456789.%/×+−-", "Outfit", "100 900")
    html = html.replace("/*@@FONTFACE@@*/", face).replace("/*@@DATA@@*/", data)
    OUT.write_text(html, encoding="utf-8")
    print(f"{OUT.name}: 글자 {len(chars)}개, 전체 {OUT.stat().st_size / 1024:.0f}KB")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
