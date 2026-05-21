import streamlit as st
import pandas as pd
import time

st.title("⚡ ระบบติดตามงานไฟฟ้าขัดข้อง")
st.write("หน้าจอแสดงผลและติดตามสถานะงานล่าสุดจาก Google Sheets")

# 🎯 ปุ่มอัปเดตเวอร์ชันกระชับสั้น ด้านบนสุด
if st.button("🔄 อัปเดต", use_container_width=True):
    with st.spinner("กำลังดึงข้อมูลล่าสุดจาก Google Sheets..."):
        st.cache_data.clear()
        time.sleep(1.0)
        st.rerun()

st.divider()

# ปุ่มตัวเลือกสำหรับกรองดูสถานะงาน
filter_option = st.radio(
    "🔍 เลือกรูปแบบการแสดงผลรายงาน:",
    ["ดูงานทั้งหมด", "ดูเฉพาะงานที่ยังไม่แก้ไข 🔴", "ดูเฉพาะงานที่แก้ไขแล้ว 🟢"],
    horizontal=True
)

st.divider()
st.subheader("📋 รายการแจ้งเหตุและสถานะปัจจุบัน")

# ฟังก์ชันดึงข้อมูลแบบทะลวง Cache ปรับปรุงตัวดักจับข้อมูลขยะขัดข้อง
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
            # ตัดเศษทศนิยมที่อาจเกิดขึ้นจากระบบล็อกคอลัมน์ออกไป (.0)
            if "." in job_id:
                job_id = str(int(float(job_id)))
            if job_id == "" or job_id == "nan":
                continue
        except:
            continue
            
        job_detail = str(row[detail_col]).strip()
        phone_val = str(row[phone_col]).strip()
        
        # ตัวดักจับช่องว่าง: ล้างค่าตัวอักษรขยะและคำแฝงออกทั้งหมดก่อนเช็ค เพื่อซ่อนแถวว่างอัตโนมัติ
        check_detail = job_detail.lower().replace("nan", "").replace(".0", "").strip()
        check_phone = phone_val.lower().replace("nan", "").replace(".0", "").replace("0", "").strip()
        
        # หากทั้งช่องรายละเอียดและเบอร์โทรไม่มีข้อความอยู่เลย ให้ข้ามบรรทัดนี้ไปทันทีไม่เอามาโชว์
        if check_detail == "" and check_phone == "":
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
        
        # เงื่อนไขตัวกรองปุ่มเลือกสลับโหมดการดูงาน
        if filter_option == "ดูเฉพาะงานที่ยังไม่แก้ไข 🔴" and is_job_done:
            continue
        elif filter_option == "ดูเฉพาะงานที่แก้ไขแล้ว 🟢" and not is_job_done:
            continue
            
        with st.container():
            st.write(f"**ลำดับที่ {job_id}** | สถานะ: **{status_display}**")
            st.write(f"📌 {job_detail}")
            
            # ล้างเงื่อนไขการโชว์เบอร์โทรไม่ให้ดึงเลขศูนย์เดี่ยวหรือค่าว่างขึ้นมาแสดงผล
            if check_phone != "":
                st.write(f"📞 เบอร์โทร: {phone_val}")
            
            # 🎯 ปุ่มลิงก์ทางลัดของน้า กดแล้ววาร์ปไปเปิดหน้า Google Sheets เพื่อเปลี่ยนสถานะได้ทันที
            st.link_button(
                "📝 กดเปิดเพื่อเปลี่ยนสถานะใน Google Sheets", 
                "https://docs.google.com/spreadsheets/d/10LJJzAoMcWfWnkcZrlEEyhogIEfmnoGzx7QsgG_2yg4/edit", 
                use_container_width=True
            )
                        
        st.divider()
