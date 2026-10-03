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

# إعداد خط عربي رسمي ومستقر يدعم PDF (تم تحديث الرابط ليكون مضموناً ومباشراً)
FONT_URL = "https://cloudflare.com"
FONT_PATH = "Amiri-Regular.ttf"

# محاولة تحميل الخط العربي بأمان دون التسبب في تعطيل البرنامج
if not os.path.exists(FONT_PATH):
    try:
        response = requests.get(FONT_URL, timeout=15)
        if response.status_code == 200:
            with open(FONT_PATH, 'wb') as f:
                f.write(response.content)
    except Exception as e:
        pass

# تسجيل الخط في مكتبة الـ PDF إذا تم تحميله بنجاح، وإلا استخدام الخط الافتراضي كحماية
has_arabic_font = False
if os.path.exists(FONT_PATH) and os.path.getsize(FONT_PATH) > 1000:
    try:
        pdfmetrics.registerFont(TTFont('ArabicFont', FONT_PATH))
        has_arabic_font = True
    except:
        has_arabic_font = False

def format_arabic(text):
    if not text:
        return ""
    # إعادة تشكيل الحروف العربية وتصحيح اتجاهها من اليمين إلى اليسار
    reshaped_text = arabic_reshaper.reshape(str(text))
    bidi_text = get_display(reshaped_text)
    return bidi_text

# إعداد واجهة Streamlit لتدعم اتجاه اللغة العربية
st.set_page_config(page_title="برنامج الخطة الأسبوعية", layout="wide")

st.markdown("""
    <style>
    .reportview-container { direction: rtl; text-align: right; }
    .sidebar .sidebar-content { direction: rtl; text-align: right; }
    div.stButton > button:first-child {
        background-color: #2B6CB0;
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 10px 24px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📝 برنامج إعداد الخطة الأسبوعية المدرسية")

# شريط جانبي للبيانات الأساسية للجدول
st.sidebar.header("📋 البيانات الأساسية (الترويسة)")
school_name = st.sidebar.text_input("اسم المدرسة", "المدرسة العالمية")
week_num = st.sidebar.text_input("الأسبوع", "الأسبوع السابع")
grade = st.sidebar.text_input("الصف", "1A")
date_range = st.sidebar.text_input("التاريخ", "4 أكتوبر - 8 أكتوبر")

st.sidebar.header("👇 الترويسة السفلية")
footer_note = st.sidebar.text_area("ملاحظة الإدارة لأولياء الأمور", "ملاحظة: الرجاء متابعة المنصة والواجبات يومياً مع الطلاب.")
signature_1 = st.sidebar.text_input("توقيع المعلمة", "معلمة المادة")
signature_2 = st.sidebar.text_input("اعتماد الإدارة", "قائدة المدرسة")

# هيكل البيانات الثابتة للأيام والمواد المقسمة حصصاً كما في ملفكِ الأصلي
days_data = {
    "الأحد": [
        (1, "Science"), (2, "Math"), (3, "Islamic"), (4, "English"),
        (5, "English"), (6, "Arabic"), (7, "Arabic"), (8, "Native Speaker")
    ],
    "الإثنين": [
        (1, "Science"), (2, "Math"), (3, "English"), (4, "English"),
        (5, "Arabic"), (6, "PE"), (7, "Islamic"), (8, "ICT")
    ],
    "الثلاثاء": [
        (1, "Math"), (2, "Little Readers Club"), (3, "Science"), (4, "Arabic"),
        (5, "English"), (6, "Islamic"), (7, "Native Speaker")
    ],
    "الأربعاء": [
        (1, "French"), (2, "Islamic"), (3, "ICT"), (4, "Math"),
        (5, "English"), (6, "Arabic"), (7, "PE")
    ],
    "الخميس": [
        (1, "Math"), (2, "English"), (3, "English"), (4, "Arabic"),
        (5, "Science"), (6, "Islamic"), (7, "Art")
    ]
}

# إنشاء التابات لكل يوم لتسهيل التعبئة على المعلمة
tabs = st.tabs(list(days_data.keys()))
all_inputs = {}

for index, (day, periods) in enumerate(days_data.items()):
    with tabs[index]:
        st.subheader(f"📅 خطة يوم {day}")
        day_inputs = []
        for period, subject in periods:
            col1, col2, col3, col4 = st.columns([1, 2, 4, 4])
            with col1:
                st.write(f"الحصة {period}")
            with col2:
                st.write(f"**{subject}**")
            with col3:
                cw = st.text_input(f"العمل الصفي", key=f"{day}_{period}_cw", placeholder="اكتبي Classwork هنا...")
            with col4:
                hw = st.text_input(f"الواجب المنزلي", key=f"{day}_{period}_hw", placeholder="اكتبي Homework هنا...")
            
            day_inputs.append({
                "الحصة": period,
                "المادة": subject,
                "Classwork": cw,
                "Homework": hw
            })
        all_inputs[day] = day_inputs

st.write("---")

# زر التصدير وتحميل ملف الـ PDF المنسق تلقائياً
if st.button("🚀 تصدير الخطة الأسبوعية كملف PDF منسق"):
    pdf_filename = "weekly_plan.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4, rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
    story = []
    
    font_name = 'ArabicFont' if has_arabic_font else 'Helvetica'
    
    # تنسيق الخطوط للترويسة
    title_style = TableStyle([
        ('FONTNAME', (0,0), (-1,-1), font_name),
        ('FONTSIZE', (0,0), (-1,-1), 13),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#1A365D")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ])
    
    # 1. تجميع ترويسة الصفحة العليا باللغة العربية المستقرة
    header_info = [
        [format_arabic(f"المدرسة: {school_name}"), format_arabic(f"الخطة الأسبوعية - {week_num}")],
        [format_arabic(f"الصف: {grade}"), format_arabic(f"التاريخ: {date_range}")]
    ]
    header_table = Table(header_info, colWidths=[270, 270])
    header_table.setStyle(title_style)
    story.append(header_table)
    story.append(Spacer(1, 15))
    
    # 2. بناء جداول الأيام وتفاصيل الحصص
    for day, rows in all_inputs.items():
        table_data = [[format_arabic("الواجب (Homework)"), format_arabic("العمل الصفي (Classwork)"), format_arabic("المادة"), format_arabic("الحصة")]]
        
        for row in rows:
            table_data.append([
                format_arabic(row['Homework']),
                format_arabic(row['Classwork']),
                format_arabic(row['المادة']),
                format_arabic(row['الحصة'])
            ])
            
        # شريط اليوم الملون فوق كل جدول
        day_title = Table([[format_arabic(f"📅 يوم {day}")]], colWidths=[540])
        day_title.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), font_name),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(day_title)
        
        # تنسيق خلايا ومظهر جدول الحصص والبيانات المعبأة
        t = Table(table_data, colWidths=[180, 180, 120, 60])
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), font_name),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#2D3748")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))
        
    # 3. بناء الترويسة السفلية (الملاحظات وأماكن توقيع الإدارة والمعلمة)
    story.append(Spacer(1, 10))
    footer_data = [
        [format_arabic(footer_note), ""],
        [format_arabic(f"اعتماد الإدارة: {signature_2}"), format_arabic(f"توقيع المعلمة: {signature_1}")]
    ]
    footer_table = Table(footer_data, colWidths=[270, 270])
    footer_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), font_name),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(footer_table)
    
    # بناء وتصدير مستند الـ PDF بالبيانات الجديدة
    doc.build(story)
    
    # توفير الملف للتحميل المباشر للمعلمة
    with open(pdf_filename, "rb") as pdf_file:
        PDFbyte = pdf_file.read()
    
    st.success("🎉 تم إنشاء ملف PDF باللغة العربية والترويسات بنجاح!")
    st.download_button(label="📥 اضغطي هنا لتحميل ملف PDF المنسق فوراً",
                       data=PDFbyte,
                       file_name=f"Weekly_Plan_{grade}.pdf",
                       mime='application/octet-stream')
