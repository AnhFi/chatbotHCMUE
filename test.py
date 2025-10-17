import pdfplumber, camelot, pandas as pd, json

PDF_PATH = "so_tay_2.pdf"
OUT_JSON = "so_tay_all_tables_clean.json"

# === 1️⃣ Đặt tên loại bảng theo số trang (mày chỉnh theo file PDF của mày) ===
page_type_map = {
    42: "thang_diem_10_4",     # Trang 42: bảng thang điểm
    44: "thang_diem_4",        # Trang 44: bảng thang điểm
    45: "xep_loai_hoc_luc",        # Trang 45: bảng xếp loại học lực
    70: "yeu_cau_hoc_bong",       # Trang 70: bảng xếp loại học bổng
    91: "xep_loai_hoc_bong",       # ví dụ
    99: "diem_ren_luyen1",
    100: "diem_ren_luyen2",
    101: "diem_ren_luyen3",
    102: "diem_ren_luyen4",
    103: "diem_ren_luyen5"
}

# === 2️⃣ Làm sạch bảng đơn giản ===
def clean_df(df):
    df = df.dropna(how="all", axis=0).dropna(how="all", axis=1)
    df = df.applymap(lambda x: str(x).strip() if pd.notna(x) else x)
    return df.reset_index(drop=True)

# === 3️⃣ Trích bảng theo từng trang ===
def extract_multiple_pages(pdf_path, pages):
    results = []
    for i in pages:
        print(f"🔍 Đang đọc trang {i}...")
        try:
            tables = camelot.read_pdf(pdf_path, pages=str(i), flavor="lattice")
            for idx, t in enumerate(tables):
                df = clean_df(t.df)
                if len(df) < 2 or len(df.columns) < 2:
                    continue
                df.columns = [str(c).strip() for c in df.iloc[0]] if len(df) > 1 else df.columns
                df = df[1:].reset_index(drop=True)
                table_type = page_type_map.get(i, "khac")  # 🔥 Lấy loại bảng theo trang
                results.append({
                    "page": i,
                    "table_index": idx + 1,
                    "type": table_type,
                    "columns": list(df.columns),
                    "data": df.to_dict(orient="records")
                })
        except Exception as e:
            print(f"⚠️ Lỗi trang {i}: {e}")
    return results

# === 4️⃣ MAIN ===
pages_to_check = list(page_type_map.keys())
tables = extract_multiple_pages(PDF_PATH, pages_to_check)

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(tables, f, ensure_ascii=False, indent=2)

print(f"\n✅ Đã trích được {len(tables)} bảng từ {len(pages_to_check)} trang.")
print(f"💾 File lưu tại: {OUT_JSON}")

# === 5️⃣ In thử vài bảng xem đúng chưa ===
for t in tables:
    df = pd.DataFrame(t["data"])
    print(f"\n📘 Trang {t['page']} | Loại: {t['type']}")
    print(df.to_markdown(index=False))

