import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection

st.title("⚡ ระบบติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# เชื่อมต่อกับ Google Sheets สำหรับอ่านข้อมูล
conn = st.connection("gsheets", type=GSheetsConnection)

def get_latest_data():
    df_raw = conn.read(ttl="0")
    df_raw.columns = df_raw.columns.str.strip()
    return df_raw.fillna("")

try:
    df = get_latest_data()
except Exception as e:
    st.error("❌ ไม่สามารถดึงข้อมูลได้ กรุณาตรวจสอบลิงก์ใน Advanced settings")
    st.stop()

st.subheader("📋 รายการแจ้งเหตุและจัดการสถานะ")

# ตรวจสอบชื่อคอลัมน์หลักจาก Google Sheets
id_col = "ลำดับที่" if "ลำดับที่" in df.columns else df.columns[0]
detail_col = "รายละเอียด" if "รายละเอียด" in df.columns else df.columns[1]
phone_col = "เบอร์โทร" if "เบอร์โทร" in df.columns else df.columns[2]
status_col = "สถานะ" if "สถานะ" in df.columns else df.columns[3]

# 🔗 ลิงก์และรหัสกล่องข้อความจาก Google Form ของคุณ
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd7tiGJnN9bnwOU9ZHToWeF2_M8GBGYKXbWvlgt9jWhD-A5WQ/formResponse"
ID_ENTRY = "entry.1773581682"
STATUS_ENTRY = "entry.1603121761"

# วนลูปแสดงผลทีละแถว
for index, row in df.iterrows():
    job_id = row[id_col]
    current_status = str(row[status_col]).strip()
    
    # ถ้าสถานะว่างเปล่า หรือดึงสูตรมาแล้วยังไม่มีค่า ให้ถือว่าเป็น รอดำเนินการ
    if current_status == "" or current_status == "nan" or current_status == "0":
        current_status = "รอดำเนินการ"
        
    status_icon = "✅ เสร็จสิ้น" if current_status == "เสร็จสิ้น" else "⏳ รอดำเนินการ"
    
    with st.container():
        col_text, col_btn = st.columns([3, 1])
        with col_text:
            st.write(f"**ลำดับที่ {job_id}** | สถานะปัจจุบัน: **{status_icon}**")
            st.write(f"📌 {row[detail_col]}")
            if str(row[phone_col]) and str(row[phone_col]) != "nan":
                st.write(f"📞 เบอร์โทร: {str(row[phone_col])}")
        
        with col_btn:
            if current_status == "เสร็จสิ้น":
                btn_label = "⏳ ปรับเป็นรอดำเนินการ"
                target_status = "รอดำเนินการ"
            else:
                btn_label = "✅ ปรับเป็นเสร็จสิ้น"
                target_status = "เสร็จสิ้น"
                
            if st.button(btn_label, key=f"btn_{job_id}_{index}"):
                with st.spinner("กำลังบันทึกสถานะ..."):
                    # ยิงข้อมูลส่งหลังบ้านผ่าน Google Form
                    payload = {ID_ENTRY: str(job_id), STATUS_ENTRY: target_status}
                    try:
                        # ใช้ requests ยิงฟอร์ม
                        response = requests.post(FORM_URL, data=payload)
                        st.success("อัปเดตเรียบร้อย!")
                        st.rerun()
                    except:
                        st.error("การส่งข้อมูลขัดข้อง กรุณาลองใหม่อีกครั้ง")
    st.divider()
