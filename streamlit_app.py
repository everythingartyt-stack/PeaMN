import streamlit as st
import pandas as pd
import requests
from streamlit_gsheets import GSheetsConnection

st.title("⚡ ระบบติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# เชื่อมต่อกับ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_latest_data():
    # 🚨 สำคัญมาก: เปลี่ยนคำว่า "Sheet1" ให้เป็นชื่อแท็บงานหลักใน Google Sheets ของคุณจริงๆ 🚨
    # เช่น worksheet="แผ่นงาน1" หรือ worksheet="Sheet1" (ต้องพิมพ์ให้ตรงกับชื่อแท็บจริงเป๊ะๆ)
    df_raw = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], worksheet="Sheet1", ttl=0)
    
    # ล้างช่องว่างที่หัวคอลัมน์ทั้งหมด
    df_raw.columns = df_raw.columns.str.strip()
    return df_raw.fillna("")

try:
    df = get_latest_data()
except Exception as e:
    st.error(f"❌ ไม่สามารถดึงข้อมูลได้ กรุณาตรวจสอบว่าชื่อแท็บในโค้ดตรงกับใน Google Sheets หรือไม่ ({str(e)})")
    st.stop()

st.subheader("📋 รายการแจ้งเหตุและจัดการสถานะ")

if df.empty:
    st.warning("⚠️ ไม่พบข้อมูลใน Google Sheets กรุณาตรวจสอบชื่อแท็บงานหลักของคุณ")
else:
    id_col = "ลำดับที่"
    detail_col = "รายละเอียด"
    phone_col = "เบอร์โทร"
    status_col = "สถานะ"

    # 🔗 ลิงก์ฟอร์มของคุณ
    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd7tiGJnN9bnwOU9ZHToWeF2_M8GBGYKXbWvlgt9jWhD-A5WQ/formResponse"
    ID_ENTRY = "entry.1773581682"
    STATUS_ENTRY = "entry.1603121761"

    # วนลูปแสดงผลรายการทั้งหมด 1-20
    for index, row in df.iterrows():
        try:
            job_id = str(row[id_col]).strip()
            if job_id == "" or job_id == "nan":
                continue
            # แปลงเป็นตัวเลขจำนวนเต็มเพื่อความสวยงาม (เช่น 1.0 -> 1)
            job_id = str(int(float(job_id)))
        except:
            continue
            
        current_status = str(row[status_col]).strip()
        if current_status == "" or current_status == "nan" or current_status == "0":
            current_status = "รอดำเนินการ"
            
        status_icon = "✅ เสร็จสิ้น" if current_status == "เสร็จสิ้น" else "⏳ รอดำเนินการ"
        
        with st.container():
            col_text, col_btn = st.columns([3, 1])
            with col_text:
                st.write(f"**ลำดับที่ {job_id}** | สถานะปัจจุบัน: **{status_icon}**")
                st.write(f"📌 {row[detail_col]}")
                
                phone_val = str(row[phone_col]).strip()
                if phone_val != "" and phone_val != "nan" and phone_val != "0.0" and phone_val != "0":
                    st.write(f"📞 เบอร์โทร: {phone_val}")
            
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
