import streamlit as st
import pandas as pd
import requests
import time
from streamlit_gsheets import GSheetsConnection

st.title("⚡ ระบบติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# 1. ใช้ระบบเชื่อมต่อ gsheets สากลเพื่อความเสถียรสูงสุด
conn = st.connection("gsheets", type=GSheetsConnection)

def get_latest_data():
    # บังคับดึงค่าสดใหม่เรียลไทม์ (ttl=0) ทะลวงทุกระบบจำของเว็บ
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

    # ลิงก์ฟอร์มหลังบ้านของน้า
    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd7tiGJnN9bnwOU9ZHToWeF2_M8GBGYKXbWvlgt9jWhD-A5WQ/formResponse"
    
    # รหัส Entry ID ทั้ง 3 ช่องที่ตรงล็อก 100%
    ID_ENTRY = "entry.1773581682"
    DETAIL_ENTRY = "entry.1603121761"
    STATUS_ENTRY = "entry.541799838"

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
        job_detail = str(row[detail_col]).strip()
        
        # เช็กคำสถานะจริงจากในตารางกูเกิลชีต
        if "ดำเนินการเสร็จสิ้น" in current_status or "เสร็จสิ้น" in current_status:
            is_completed = True
            status_icon = "✅ เสร็จสิ้น"
        else:
            is_completed = False
            status_icon = "⏳ รอดำเนินการ"
        
        with st.container():
            col_text, col_status_display = st.columns([3, 1])
            
            with col_text:
                st.write(f"**ลำดับที่ {job_id}** | สถานะปัจจุบัน: **{status_icon}**")
                st.write(f"📌 {job_detail}")
                
                phone_val = str(row[phone_col]).strip()
                if phone_val != "" and phone_val != "nan" and phone_val != "0.0" and phone_val != "0":
                    st.write(f"📞 เบอร์โทร: {phone_val}")
            
            with col_status_display:
                # ปุ่มอัปเดตสถานะ
                if st.button("อัปเดตสถานะ", key=f"btn_{job_id}_{index}"):
                    target_status = "รอดำเนินการ" if is_completed else "ดำเนินการเสร็จสิ้น"
                    payload = {
                        ID_ENTRY: str(job_id),
                        DETAIL_ENTRY: job_detail,
                        STATUS_ENTRY: target_status
                    }
                    
                    with st.spinner("กำลังบันทึก..."):
                        try:
                            # ยิงข้อมูลเข้าฟอร์ม
                            requests.post(FORM_URL, data=payload, timeout=5)
                        except:
                            pass
                        
                        # 🚨 จุดตายสำคัญ: สั่งระเบิดล้างแคชหน้าเว็บทิ้งทันที เพื่อบังคับให้ดึงค่าล่าสุดมาแสดงผล
                        st.cache_data.clear()
                        time.sleep(1.5)
                        st.rerun()

                # บังคับแสดงผลแค่ 1 กล่องสถานะเดี่ยว ๆ ต่อครั้งฝั่งขวามือ
                if is_completed:
                    st.success("ดำเนินการเสร็จสิ้น!")
                else:
                    st.error("รอดำเนินการ")
                    
        st.divider()
