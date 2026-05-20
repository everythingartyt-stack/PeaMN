import streamlit as st
import pandas as pd
import time

st.title("⚡ ระบบติดตามงานไฟฟ้าขัดข้อง")
st.write("หน้าจอแสดงผลและติดตามสถานะงานล่าสุดจาก Google Sheets")

# ฟังก์ชันดึงข้อมูลจาก Google Sheets (ฐานหลักดั้งเดิม ดึงสดเรียลไทม์ทะลวง Cache)
def get_latest_data():
    spreadsheet_id = "10LJJzAoMcWfWnkcZrlEEyhogIEfmnoGzx7QsgG_2yg4"
    # เติมตัวแปรเวลาสุ่มท้ายลิงก์เพื่อบังคับให้กูเกิลส่งข้อมูลปัจจุบันออกมาเสมอ ไม่ค้างแคช
    csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=Sheet1&t={int(time.time())}"
    
    df_raw = pd.read_csv(csv_url)
    df_raw.columns = df_raw.columns.str.strip()
    return df_raw.fillna("")

try:
    df = get_latest_data()
except Exception as e:
    st.error("❌ ระบบดึงข้อมูลขัดข้อง: กรุณาตรวจสอบสิทธิ์การแชร์ Google Sheets")
    st.stop()

st.subheader("📋 รายการแจ้งเหตุและสถานะปัจจุบัน")

if df.empty:
    st.warning("⚠️ ไม่พบข้อมูลในแท็บ Sheet1 กรุณาตรวจสอบข้อมูลใน Google Sheets")
else:
    id_col = "ลำดับที่" if "ลำดับที่" in df.columns else df.columns[0]
    detail_col = "รายละเอียด" if "รายละเอียด" in df.columns else df.columns[1]
    phone_col = "เบอร์โทร" if "เบอร์โทร" in df.columns else df.columns[2]
    status_col = "สถานะ" if "สถานะ" in df.columns else df.columns[3]

    # วนลูปแสดงผลรายการทั้งหมด 1-20 แบบไม่มีปุ่มกด
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
        
        # 🎯 ดึงสถานะจากคอลัมน์ D มาแปรเป็นข้อความโชว์ในตารางงานตรงๆ
        if "ดำเนินการเสร็จสิ้น" in current_status or "เสร็จสิ้น" in current_status:
            status_display = "✅ เสร็จสิ้น"
        else:
            status_display = "⏳ รอดำเนินการ"
        
        with st.container():
            # โชว์ข้อมูลงานและสถานะจากคอลัมน์ D นอกปุ่มแบบเน้นๆ
            st.write(f"**ลำดับที่ {job_id}** | สถานะ: **{status_display}**")
            st.write(f"📌 {job_detail}")
            
            phone_val = str(row[phone_col]).strip()
            if phone_val != "" and phone_val != "nan" and phone_val != "0.0" and phone_val != "0":
                st.write(f"📞 เบอร์โทร: {phone_val}")
                        
        st.divider()
