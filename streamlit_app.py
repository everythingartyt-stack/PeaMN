import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection

st.title("⚡ ระบบติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# เชื่อมต่อกับ Google Sheets สำหรับอ่านข้อมูล (อ่านได้อย่างเดียวไม่มีวันเออเรอร์)
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

id_col = "ลำดับที่" if "ลำดับที่" in df.columns else df.columns[0]
detail_col = "รายละเอียด" if "รายละเอียด" in df.columns else df.columns[1]
phone_col = "เบอร์โทร" if "เบอร์โทร" in df.columns else df.columns[2]
status_col = "สถานะ" if "สถานะ" in df.columns else df.columns[3]

# 🛠️ นำข้อมูลชุดข้อมูลลิงก์จากขั้นตอนที่ 2 มาใส่ตรงนี้ครับ 🛠️
FORM_URL = "https://docs.google.com/forms/d/e/ใส่_ID_ฟอร์มของคุณตรงนี้/formResponse" 
ID_ENTRY = "entry.1234567"  # เปลี่ยนเป็นรหัส entry ID ของคุณ
STATUS_ENTRY = "entry.9876543"  # เปลี่ยนเป็นรหัส entry สถานะของคุณ

for index, row in df.iterrows():
    job_id = row[id_col]
    current_status = str(row[status_col]).strip()
    
    if current_status == "" or current_status == "nan":
        current_status = "รอดำเนินการ"
        
    status_icon = "✅ เสร็จสิ้น" if current_status == "เสร็จสิ้น" else "⏳ รอดำเนินการ"
    
    with st.container():
        col_text, col_btn = st.columns([3, 1])
        with col_text:
            st.write(f"**ลำดับที่ {job_id}** | สถานะปัจจุบัน: **{status_icon}**")
            st.write(f"📌 {row[detail_col]}")
            if str(row[phone_col]):
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
                    # ยิงข้อมูลแอบส่งหลังบ้านผ่าน Google Form API
                    payload = {ID_ENTRY: str(job_id), STATUS_ENTRY: target_status}
                    try:
                        requests.post(FORM_URL, data=payload)
                        st.success("อัปเดตเรียบร้อย!")
                        st.rerun()
                    except:
                        st.error("การส่งข้อมูลขัดข้อง ลองใหม่อีกครั้ง")
    st.divider()
