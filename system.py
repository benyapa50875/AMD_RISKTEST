import streamlit as st
import vcf
import requests
import os

# ฟังก์ชันในการเรียกใช้ ClinVar API
def get_clinvar_info(variant_id):
    url = f'https://api.ncbi.nlm.nih.gov/variation/v0/beta/refsnp/{variant_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# อ่านไฟล์ .VCF
def read_vcf(file_path):
    vcf_reader = vcf.Reader(open(file_path, 'r'))
    variants = []
    for record in vcf_reader:
        variants.append(record)
    return variants

# วิเคราะห์ข้อมูลและประเมินความเสี่ยง
def analyze_variants(variants):
    amd_snps = ['rs10490924', 'rs1061170']
    results = []

    for variant in variants:
        if variant.ID in amd_snps:
            clinvar_info = get_clinvar_info(variant.ID)
            if clinvar_info:
                results.append({
                    'SNP': variant.ID,
                    'ClinVar': clinvar_info,
                    'Genotype': variant.genotype('Sample1').data.GT
                })
    return results

# หน้าหลักของแอป
def main():
    st.title('VCF File Analysis')

    # สร้างโฟลเดอร์ uploads หากไม่มี
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    uploaded_file = st.file_uploader("Upload VCF file", type=["vcf"])
    if uploaded_file is not None:
        # บันทึกไฟล์
        file_path = os.path.join('uploads', uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.read())

        # อ่านไฟล์ VCF และวิเคราะห์ข้อมูล
        variants = read_vcf(file_path)
        results = analyze_variants(variants)

        # ประเมินความเสี่ยง
        risk = "No risk detected"
        for result in results:
            if result['Genotype'] in ['1/1', '1/0', '0/1']:
                risk = "At risk"
                break

        # แสดงผลลัพธ์
        st.subheader("Analysis Results:")
        st.write(f"Risk Assessment: {risk}")
        st.write("Details:")
        for result in results:
            st.write(f"- SNP: {result['SNP']}")
            st.write(f"  ClinVar Info: {result['ClinVar']}")
            st.write(f"  Genotype: {result['Genotype']}")

if __name__ == '__main__':
    main()
