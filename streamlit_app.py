import streamlit as st
import pandas as pd
import time

st.title("⚡ ระบบติดตามงานไฟฟ้าขัดข้อง")
st.write("หน้าจอแสดงผลและติดตามสถานะงานล่าสุดจาก Google Sheets")

# 🎯 วางปุ่มอัปเดตสถานะงานทั้งหมดไว้ด้านบนสุด กดทีเดียวดึงค่าใหม่ให้ทุกแถวพร้อมกัน
if st.button("🔄 คลิกเพื่ออัปเดตสถานะงานทั้งหมด", use_container_width=True):
    with st.spinner("กำลังดึงข้อมูลล่าสุดจาก Google Sheets..."):
        # ล้างแคชหน้าเว็บเพื่อบังคับให้แอปดึงค่าใหม่ล่าสุดทันที
        st.cache_data.clear()
        time.sleep(1.0)
        st.rerun()

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
    status_col = "สถานะ
