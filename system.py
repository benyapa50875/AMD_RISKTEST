import streamlit as st
import vcf
import requests

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
    amd_snps = ['rs10490924', 'rs1061170']  # SNP ที่เกี่ยวข้องกับโรค AMD
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

# หน้าหลักของแอป Streamlit
def main():
    st.title('AMD Risk Assessment Tool')

    uploaded_file = st.file_uploader("Upload VCF File", type=['vcf', 'txt'])

    if uploaded_file is not None:
        # บันทึกไฟล์ที่อัปโหลด
        with open('uploaded.vcf', 'wb') as f:
            f.write(uploaded_file.getvalue())

        st.write("File uploaded successfully.")

        # อ่านไฟล์ .VCF และประมวลผล
        variants = read_vcf('uploaded.vcf')
        results = analyze_variants(variants)

        # ประเมินความเสี่ยง
        risk = "No risk detected"
        for result in results:
            if result['Genotype'] in ['1/1', '1/0', '0/1']:
                risk = "At risk"

        # แสดงผลลัพธ์
        st.write(f"Risk: {risk}")
        st.write("Details:")
        st.write(results)

if __name__ == '__main__':
    main()
