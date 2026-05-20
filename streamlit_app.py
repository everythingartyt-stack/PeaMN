import streamlit as st
import pandas as pd
import requests
import time

st.title("⚡ ระบบติดตามและอัปเดตงานไฟฟ้าขัดข้อง")
st.write("ทุกคนสามารถเข้าดูข้อมูล และคลิกปุ่มเพื่อเปลี่ยนสถานะงานได้ทันที")

# ฟังก์ชันดึงข้อมูลจาก Google Sheets (Sheet1) เวอร์ชันแก้ไข KeyError ถาวร
def get_latest_data():
    # 🚨 ให้น้าเปลี่ยนลิงก์ในเครื่องหมายคำพูดด้านล่างนี้ ให้เป็นลิงก์แชร์ Google Sheets จริงของน้าได้เลยครับ 🚨
    sheet_url = "https://docs.google.com/spreadsheets/d/1U40Yshv7_2iS5ZfL0_0iE6_7R6kOas9p_A6iEaO_s7k/edit?usp=sharing"
    
    # ดึงไอดีและแปลงท่อดึงข้อมูล CSV เจาะจงแท็บ Sheet1 โดยตรง
    spreadsheet_id = sheet_url.split("/d/")[1].split("/")[0]
    csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&sheet=Sheet1"
    
    # อ่านข้อมูลสดใหม่แบบเรียลไทม์
    df_raw = pd.read_csv(csv_url)
    df_raw.columns = df_raw.columns.str.strip()
    return df_raw.fillna("")

try:
    df = get_latest_data()
except Exception as e:
    st.error("❌ ไม่สามารถดึงข้อมูลได้ กรุณาตรวจสอบว่าได้เปลี่ยนสิทธิ์แชร์ Google Sheets เป็น 'ทุกคนที่มีลิงก์' แล้วหรือยัง")
    st.stop()

st.subheader("📋 รายการแจ้งเหตุและจัดการสถานะ")

if df.empty:
    st.warning("⚠️ ไม่พบข้อมูลในแท็บ Sheet1 กรุณาตรวจสอบข้อมูลใน Google Sheets")
else:
    id_col = "ลำดับที่" if "ลำดับที่" in df.columns else df.columns[0]
    detail_col = "รายละเอียด" if "รายละเอียด" in df.columns else df.columns[1]
    phone_col = "เบอร์โทร" if "เบอร์โทร" in df.columns else df.columns[2]
    status_col = "สถานะ" if "สถานะ" in df.columns else df.columns[3]

    FORM_URL = "
