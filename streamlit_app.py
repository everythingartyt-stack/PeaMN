import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ลบ st.set_page_config ออกไปเลย เพื่อตัดปัญหา Python 3.14 บนคลาวด์มองว่ามีอะไรทำงานก่อนหน้า

st.title("⚡ ระบบติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# เชื่อมต่อกับ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ฟังก์ชันดึงข้อมูลล่าสุด
def get_latest_data():
    df_raw = conn.read(ttl="0")
    df_raw.columns = df_raw.columns.str.strip()
    return df_raw.fillna("")

try:
    df = get_latest_data()
except Exception as e:
    st.error("❌ ไม่สามารถดึงข้อมูลจาก Google Sheets ได้ กรุณาตรวจสอบลิงก์ใน Advanced settings (Secrets)")
    st.stop()

# --- ส่วนที่ 1: ตารางรายการงานพร้อมปุ่มกดอัปเดตสถานะ ---
st.subheader("📋 รายการแจ้งเหตุและจัดการสถานะ")

# ตรวจสอบชื่อคอลัมน์หลักจาก Google Sheets ของคุณ
id_col = "ลำดับที่" if "ลำดับที่" in df.columns else df.columns[0]
detail_col = "รายละเอียด" if "รายละเอียด" in df.columns else df.columns[1]
phone_col = "เบอร์โทร" if "เบอร์โทร" in df.columns else df.columns[2]
status_col = "สถานะ" if "สถานะ" in df.columns else df.columns[3]

# วนลูปแสดงผลทีละแถว
for index, row in df.iterrows():
    job_id = row[id_col]
    current_status = str(row[status_col]).strip()
    
    # ถ้าสถานะว่างเปล่า ให้ตั้งเป็น รอดำเนินการ
    if current_status == "" or current_status == "nan":
        current_status = "รอดำเนินการ"
        
    status_icon = "✅ เสร็จสิ้น" if current_status == "เสร็จสิ้น" else "⏳ รอดำเนินการ"
    
    # สร้างกล่องข้อความแสดงรายละเอียดงานแต่ละตัว
    with st.container():
        col_text, col_btn = st.columns([3, 1])
        
        with col_text:
            st.write(f"**ลำดับที่ {job_id}** | สถานะปัจจุบัน: **{status_icon}**")
            st.write(f"📌 {row[detail_col]}")
            if str(row[phone_col]):
                st.write(f"📞 เบอร์โทร: {str(row[phone_col])}")
        
        with col_btn:
            # สลับสถานะปุ่มกด
            if current_status == "เสร็จสิ้น":
                btn_label = "⏳ ปรับเป็นรอดำเนินการ"
                target_status = "รอดำเนินการ"
            else:
                btn_label = "✅ ปรับเป็นเสร็จสิ้น"
                target_status = "เสร็จสิ้น"
                
            if st.button(btn_label, key=f"btn_{job_id}_{index}"):
                with st.spinner("กำลังบันทึก..."):
                    df_latest = get_latest_data()
                    df_latest.loc[df_latest[id_col].astype(str) == str(job_id), status_col] = target_status
                    conn.update(data=df_latest)
                    st.success("อัปเดตเรียบร้อย!")
                    st.rerun()
    st.divider()
