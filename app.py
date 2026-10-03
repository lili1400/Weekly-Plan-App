import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
import requests
import os

# إعداد خط ذكي عالمي يدعم الإنجليزية والعربية في الـ PDF
FONT_URL = "https://cloudflare.com"
FONT_PATH = "Amiri-Regular.ttf"

if not os.path.exists(FONT_PATH):
    try:
        response = requests.get(FONT_URL, timeout=15)
        if response.status_code == 200:
            with open(FONT_PATH, 'wb') as f:
                f.write(response.content)
    except:
        pass

has_font = False
if os.path.exists(FONT_PATH) and os.path.getsize(FONT_PATH) > 1000:
    try:
        pdfmetrics.registerFont(TTFont('GlobalFont', FONT_PATH))
        has_font = True
    except:
        has_font = False

# دالة ذكية لتنسيق النصوص وتوصيل الحروف العربية وتصحيح اتجاهها
def smart_format(text):
    if not text:
        return ""
    text_str = str(text)
    has_arabic = any(u'\u0600' <= char <= u'\u06FF' for char in text_str)
    if has_arabic:
        reshaped = arabic_reshaper.reshape(text_str)
        return get_display(reshaped)
    return text_str

# إعداد واجهة برنامج المعلمات
st.set_page_config(page_title="Weekly Lesson Plan App", layout="wide")
st.title("📝 International School - Weekly Lesson Plan Generator")

# شريط جانبي لتعبئة البيانات الأساسية للجدول
st.sidebar.header("📋 Header Information")
school_name = st.sidebar.text_input("School Name", "International School")
week_num = st.sidebar.text_input("Week", "Week 7")
grade = st.sidebar.text_input("Grade / Section", "1A")
date_range = st.sidebar.text_input("Date", "Oct 4 - Oct 8")

st.sidebar.header("👇 Footer Information")
footer_note = st.sidebar.text_area("Administration Note", "Note: Please follow up on the platform and homework daily.")
signature_1 = st.sidebar.text_input("Teacher's Signature", "Class Teacher")
signature_2 = st.sidebar.text_input("Coordinator's Signature", "School Principal")

# هيكل جدول الحصص والمواد الأصلي المعتمد في مدرستكم
days_data = {
    "Sunday": [
        (1, "Science"), (2, "Math"), (3, "Islamic"), (4, "English"),
        (5, "English"), (6, "Arabic"), (7, "Arabic"), (8, "Native Speaker")
    ],
    "Monday": [
        (1, "Science"), (2, "Math"), (3, "English"), (4, "English"),
        (5, "Arabic"), (6, "PE"), (7, "Islamic"), (8, "ICT")
    ],
    "Tuesday": [
        (1, "Math"), (2, "Little Readers Club"), (3, "Science"), (4, "Arabic"),
        (5, "English"), (6, "Islamic"), (7, "Native Speaker")
    ],
    "Wednesday": [
        (1, "French"), (2, "Islamic"), (3, "ICT"), (4, "Math"),
        (5, "English"), (6, "Arabic"), (7, "PE")
    ],
    "Thursday": [
        (1, "Math"), (2, "English"), (3, "English"), (4, "Arabic"),
        (5, "Science"), (6, "Islamic"), (7, "Art")
    ]
}

# بناء تابات الأيام المريحة للمعلمة للتعبئة
tabs = st.tabs(list(days_data.keys()))
all_inputs = {}

for index, (day, periods) in enumerate(days_data.items()):
    with tabs[index]:
        st.subheader(f"📅 Schedule for {day}")
        day_inputs = []
        for period, subject in periods:
            # هنا تم التعديل بوضع رقم 4 لتحديد تقسيم الأعمدة بشكل سليم ومنع الخطأ
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write(f"Period {period}")
            with col2:
                st.write(f"**{subject}**")
            with col3:
                cw = st.text_input(f"Classwork - P{period}", key=f"{day}_{period}_cw", placeholder="Enter classwork...")
            with col4:
                hw = st.text_input(f"Homework - P{period}", key=f"{day}_{period}_hw", placeholder="Enter homework...")
            
            day_inputs.append({
                "Period": period,
                "Subject": subject,
                "Classwork": cw,
                "Homework": hw
            })
        all_inputs[day] = day_inputs

st.write("---")

# إجراء توليد وتصدير ملف الـ PDF الموسط بالكامل
if st.button("🚀 Export Weekly Plan to PDF"):
    pdf_filename = "weekly_plan.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    story = []
    
    font_name = 'GlobalFont' if has_font else 'Helvetica'
    
    # 1. ترويسة الصفحة العليا (موسطة بالكامل CENTER)
    title_style = TableStyle([
        ('FONTNAME', (0,0), (-1,-1), font_name),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#1A365D")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ])
    
    header_info = [
        [smart_format(f"School: {school_name}"), smart_format(f"Weekly Lesson Plan - {week_num}")],
        [smart_format(f"Grade: {grade}"), smart_format(f"Date: {date_range}")]
    ]
    header_table = Table(header_info, colWidths=[270, 270])
    header_table.setStyle(title_style)
    story.append(header_table)
    story.append(Spacer(1, 15))
    
    # 2. جداول الحصص الأسبوعية (موسطة بالكامل CENTER)
    for day, rows in all_inputs.items():
        table_data = [["Period", "Subject", "Classwork", "Homework"]]
        
        for row in rows:
            table_data.append([
                smart_format(row['Period']),
                smart_format(row['Subject']),
                smart_format(row['Classwork']),
                smart_format(row['Homework'])
            ])
            
        # شريط اسم اليوم العلوي (موسط)
        day_title = Table([[smart_format(f"📅 {day}")]], colWidths=[540])
        day_title.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), font_name),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(day_title)
        
        # تنسيق الجدول وتوسيط المدخلات والبيانات أفقياً وعمودياً
        t = Table(table_data, colWidths=[50, 110, 190, 190])
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), font_name),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#2D3748")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))
        
    # 3. ترويسة الصفحة السفلية والتواقيع (موسطة بالكامل CENTER)
    story.append(Spacer(1, 10))
    footer_data = [
        [smart_format(footer_note), ""],
        [smart_format(f"Teacher: {signature_1}"), smart_format(f"Coordinator: {signature_2}")]
    ]
    footer_table = Table(footer_data, colWidths=[270, 270])
    footer_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), font_name),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(footer_table)
    
    # بناء المستند
    doc.build(story)
    
    with open(pdf_filename, "rb") as pdf_file:
        PDFbyte = pdf_file.read()
    
    st.success("🎉 PDF Generated with Centered Text Successfully!")
    st.download_button(label="📥 Click Here to Download PDF File",
                       data=PDFbyte,
                       file_name=f"Weekly_Plan_{grade}.pdf",
                       mime='application/octet-stream')
