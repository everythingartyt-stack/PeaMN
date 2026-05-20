import streamlit as st
import pandas as pd
import requests
import time
from streamlit_gsheets import GSheetsConnection

# 🚨 คำสั่งล้างแคชค้างสะสมชั่วคราว เพื่อแก้ปัญหากล่องเหลืองหน้าว่างเปล่า
st.cache_data.clear()

st.title("⚡ ระบบติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# เชื่อมต่อกับ Google Sheets ผ่าน Secrets ตัวเดิม
conn = st.connection("gsheets", type=GSheetsConnection)

def get_latest_data():
    # ดึงข้อมูลสดใหม่เรียลไทม์ ข้ามทุกระบบจำของเว็บ (ttl=0)
    df_raw = conn.read(ttl=0)
    df_raw.columns = df_raw.columns.str.strip()
    return df_raw.fillna("")

try:
    df = get_latest_data()
except Exception as e:
    st.error("❌ ไม่สามารถดึงข้อมูลได้ กรุณาตรวจสอบลิงก์ Google Sheets ในระบบ Advanced settings (Secrets)")
    st.stop()

st.subheader("📋 รายการแจ้งเหตุและจัดการสถานะ")

if df.empty:
    st.warning("⚠️ ไม่พบข้อมูลใน Google Sheets กรุณาตรวจสอบแท็บหน้างานหลักของคุณ")
else:
    id_col = "ลำดับที่" if "ลำดับที่" in df.columns else df.columns[0]
    detail_col = "รายละเอียด" if "รายละเอียด" in df.columns else df.columns[1]
    phone_col = "เบอร์โทร" if "เบอร์โทร" in df.columns else df.columns[2]
    status_col = "สถานะ" if "สถานะ" in df.columns else df.columns[3]

    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd7tiGJnN9bnwOU9ZHToWeF2_M8GBGYKXbWvlgt9jWhD-A5WQ/formResponse"
    ID_ENTRY = "entry.1773581682"
    STATUS_ENTRY = "entry.1603121761"

    # วนลูปแสดงผลรายการทั้งหมด 1-20
    for index, row in df.iterrows():
        try:
            job_id = str(row[id_col]).strip()
            if job_id == "" or job_id == "nan":
                continue
            if "." in job_id:
                job_id = str(int(float(job_id)))
        except:
            continue
            
        current_status = str(row[status_col]).strip()
        if current_status == "" or current_status == "nan" or current_status == "0":
            current_status = "รอดำเนินการ"
            
        status_icon = "✅ เสร็จสิ้น" if current_status == "เสร็จสิ้น" else "⏳ รอดำเนินการ"
        
        with st.container():
            col_text, col_status_display = st.columns([3, 1])
            
            with col_text:
                st.write(f"**ลำดับที่ {job_id}** | สถานะปัจจุบัน: **{status_icon}**")
                st.write(f"📌 {row[detail_col]}")
                
                phone_val = str(row[phone_col]).strip()
                if phone_val != "" and phone_val != "nan" and phone_val != "0.0" and phone_val != "0":
                    st.write(f"📞 เบอร์โทร: {phone_val}")
            
            with col_status_display:
                # 1. ปุ่มกด "อัปเดตสถานะ" สลับค่าไปมา
                if st.button("อัปเดตสถานะ", key=f"btn_{job_id}_{index}"):
                    target_status = "รอดำเนินการ" if current_status == "เสร็จสิ้น" else "เสร็จสิ้น"
                    payload = {ID_ENTRY: str(job_id), STATUS_ENTRY: target_status}
                    
                    with st.spinner("กำลังบันทึกสถานะ..."):
                        try:
                            requests.post(FORM_URL, data=payload, timeout=5)
                        except:
                            pass
                        time.sleep(1.2)
                        st.rerun()

                # 2. กล่องแสดงสถานะค้างถาวรฝั่งขวา (แดง/เขียว) 
                if current_status == "เสร็จสิ้น":
                    st.success("ดำเนินการเสร็จสิ้น!")
                else:
                    st.error("รอดำเนินการ")
                    
        st.divider()                    payload = {ID_ENTRY: str(job_id), STATUS_ENTRY: target_status}
                    
                    with st.spinner("กำลังบันทึกสถานะ..."):
                        try:
                            requests.post(FORM_URL, data=payload, timeout=5)
                        except:
                            pass
                        time.sleep(1.2)
                        st.rerun()

                # 2. กล่องแสดงสถานะค้างถาวรฝั่งขวา (แดง/เขียว) ตามสเปกใหม่ของน้า
                if current_status == "เสร็จสิ้น":
                    st.success("ดำเนินการเสร็จสิ้น!")
                else:
                    st.error("รอดำเนินการ")
                    
        st.divider()
