import camelot
import pandas as pd

def extract_material_schedule(pdf_path, output_file):
    tables = camelot.read_pdf(
        pdf_path,
        pages="1",
        flavor="lattice",
        line_scale=40
    )

    if tables.n == 0:
        raise RuntimeError("No tables detected")

    df_raw = tables[0].df.reset_index(drop=True)

    # Detect header
    header_idx = None
    for i in range(min(15, len(df_raw))):
        row = " ".join(df_raw.iloc[i].astype(str).str.upper())
        if "MARK" in row and "PROFILE" in row and "QTY" in row:
            header_idx = i
            break

    if header_idx is None:
        raise RuntimeError("Header row not found")

    header = df_raw.iloc[header_idx].fillna("").astype(str)

    col_map = {}
    current = None

    for idx, cell in enumerate(header):
        c = cell.upper()
        if "MARK" in c:
            current = "MARK"
        elif "PROFILE" in c:
            current = "PROFILE"
        elif "LENGTH" in c:
            current = "LENGTH"
        elif "GRADE" in c:
            current = "GRADE"
        elif "QTY" in c:
            current = "QTY"
        elif "UNIT" in c:
            current = "UNIT_WEIGHT"
        elif "TOTAL" in c:
            current = "TOTAL_WEIGHT"
        if current:
            col_map.setdefault(current, []).append(idx)

    data = {}
    for k, idxs in col_map.items():
        data[k] = (
            df_raw.iloc[header_idx + 1 :, idxs]
            .apply(lambda x: " ".join(x.dropna().astype(str)), axis=1)
            .str.strip()
        )

    df = pd.DataFrame(data).dropna(how="all")

    def classify(r):
        m = str(r.get("MARK", "")).upper()
        p = str(r.get("PROFILE", "")).upper()
        if "TOTAL" in m or "TOTAL" in p:
            return "TOTAL"
        if p == "BOLT":
            return "BOLT"
        if m.endswith("HT"):
            return "REBAR"
        return "OTHER"

    df["ROW_TYPE"] = df.apply(classify, axis=1)

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df[df["ROW_TYPE"] == "REBAR"].to_excel(writer, "REBAR", index=False)
        df[df["ROW_TYPE"] == "BOLT"].to_excel(writer, "BOLTS", index=False)
        df[df["ROW_TYPE"] == "TOTAL"].to_excel(writer, "TOTALS", index=False)
        df[df["ROW_TYPE"] == "OTHER"].to_excel(writer, "OTHER", index=False)

    return output_file
