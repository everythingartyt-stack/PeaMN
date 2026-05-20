import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(title="ระบบอัปเดตงานไฟฟ้า", layout="wide")
st.title("⚡ แดชบอร์ดติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# 1. เชื่อมต่อกับ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ฟังก์ชันดึงข้อมูลล่าสุด
def get_latest_data():
    df_raw = conn.read(ttl="0")
    # จัดการกรณีช่องว่างให้แสดงเป็นข้อความธรรมดา
    df_raw["สถานะ"] = df_raw["สถานะ"].fillna("รอดำเนินการ").strip() if "สถานะ" in df_raw.columns else "รอดำเนินการ"
    df_raw["สถานะ"] = df_raw["สถานะ"].replace("", "รอดำเนินการ")
    return df_raw.fillna("")

df = get_latest_data()

# --- ส่วนที่ 1: แดชบอร์ดสรุปภาพรวม (Metrics) ---
st.subheader("📊 สรุปภาพรวมสถานะงาน")
if not df.empty:
    total_jobs = len(df)
    # นับจำนวนงานเสร็จสิ้นและรอดำเนินการ
    done_count = len(df[df["สถานะ"] == "เสร็จสิ้น"])
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

# สร้างหัวคอลัมน์สำหรับการแสดงผลบนหน้าเว็บ (แบ่งสัดส่วนหน้าจอ)
col_id, col_detail, col_phone, col_status, col_action = st.columns([1, 4, 2, 2, 2])

# แสดงหัวตาราง
with col_id: st.markdown("**ลำดับที่**")
with col_detail: st.markdown("**รายละเอียด**")
with col_phone: st.markdown("**เบอร์โทร**")
with col_status: st.markdown("**สถานะปัจจุบัน**")
with col_action: st.markdown("**เปลี่ยนสถานะ**")

st.divider()

# วนลูปแสดงข้อมูลทีละแถวพร้อมสร้างปุ่มกด
for index, row in df.iterrows():
    # ตรวจสอบความถูกต้องของลำดับที่
    job_id = row["ลำดับที่"]
    current_status = row["สถานะ"] if row["สถานะ"] != "" else "รอดำเนินการ"
    
    # กำหนดสีหรือไอคอนให้สถานะดูง่ายขึ้น
    status_display = f"✅ เสร็จสิ้น" if current_status == "เสร็จสิ้น" else f"⏳ รอดำเนินการ"
    
    # สร้างแถวข้อมูล
    c_id, c_detail, c_phone, c_status, c_action = st.columns([1, 4, 2, 2, 2])
    
    with c_id:
        st.write(str(job_id))
    with c_detail:
        st.write(row["รายละเอียด"])
    with c_phone:
        st.write(str(row["เบอร์โทร"]))
    with c_status:
        st.write(status_display)
    with c_action:
        # เงื่อนไขปุ่มกด: ถ้าเป็น 'รอดำเนินการ' จะขึ้นปุ่มให้กด 'เสร็จสิ้น' และสลับกัน
        if current_status == "เสร็จสิ้น":
            button_label = "⏳ ปรับเป็นรอดำเนินการ"
            target_status = "รอดำเนินการ"
        else:
            button_label = "✅ ปรับเป็นเสร็จสิ้น"
            target_status = "เสร็จสิ้น"
            
        # เมื่อมีการกดปุ่มในแถวนั้นๆ
        if st.button(button_label, key=f"btn_{job_id}_{index}"):
            with st.spinner("กำลังบันทึกข้อมูล..."):
                # ดึงข้อมูลล่าสุดเสี้ยววินาทีก่อนเซฟเพื่อป้องกันการเขียนทับข้อมูลคนอื่น
                df_latest = get_latest_data()
                
                # อัปเดตสถานะเฉพาะแถวที่กดลงคอลัมน์ 'สถานะ' (คอลัมน์ D)
                df_latest.loc[df_latest["ลำดับที่"] == job_id, "status"] = target_status # รองรับชื่อคอลัมน์เล็กใหญ่
                if "สถานะ" in df_latest.columns:
                    df_latest.loc[df_latest["ลำดับที่"] == job_id, "สถานะ"] = target_status
                
                # ส่งข้อมูลที่แก้ไขแล้วกลับไปยัง Google Sheets
                conn.update(data=df_latest)
                st.success(f"อัปเดตลำดับที่ {job_id} เป็น '{target_status}' เรียบร้อยแล้ว!")
                st.rerun() # รีเฟรชหน้าจอเพื่อแสดงผลทันที
