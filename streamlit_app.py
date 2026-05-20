import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection

st.title("⚡ ระบบติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# เชื่อมต่อกับ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_latest_data():
    # สั่งให้เจาะจงอ่านจากแท็บแรก หรือระบุชื่อแท็บงานหลักของคุณ (เช่น worksheet="Sheet1" หรือชื่อแท็บของคุณ)
    # ในที่นี้ใส่เป็นแผ่นงานแรกลงไปก่อน เพื่อความถูกต้อง
    df_raw = conn.read(ttl="0")
    
    # ล้างช่องว่างที่หัวคอลัมน์ทั้งหมด
    df_raw.columns = df_raw.columns.str.strip()
    return df_raw.fillna("")

try:
    df = get_latest_data()
except Exception as e:
    st.error("❌ ไม่สามารถดึงข้อมูลได้ กรุณาตรวจสอบลิงก์ใน Advanced settings")
    st.stop()

st.subheader("📋 รายการแจ้งเหตุและจัดการสถานะ")

# ถ้าพบว่าดึงมาแล้วไม่มีข้อมูล ให้แจ้งเตือนผู้ใช้
if df.empty:
    st.warning("⚠️ ไม่พบข้อมูลใน Google Sheets กรุณาตรวจสอบว่ามีข้อมูลอยู่ในแผ่นงานหลักหรือไม่")
else:
    # ค้นหาชื่อคอลัมน์ที่แท้จริง
    id_col = "ลำดับที่" if "ลำดับที่" in df.columns else df.columns[0]
    detail_col = "รายละเอียด" if "รายละเอียด" in df.columns else df.columns[1]
    phone_col = "เบอร์โทร" if "เบอร์โทร" in df.columns else df.columns[2]
    status_col = "สถานะ" if "สถานะ" in df.columns else df.columns[3]

    # 🔗 ลิงก์ฟอร์มของคุณ
    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd7tiGJnN9bnwOU9ZHToWeF2_M8GBGYKXbWvlgt9jWhD-A5WQ/formResponse"
    ID_ENTRY = "entry.1773581682"
    STATUS_ENTRY = "entry.1603121761"

    # วนลูปแสดงผลรายการทั้งหมด
    for index, row in df.iterrows():
        job_id = row[id_col]
        
        # ป้องกันกรณีลำดับที่ไม่มีข้อมูล
        if str(job_id).strip() == "":
            continue
            
        current_status = str(row[status_col]).strip()
        
        # คัดกรองสถานะ
        if current_status == "" or current_status == "nan" or current_status == "0":
            current_status = "รอดำเนินการ"
            
        status_icon = "✅ เสร็จสิ้น" if current_status == "เสร็จสิ้น" else "⏳ รอดำเนินการ"
        
        with st.container():
            col_text, col_btn = st.columns([3, 1])
            with col_text:
                st.write(f"**ลำดับที่ {job_id}** | สถานะปัจจุบัน: **{status_icon}**")
                st.write(f"📌 {row[detail_col]}")
                if str(row[phone_col]) and str(row[phone_col]) != "nan" and str(row[phone_col]) != "0":
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
                        payload = {ID_ENTRY: str(job_id), STATUS_ENTRY: target_status}
                        try:
                            requests.post(FORM_URL, data=payload)
                            st.success("อัปเดตเรียบร้อย!")
                            st.rerun()
                        except:
                            st.error("การส่งข้อมูลขัดข้อง กรุณาลองใหม่อีกครั้ง")
        st.divider()
