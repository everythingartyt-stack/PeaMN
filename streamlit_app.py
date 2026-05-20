import streamlit as st
import pandas as pd
import requests
import time

st.title("⚡ ระบบติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# ฟังก์ชันดึงข้อมูลจาก Google Sheets (ฐานหลักตัวที่ทำงานได้ดีที่สุด)
def get_latest_data():
    spreadsheet_id = "10LJJzAoMcWfWnkcZrlEEyhogIEfmnoGzx7QsgG_2yg4"
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
    st.warning("⚠️ 不พบข้อมูลในแท็บ Sheet1 กรุณาตรวจสอบข้อมูลใน Google Sheets")
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
        
        # ปรับการเช็กคำสถานะให้ตรงกับโครงสร้าง Google Sheets ของน้า
        if current_status == "" or current_status == "nan" or current_status == "0" or current_status == "รอดำเนินการ":
            is_completed = False
            status_icon = "⏳ รอดำเนินการ"
        else:
            is_completed = True
            status_icon = "✅ เสร็จสิ้น"
        
        with st.container():
            col_text, col_status_display = st.columns([3, 1])
            
            with col_text:
                st.write(f"**ลำดับที่ {job_id}** | สถานะปัจจุบัน: **{status_icon}**")
                st.write(f"📌 {row[detail_col]}")
                
                phone_val = str(row[phone_col]).strip()
                if phone_val != "" and phone_val != "nan" and phone_val != "0.0" and phone_val != "0":
                    st.write(f"📞 เบอร์โทร: {phone_val}")
            
            with col_status_display:
                # ปุ่มอัปเดตสถานะ
                if st.button("อัปเดตสถานะ", key=f"btn_{job_id}_{index}"):
                    # 🟢 แก้ไขตรงนี้: ส่งคำว่า "ดำเนินการเสร็จสิ้น" หรือ "รอดำเนินการ" ให้ตรงกับช้อยส์ในฟอร์มของน้าเป๊ะๆ
                    target_status = "รอดำเนินการ" if is_completed else "ดำเนินการเสร็จสิ้น"
                    payload = {ID_ENTRY: str(job_id), STATUS_ENTRY: target_status}
                    
                    with st.spinner("กำลังบันทึก..."):
                        try:
                            requests.post(FORM_URL, data=payload, timeout=5)
                        except:
                            pass
                        time.sleep(1.5)
                        st.rerun()

                # เลือกโชว์แค่กล่องสีเดียวค้างไว้ตามสถานะปัจจุบัน
                if is_completed:
                    st.success("ดำเนินการเสร็จสิ้น!")
                else:
                    st.error("รอดำเนินการ")
                    
        st.divider()
