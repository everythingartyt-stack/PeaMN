import streamlit as st
import pandas as pd
import requests
import time

st.title("⚡ ระบบติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# ฟังก์ชันดึงข้อมูลจาก Google Sheets (ฐานหลักดั้งเดิมตัวที่ทำงานได้ดีที่สุดและดึงสดเรียลไทม์)
def get_latest_data():
    spreadsheet_id = "10LJJzAoMcWfWnkcZrlEEyhogIEfmnoGzx7QsgG_2yg4"
    # เติมตัวแปรเวลาสุ่มท้ายลิงก์เพื่อทลาย Cache ของ Google บังคับดึงข้อมูลล่าสุดร้อยเปอร์เซ็นต์
    csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=Sheet1&t={int(time.time())}"
    
    df_raw = pd.read_csv(csv_url)
    df_raw.columns = df_raw.columns.str.strip()
    return df_raw.fillna("")

try:
    df = get_latest_data()
except Exception as e:
    st.error("❌ ระบบดึงข้อมูลขัดข้อง: กรุณาตรวจสอบสิทธิ์การแชร์ Google Sheets")
    st.stop()

st.subheader("📋 รายการแจ้งเหตุและจัดการสถานะ")

if df.empty:
    st.warning("⚠️ ไม่พบข้อมูลในแท็บ Sheet1 กรุณาตรวจสอบข้อมูลใน Google Sheets")
else:
    id_col = "ลำดับที่" if "ลำดับที่" in df.columns else df.columns[0]
    detail_col = "รายละเอียด" if "รายละเอียด" in df.columns else df.columns[1]
    phone_col = "เบอร์โทร" if "เบอร์โทร" in df.columns else df.columns[2]
    status_col = "สถานะ" if "สถานะ" in df.columns else df.columns[3]

    # ลิงก์ยิงข้อมูลเข้าหลังบ้าน Google Form ของน้า
    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd7tiGJnN9bnwOU9ZHToWeF2_M8GBGYKXbWvlgt9jWhD-A5WQ/formResponse"
    
    # รหัส Entry ID ทั้ง 3 ช่องจากลิงก์จริงของน้าตรงล็อกร้อยเปอร์เซ็นต์
    ID_ENTRY = "entry.1773581682"       # ช่องลำดับที่
    DETAIL_ENTRY = "entry.1603121761"   # ช่องรายละเอียด
    STATUS_ENTRY = "entry.541799838"     # ช่องสถานะงานจริง

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
        
        # ตรวจเช็กคำสถานะงานที่ดึงมาจากคอลัมน์ D ในตารางชีตของน้า
        if "ดำเนินการเสร็จสิ้น" in current_status or "เสร็จสิ้น" in current_status:
            is_completed = True
            status_icon = "✅ เสร็จสิ้น"
            button_label = "🔄 สลับเป็นรอดำเนินการ"  # ข้อความบนปุ่มเมื่อเสร็จแล้ว
        else:
            is_completed = False
            status_icon = "⏳ รอดำเนินการ"
            button_label = "🟢 คลิกเพื่อเสร็จงาน"      # ข้อความบนปุ่มเมื่อยังไม่เสร็จ
        
        with st.container():
            col_text, col_status_display = st.columns([3, 1])
            
            with col_text:
                st.write(f"**ลำดับที่ {job_id}** | สถานะปัจจุบัน: **{status_icon}**")
                st.write(f"📌 {job_detail}")
                
                phone_val = str(row[phone_col]).strip()
                if phone_val != "" and phone_val != "nan" and phone_val != "0.0" and phone_val != "0":
                    st.write(f"📞 เบอร์โทร: {phone
