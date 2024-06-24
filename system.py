import streamlit as st
import vcfpy
import requests
import os

# ClinVar API
def get_clinvar_info(variant_id):
    url = f'https://api.ncbi.nlm.nih.gov/variation/v0/beta/refsnp/{variant_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# อ่านไฟล์ .VCF ด้วย vcfpy
def read_vcf(file_path):
    try:
        variants = []
        with vcfpy.Reader.from_path(file_path) as reader:
            for record in reader:
                variants.append(record)
        return variants
    except Exception as e:
        st.error(f"Error reading VCF file: {e}")
        return None

# วิเคราะห์ข้อมูลและประเมินความเสี่ยง
def analyze_variants(variants):
    amd_snps = ['rs10490924', 'rs1061170']
    results = []

    for variant in variants:
        if variant.id in amd_snps:  # ใช้ variant.id แทน variant.ID
            clinvar_info = get_clinvar_info(variant.id)
            if clinvar_info:
                results.append({
                    'SNP': variant.id,
                    'ClinVar': clinvar_info,
                    'Genotype': variant.samples[0].data.get('GT')  # ดึง Genotype จาก sample แรก
                })
    return results

def main():
    st.title('VCF File Analysis')

    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    uploaded_file = st.file_uploader("Upload VCF file", type=["vcf"])
    if uploaded_file is not None:
        # บันทึกไฟล์
        file_path = os.path.join('uploads', uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.read())

        # อ่านไฟล์ VCF ด้วย vcfpy และวิเคราะห์ข้อมูล
        variants = read_vcf(file_path)
        
        if variants is not None:
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
        else:
            st.error("Failed to read VCF file. Please upload a valid VCF file.")

if __name__ == '__main__':
    main()
