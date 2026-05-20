import streamlit as st
import pandas as pd
import requests
import time

st.title("⚡ ระบบติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# ฟังก์ชันดึงข้อมูลจาก Google Sheets (ฐานหลักตัวที่ทำงานได้ดีที่สุดและดึงสดเรียลไทม์)
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
    st.warning("⚠️ ไม่พบข้อมูลในแท็บ Sheet1 กรุณาตรวจสอบข้อมูลใน Google Sheets")
else:
    id_col = "ลำดับที่" if "ลำดับที่" in df.columns else df.columns[0]
    detail_col = "รายละเอียด" if "รายละเอียด" in df.columns else df.columns[1]
    phone_col = "เบอร์โทร" if "เบอร์โทร" in df.columns else df.columns[2]
    status_col = "สถานะ" if "สถานะ" in df.columns else df.columns[3]

    # ลิงก์ยิงส่งข้อมูลฟอร์มหลังบ้านของน้า
    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd_wMre6U9zY3z-K613M66C9g6x10lUWhR9o79oV49e4M38aw/formResponse"
    
    # 🎯 แก้ไขรหัส Entry ID หลังบ้านให้ตรงกับลิงก์ฟอร์มจริงของน้า 100%
    ID_ENTRY = "entry.460492823"
    STATUS_ENTRY = "entry.680076043"

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
        
        # เช็กสถานะคำว่า ดำเนินการเสร็จสิ้น จากในตารางสเปรดชีตของน้า
        if current_status == "ดำเนินการเสร็จสิ้น" or current_status == "เสร็จสิ้น":
            is_completed = True
            status_icon = "✅ เสร็จสิ้น"
        else:
            is_completed = False
            status_icon = "⏳ รอดำเนินการ"
        
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
                    # ส่งค่าให้ตรงกับตัวเลือกในกูเกิลฟอร์มของน้าเป๊ะๆ
                    target_status = "รอดำเนินการ" if is_completed else "ดำเนินการเสร็จสิ้น"
                    payload = {ID_ENTRY: str(job_id), STATUS_ENTRY: target_status}
                    
                    with st.spinner("กำลังบันทึก..."):
                        try:
                            # ส่งคำสั่งโพสต์ไปที่ฟอร์มตัวจริงของน้า
                            requests.post(FORM_URL, data=payload, timeout=5)
                        except:
                            pass
                        time.sleep(1.5)
                        st.rerun()

                # เลือกโชว์แค่กล่องสีเดียวค้างไว้ฝั่งขวาตามสถานะจริง
                if is_completed:
                    st.success("ดำเนินการเสร็จสิ้น!")
                else:
                    st.error("รอดำเนินการ")
                    
        st.divider()
