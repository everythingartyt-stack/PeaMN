import streamlit as st
import pandas as pd
import time

st.title("⚡ ระบบติดตามงานไฟฟ้าขัดข้อง")
st.write("หน้าจอแสดงผลและติดตามสถานะงานล่าสุดจาก Google Sheets")

# 🎯 ปุ่มอัปเดตสถานะงานทั้งหมดไว้ด้านบนสุด กดทีเดียวดึงค่าใหม่ให้ทุกแถวพร้อมกัน
if st.button("🔄 คลิกเพื่ออัปเดตสถานะงานทั้งหมด", use_container_width=True):
    with st.spinner("กำลังดึงข้อมูลล่าสุดจาก Google Sheets..."):
        # ล้างแคชหน้าเว็บเพื่อบังคับให้แอปดึงค่าใหม่ล่าสุดทันที
        st.cache_data.clear()
        time.sleep(1.0)
        st.rerun()

st.divider()

# 🎯 เพิ่มปุ่มตัวเลือกสำหรับกรองดูสถานะงาน (กดเลือกสลับดูได้ทันที)
filter_option = st.radio(
    "🔍 เลือกรูปแบบการแสดงผลรายงาน:",
    ["ดูงานทั้งหมด", "ดูเฉพาะงานที่ยังไม่แก้ไข 🔴", "ดูเฉพาะงานที่แก้ไขแล้ว 🟢"],
    horizontal=True # แสดงผลเป็นแนวนอนเรียงกันสวยงาม
)

st.divider()
st.subheader("📋 รายการแจ้งเหตุและสถานะปัจจุบัน")

# ฟังก์ชันดึงข้อมูลจาก Google Sheets (ฐานหลักดั้งเดิม ดึงสดเรียลไทม์ทะลวง Cache)
def get_latest_data():
    spreadsheet_id = "10LJJzAoMcWfWnkcZrlEEyhogIEfmnoGzx7QsgG_2yg4"
    # เติมตัวแปรเวลาสุ่มท้ายลิงก์เพื่อทลาย Cache ของ Google บังคับดึงข้อมูลล่าสุด
    csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=Sheet1&t={int(time.time())}"
    
    df_raw = pd.read_csv(csv_url)
    df_raw.columns = df_raw.columns.str.strip()
    return df_raw.fillna("")

try:
    df = get_latest_data()
except Exception as e:
    st.error("❌ ระบบดึงข้อมูลขัดข้อง: กรุณาตรวจสอบสิทธิ์การแชร์ Google Sheets")
    st.stop()

if df.empty:
    st.warning("⚠️ ไม่พบข้อมูลในแท็บ Sheet1 กรุณาตรวจสอบข้อมูลใน Google Sheets")
else:
    id_col = "ลำดับที่" if "ลำดับที่" in df.columns else df.columns[0]
    detail_col = "รายละเอียด" if "รายละเอียด" in df.columns else df.columns[1]
    phone_col = "เบอร์โทร" if "เบอร์โทร" in df.columns else df.columns[2]
    status_col = "สถานะ" if "สถานะ" in df.columns else df.columns[3]

    # วนลูปแสดงผลรายการทั้งหมดแบบอัตโนมัติ
    for index, row in df.iterrows():
        try:
            job_id = str(row[id_col]).strip()
            if job_id == "" or job_id == "nan":
                continue
            if "." in job_id:
                job_id = str(int(float(job_id)))
        except:
            continue
            
        job_detail = str(row[detail_col]).strip()
        phone_val = str(row[phone_col]).strip()
        
        # คัดกรองเงื่อนไขพื้นฐาน: ถ้าคอลัมน์รายละเอียด และ คอลัมน์เบอร์โทร ว่างทั้งคู่ จะไม่โชว์บนหน้าเว็บ
        if (job_detail == "" or job_detail == "nan") and (phone_val == "" or phone_val == "nan" or phone_val == "0.0" or phone_val == "0"):
            continue
            
        # ดึงข้อความสถานะในคอลัมน์ D มาตรวจสอบเพื่อใส่สัญลักษณ์วงกลมสี
        current_status = str(row[status_col]).strip()
        
        # เช็กสถานะจริงจากชีตเพื่อเตรียมแสดงผล
        if current_status == "แก้ไขแล้ว" or "เสร็จ" in current_status:
            is_job_done = True
            status_display = "🟢 แก้ไขแล้ว"
        else:
            is_job_done = False
            status_display = "🔴 ยังไม่แก้ไข"
        
        # 🎯 เงื่อนไขตัวกรองปุ่มเลือก: คัดแยกแถวที่ไม่ตรงกับที่เลือกออกไป
        if filter_option == "ดูเฉพาะงานที่ยังไม่แก้ไข 🔴" and is_job_done:
            continue # ถ้าเลือกดูงานค้าง แต่งานนี้เสร็จแล้ว -> ให้ข้ามไป ไม่ต้องโชว์
        elif filter_option == "ดูเฉพาะงานที่แก้ไขแล้ว 🟢" and not is_job_done:
            continue # ถ้าเลือกดูงานเสร็จ แต่งานนี้ยังไม่เสร็จ -> ให้ข้ามไป ไม่ต้องโชว์
            
        with st.container():
            # โชว์ข้อความสถานะพร้อมวงกลมสีไว้ข้างๆ เลขลำดับนอกปุ่ม
            st.write(f"**ลำดับที่ {job_id}** | สถานะ: **{status_display}**")
            st.write(f"📌 {job_detail}")
            
            if phone_val != "" and phone_val != "nan" and phone_val != "0.0" and phone_val != "0":
                st.write(f"📞 เบอร์โทร: {phone_val}")
                        
        st.divider()
