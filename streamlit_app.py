import streamlit as st
import pandas as pd

# บรรทัดนี้ต้องอยู่บนสุด ห้ามมีคำสั่ง st. อื่นๆ อยู่ก่อนหน้าเด็ดขาด
st.set_page_config(title="ระบบอัปเดตงานไฟฟ้า", layout="wide")

from streamlit_gsheets import GSheetsConnection

st.title("⚡ แดชบอร์ดติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# เชื่อมต่อกับ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ฟังก์ชันดึงข้อมูลล่าสุด
def get_latest_data():
    df_raw = conn.read(ttl="0")
    # ป้องกันกรณีดึงข้อมูลมาแล้วได้ค่าว่าง หรือพิมพ์หัวคอลัมน์เล็กใหญ่ไม่ตรงกัน
    df_raw.columns = df_raw.columns.str.strip()
    return df_raw.fillna("")

try:
    df = get_latest_data()
except Exception as e:
    st.error("❌ ไม่สามารถดึงข้อมูลจาก Google Sheets ได้ กรุณาตรวจสอบลิงก์ใน Advanced settings (Secrets)")
    st.stop()

# --- ส่วนที่ 1: แดชบอร์ดสรุปภาพรวม (Metrics) ---
st.subheader("📊 สรุปภาพรวมสถานะงาน")
if not df.empty:
    total_jobs = len(df)
    
    # ดักจับชื่อคอลัมน์สถานะ (รองรับทั้งภาษาไทยและอังกฤษ)
    status_col = "สถานะ" if "สถานะ" in df.columns else "status" if "status" in df.columns else None
    
    if status_col:
        # ล้างช่องว่างในข้อมูลสถานะ
        df[status_col] = df[status_col].astype(str).str.strip()
        done_count = len(df[df[status_col] == "เสร็จสิ้น"])
    else:
        done_count = 0
        
    pending_count = total_jobs - done_count

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 งานแจ้งทั้งหมด", f"{total_jobs} รายการ")
    with col2:
        st.metric("⏳ รอดำเนินการ", f"{pending_count} รายการ")
    with col3:
        st.metric("✅ เสร็จสิ้นแล้ว", f"{done_count} รายการ")
    with col4:
        st.metric("💡 อัตราความสำเร็จ", f"{(done_count/total_jobs*100):.1f}%" if total_jobs > 0 else "0%")

st.divider()

# --- ส่วนที่ 2: ตารางรายการงานพร้อมปุ่มกดอัปเดตสถานะ ---
st.subheader("📋 รายการแจ้งเหตุและจัดการสถานะ")

# ตรวจสอบชื่อคอลัมน์หลัก
id_col = "ลำดับที่" if "ลำดับที่" in df.columns else "id" if "id" in df.columns else df.columns[0]
detail_col = "รายละเอียด" if "รายละเอียด" in df.columns else "detail" if "detail" in df.columns else df.columns[1]
phone_col = "เบอร์โทร" if "เบอร์โทร" in df.columns else "phone" if "phone" in df.columns else df.columns[2]
status_col = "สถานะ" if "สถานะ" in df.columns else "status" if "status" in df.columns else df.columns[3]

col_id, col_detail, col_phone, col_status, col_action = st.columns([1, 4, 2, 2, 2])
with col_id: st.markdown("**ลำดับที่**")
with col_detail: st.markdown("**รายละเอียด**")
with col_phone: st.markdown("**เบอร์โทร**")
with col_status: st.markdown("**สถานะปัจจุบัน**")
with col_action: st.markdown("**เปลี่ยนสถานะ**")

st.divider()

for index, row in df.iterrows():
    job_id = row[id_col]
    current_status = str(row[status_col]).strip()
    
    if current_status == "" or current_status == "nan":
        current_status = "รอดำเนินการ"
        
    status_display = "✅ เสร็จสิ้น" if current_status == "เสร็จสิ้น" else "⏳ รอดำเนินการ"
    
    c_id, c_detail, c_phone, c_status, c_action = st.columns([1, 4, 2, 2, 2])
    
    with c_id: st.write(str(job_id))
    with c_detail: st.write(str(row[detail_col]))
    with c_phone: st.write(str(row[phone_col]))
    with c_status: st.write(status_display)
    with c_action:
        if current_status == "เสร็จสิ้น":
            button_label = "⏳ ปรับเป็นรอดำเนินการ"
            target_status = "รอดำเนินการ"
        else:
            button_label = "✅ ปรับเป็นเสร็จสิ้น"
            target_status = "เสร็จสิ้น"
            
        if st.button(button_label, key=f"btn_{job_id}_{index}"):
            with st.spinner("กำลังบันทึกข้อมูล..."):
                df_latest = get_latest_data()
                
                # บันทึกสถานะใหม่ลงไป
                df_latest.loc[df_latest[id_col].astype(str) == str(job_id), status_col] = target_status
                
                conn.update(data=df_latest)
                st.success(f"อัปเดตลำดับที่ {job_id} เรียบร้อย!")
                st.rerun()
