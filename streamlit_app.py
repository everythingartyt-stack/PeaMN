import streamlit as st
import pandas as pd
import requests
import time

st.title("⚡ ระบบติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# ฟังก์ชันดึงข้อมูลจาก Google Sheets (Sheet1)
def get_latest_data():
    base_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    if "/edit" in base_url:
        spreadsheet_id = base_url.split("/d/")[1].split("/edit")[0]
    else:
        spreadsheet_id = base_url.split("/d/")[1].split("?")[0]
        
    csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=Sheet1"
    
    df_raw = pd.read_csv(csv_url)
    df_raw.columns = df_raw.columns.str.strip()
    return df_raw.fillna("")

try:
    df = get_latest_data()
except Exception as e:
    st.error("❌ ระบบดึงข้อมูลขัดข้อง: กรุณาตรวจสอบว่าลิงก์ใน Advanced settings (Secrets) ถูกต้องหรือไม่")
    st.stop()

st.subheader("📋 รายการแจ้งเหตุและจัดการสถานะ")

if df.empty:
    st.warning("⚠️ ไม่พบข้อมูลในแท็บ Sheet1 กรุณาตรวจสอบข้อมูลใน Google Sheets")
else:
    id_col = "ลำดับที่" if "ลำดับที่" in df.columns else df.columns[0]
    detail_col = "รายละเอียด" if "รายละเอียด" in df.columns else df.columns[1]
    phone_col = "เบอร์โทร" if "เบอร์โทร" in df.columns else df.columns[2]
    status_col = "สถานะ" if "สถานะ" in df.columns else df.columns[3]

    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd7tiGJnN9bnwOU9ZHToWeF2_M8GBGYKXbWvlgt9jWhD-A5WQ/formResponse"
    ID_ENTRY = "entry.1773581682"
    STATUS_ENTRY = "entry.1603121761"

    # วนลูปแสดงผลรายการทั้งหมด
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
            col_text, col_btn = st.columns([3, 1])
            with col_text:
                st.write(f"**ลำดับที่ {job_id}** | สถานะปัจจุบัน: **{status_icon}**")
                st.write(f"📌 {row[detail_col]}")
                
                phone_val = str(row[phone_col]).strip()
                if phone_val != "" and phone_val != "nan" and phone_val != "0.0" and phone_val != "0":
                    st.write(f"📞 เบอร์โทร: {phone_val}")
            
            with col_btn:
                # ระบบคำนวณสถานะสลับค่าไปมา
                if current_status == "เสร็จสิ้น":
                    target_status = "รอดำเนินการ"
                    success_message = f"🟢 ลำดับที่ {job_id} เปลี่ยนสถานะเป็น: [รอดำเนินการ] เรียบร้อยแล้ว! (กำลังอัปเดตฐานข้อมูล)"
                else:
                    target_status = "เสร็จสิ้น"
                    success_message = f"🟢 ลำดับที่ {job_id} เปลี่ยนสถานะเป็น: [ดำเนินการเสร็จสิ้น!] เรียบร้อยแล้ว! (กำลังอัปเดตฐานข้อมูล)"
                
                # ปุ่มอัปเดตสถานะ
                if st.button("อัปเดตสถานะ", key=f"btn_{job_id}_{index}"):
                    with st.spinner("กำลังส่งข้อมูล..."):
                        payload = {ID_ENTRY: str(job_id), STATUS_ENTRY: target_status}
                        
                        for attempt in range(3):
                            try:
                                requests.post(FORM_URL, data=payload, timeout=5)
                                # 💡 ค้างกล่องเขียวโชว์สถานะไว้ด้านบนสุดจนกว่าจะกดปิด เพื่อให้เวลา Google ชีตอัปเดตค่า
                                st.toast(success_message, icon="⚡")
                                time.sleep(1.5) # หน่วงเวลาให้ Google Sheets บันทึกค่าเรียบร้อย
                                st.rerun()
                                break
                            except requests.exceptions.RequestException:
                                if attempt == 2:
                                    st.error("สัญญาณเครือข่ายขัดข้อง กรุณาลองใหม่อีกครั้ง")
                                time.sleep(1)
        st.divider()
