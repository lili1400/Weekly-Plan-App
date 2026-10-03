import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io

# Setup page config
st.set_page_config(page_title="Weekly Plan Generator", layout="wide")

st.title("📋 Weekly Plan Generator | مُولد الخطة الأسبوعية")
st.write("Fill in Classwork and Homework for each subject, then click **Export to PDF**.")

# Initial schedule structure based on the provided template
schedule_data = {
    'Sunday': [
        (1, 'Science'), (2, 'Math'), (3, 'Islamic'), (4, 'English'),
        (5, 'English'), (6, 'Arabic'), (7, 'Arabic'), (8, 'Native Speaker')
    ],
    'Monday': [
        (1, 'Science'), (2, 'Math'), (3, 'English'), (4, 'English'),
        (5, 'Arabic'), (6, 'PE'), (7, 'Islamic'), (8, 'ICT')
    ],
    'Tuesday': [
        (1, 'Math'), (2, 'Little Readers Club'), (3, 'Science'), (4, 'Arabic'),
        (5, 'English'), (6, 'Islamic'), (7, 'Native Speaker')
    ],
    'Wednesday': [
        (1, 'French'), (2, 'Islamic'), (3, 'ICT'), (4, 'Math'),
        (5, 'English'), (6, 'Arabic'), (7, 'PE')
    ],
    'Thursday': [
        (1, 'Math'), (2, 'English'), (3, 'English'), (4, 'Arabic'),
        (5, 'Science'), (6, 'Islamic'), (7, 'Art')
    ]
}

# Sidebar for Header Details
st.sidebar.header("📌 Header Information (الترويسة)")
week_input = st.sidebar.text_input("Week (الأسبوع)", value="Week 7")
grade_input = st.sidebar.text_input("Grade (الصف)", value="Grade: 1A")
date_input = st.sidebar.text_input("Date (التاريخ)", value="4th Oct. - 8th Oct.")

st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: You can host this app on Streamlit Community Cloud and share the link via Google Drive!")

# Dictionary to hold the inputs
inputs = {}

# Layout: Generate tabs for each day
days = list(schedule_data.keys())
tabs = st.tabs(days)

for tab, day in zip(tabs, days):
    with tab:
        st.subheader(f"📅 {day} Schedule")
        inputs[day] = []
        
        # Table layout inside Streamlit for easier input
        for period, subject in schedule_data[day]:
            col1, col2, col3, col4 = st.columns([1, 2, 4, 4])
            with col1:
                st.write(f"**Period {period}**")
            with col2:
                st.write(f"*{subject}*")
            with col3:
                cw = st.text_input(f"Classwork", key=f"{day}_{period}_cw", placeholder="Enter classwork...")
            with col4:
                hw = st.text_input(f"Homework", key=f"{day}_{period}_hw", placeholder="Enter homework...")
            
            inputs[day].append({
                'Period': period,
                'Subject': subject,
                'Classwork': cw,
                'Homework': hw
            })

# Function to generate PDF
def generate_pdf(week, grade, date_range, all_inputs):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        alignment=TA_CENTER
    )
    
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        alignment=TA_LEFT
    )
    
    cell_bold_style = ParagraphStyle(
        'CellBoldStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        alignment=TA_LEFT
    )
    
    elements = []
    
    # 1. Header Table
    header_data = [
        [
            Paragraph(f"<b>{week}</b>", title_style),
            Paragraph(f"<b>{grade}</b>", title_style),
            Paragraph(f"<b>{date_range}</b>", title_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[180, 180, 192])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0f2f6")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#4f8bf0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 15))
    
    # 2. Main Content Table containing all days
    main_table_data = []
    
    for day, periods in all_inputs.items():
        # Day Header Row
        main_table_data.append([
            Paragraph(f"<b>{day}</b>", cell_bold_style),
            Paragraph("", cell_style),
            Paragraph("<b>Subject</b>", cell_bold_style),
            Paragraph("<b>Classwork</b>", cell_bold_style),
            Paragraph("<b>Homework</b>", cell_bold_style)
        ])
        
        # Period Rows
        for p in periods:
            main_table_data.append([
                Paragraph("", cell_style), # Empty for spanning look
                Paragraph(str(p['Period']), cell_style),
                Paragraph(p['Subject'], cell_style),
                Paragraph(p['Classwork'] if p['Classwork'] else "-", cell_style),
                Paragraph(p['Homework'] if p['Homework'] else "-", cell_style)
            ])
            
    # Table Width configuration (Total = 552)
    # Day (70), Period (40), Subject (102), Classwork (170), Homework (170)
    content_table = Table(main_table_data, colWidths=[70, 40, 102, 170, 170], repeatRows=0)
    
    # Build dynamic styling for spans and background colors
    t_style = [
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#d3d3d3")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]
    
    row_idx = 0
    for day, periods in all_inputs.items():
        # Style the day header row
        t_style.append(('SPAN', (0, row_idx), (1, row_idx)))
        t_style.append(('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor("#eef4fc")))
        t_style.append(('LINEBELOW', (0, row_idx), (-1, row_idx), 1.5, colors.HexColor("#4f8bf0")))
        
        start_period_row = row_idx + 1
        end_period_row = row_idx + len(periods)
        
        # Span the Day name vertically across its periods
        t_style.append(('SPAN', (0, start_period_row), (0, end_period_row)))
        t_style.append(('VALIGN', (0, start_period_row), (0, end_period_row), 'MIDDLE'))
        t_style.append(('ALIGN', (0, start_period_row), (0, end_period_row), 'CENTER'))
        
        # Put the day name in the first cell of the spanned section
        main_table_data[start_period_row][0] = Paragraph(f"<b>{day}</b>", ParagraphStyle('DayName', parent=cell_bold_style, fontSize=10, alignment=TA_CENTER))
        
        row_idx += len(periods) + 1 # +1 for the header row
        
    content_table.setStyle(TableStyle(t_style))
    elements.append(content_table)
    
    # Build document
    doc.build(elements)
    buffer.seek(0)
    return buffer

st.markdown("---")
st.subheader("🚀 Export Options")

# Generate PDF button
if st.button("📄 Generate and Preview PDF Report"):
    pdf_buffer = generate_pdf(week_input, grade_input, date_input, inputs)
    st.success("PDF generated successfully!")
    st.download_button(
        label="📥 Download PDF File",
        data=pdf_buffer,
        file_name=f"Weekly_Plan_{grade_input.replace(' ', '_')}_{week_input.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
