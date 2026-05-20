import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection

st.title("⚡ ระบบติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# เชื่อมต่อกับ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_latest_data():
    # บังคับดึงข้อมูลสดใหม่เสมอ (ttl=0)
    df_raw = conn.read(ttl=0)
    # ล้างช่องว่างที่หัวคอลัมน์ทั้งหมด
    df_raw.columns = df_raw.columns.str.strip()
    return df_raw.fillna("")

try:
    df = get_latest_data()
except Exception as e:
    st.error("❌ ไม่สามารถดึงข้อมูลได้ กรุณาตรวจสอบลิงก์ใน Advanced settings")
    st.stop()

st.subheader("📋 รายการแจ้งเหตุและจัดการสถานะ")

# ตรวจสอบตัวตารางข้อมูล
if df.empty:
    st.warning("⚠️ ไม่พบข้อมูลใน Google Sheets กรุณาตรวจสอบแท็บหน้างานหลักของคุณ")
else:
    # ระบุชื่อคอลัมน์ให้ตรงตามภาพถ่ายจริงของคุณ
    id_col = "ลำดับที่"
    detail_col = "รายละเอียด"
    phone_col = "เบอร์โทร"
    status_col = "สถานะ"

    # ลิงก์ฟอร์มของคุณ
    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd7tiGJnN9bnwOU9ZHToWeF2_M8GBGYKXbWvlgt9jWhD-A5WQ/formResponse"
    ID_ENTRY = "entry.1773581682"
    STATUS_ENTRY = "entry.1603121761"

    # วนลูปแสดงผลรายการทั้งหมด 1-20
    for index, row in df.iterrows():
        # ตรวจสอบว่าคอลัมน์ "ลำดับที่" มีตัวเลขไหม (ดึงเฉพาะแถวที่มีข้อมูลจริง)
        try:
            job_id = str(row[id_col]).strip()
            if job_id == "" or job_id == "nan":
                continue
        except:
            continue
            
        # ดึงสถานะปัจจุบันจากช่อง D
        current_status = str(row[status_col]).strip()
        
        # จัดการคำและค่าว่าง
        if current_status == "" or current_status == "nan" or current_status == "0":
            current_status = "รอดำเนินการ"
            
        status_icon = "✅ เสร็จสิ้น" if current_status == "เสร็จสิ้น" else "⏳ รอดำเนินการ"
        
        # แสดงผลกล่องข้อมูลแต่ละรายการ
        with st.container():
            col_text, col_btn = st.columns([3, 1])
            with col_text:
                st.write(f"**ลำดับที่ {job_id}** | สถานะปัจจุบัน: **{status_icon}**")
                st.write(f"📌 {row[detail_col]}")
                
                # แสดงเบอร์โทร (ถ้ามีข้อมูล)
                phone_val = str(row[phone_col]).strip()
                if phone_val != "" and phone_val != "nan" and phone_val != "0.0" and phone_val != "0":
                    st.write(f"📞 เบอร์โทร: {phone_val}")
            
            with col_btn:
                # ตั้งสลับข้อความบนปุ่ม
                if current_status == "เสร็จสิ้น":
                    btn_label = "⏳ ปรับเป็นรอดำเนินการ"
                    target_status = "รอดำเนินการ"
                else:
                    btn_label = "✅ ปรับเป็นเสร็จสิ้น"
                    target_status = "เสร็จสิ้น"
                    
                if st.button(btn_label, key=f"btn_{job_id}_{index}"):
                    with st.spinner("กำลังบันทึกสถานะ..."):
                        payload = {ID_ENTRY: str(job_id), STATUS_ENTRY: target_status}
                        try:
                            # ส่งสัญญานไปที่ Google Form
                            requests.post(FORM_URL, data=payload)
                            st.success("อัปเดตเรียบร้อย!")
                            st.rerun()
                        except:
                            st.error("การส่งข้อมูลขัดข้อง กรุณาลองใหม่อีกครั้ง")
        st.divider()
