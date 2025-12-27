import streamlit as st
import tempfile
import os
from extractor import extract_material_schedule

st.set_page_config(page_title="EPC PDF Extractor", layout="centered")

st.title("📄 EPC PDF Material Schedule Extractor")
st.write("Upload AutoCAD / EPC PDF and download structured Excel")

uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])

if uploaded_file:
    st.success("PDF uploaded successfully")

    if st.button("Extract to Excel"):
        with st.spinner("Processing PDF..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                pdf_path = os.path.join(tmpdir, uploaded_file.name)
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_file.read())

                output_path = os.path.join(tmpdir, "material_schedule.xlsx")

                try:
                    extract_material_schedule(pdf_path, output_path)

                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="Download Excel",
                            data=f,
                            file_name="material_schedule.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                except Exception as e:
                    st.error(str(e))
