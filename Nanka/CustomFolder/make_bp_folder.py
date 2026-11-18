# 難易度表のdata.jsonから、BP%帯で分けたbeatoraja用 folder/default.json を生成する
# 使い方: python make_bp_folder.py data.json default.json
import json, re, sys

ROOT_NAME = "任意のフォルダ名"
# (フォルダ名, 下限%(含まない), 上限%(含む))  None は制限なし
BANDS = [
    ("BP 0-2%",   None, 2),
    ("BP 2-4%",   2,    4),
    ("BP 4-6%",   4,    6),
    ("BP 6-8%",   6,    8),
    ("BP 8-10%",  8,    10),
    ("BP 10%-",   10,   None),
]
MODE = 0  # score.mode（LNモードで分けて記録される譜面用。通常は0）

def main(src, dst):
    data = json.load(open(src, encoding="utf-8"))
    md5s = sorted({e["md5"].lower() for e in data
                   if re.fullmatch(r"[0-9a-fA-F]{32}", e.get("md5") or "")})
    in_table = "md5 IN (" + ",".join(f"'{m}'" for m in md5s) + ")"
    played = f"{in_table} AND score.mode = {MODE} AND song.notes > 0"
    folders = []
    for name, lo, hi in BANDS:
        cond = [played]
        if lo is not None:
            cond.append(f"score.minbp * 100 > song.notes * {lo}")
        if hi is not None:
            cond.append(f"score.minbp * 100 <= song.notes * {hi}")
        folders.append({"name": name, "sql": " AND ".join(cond)})
    folders.append({"name": "未プレイ", "sql": f"{in_table} AND score.sha256 IS NULL"})
    out = [{"name": ROOT_NAME, "folder": folders}]
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"{len(md5s)} charts -> {dst}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
