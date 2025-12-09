"""
Utilidades para generación de PDFs y otras funcionalidades
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from django.core.files.base import ContentFile
from io import BytesIO
from datetime import datetime


def generar_pdf_informe(informe):
    """Genera y guarda un PDF en el FileField del informe"""
    buffer = BytesIO()
    
    # Crear documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Contenedor para elementos del PDF
    elementos = []
    
    # Estilos
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'CustomTitle',
        parent=estilos['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    estilo_subtitulo = ParagraphStyle(
        'CustomSubtitle',
        parent=estilos['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    estilo_normal = ParagraphStyle(
        'CustomNormal',
        parent=estilos['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#444444'),
        spaceAfter=8,
        fontName='Helvetica'
    )
    
    # Título principal
    elementos.append(Paragraph("INFORME DE MANTENIMIENTO", estilo_titulo))
    elementos.append(Paragraph("Sistema MantenTask", estilos['Heading3']))
    elementos.append(Spacer(1, 0.3*inch))
    
    # Información del informe
    elementos.append(Paragraph("INFORMACIÓN GENERAL", estilo_subtitulo))
    
    datos_generales = [
        ['Código de Solicitud:', f'#{informe.codigo_solicitud.codigo_solicitud}'],
        ['Fecha del Informe:', informe.fecha_informe.strftime('%d/%m/%Y %H:%M')],
        ['Generado por:', informe.id_usuario.get_full_name()],
        ['Estado:', informe.codigo_solicitud.codigo_estado.nombre_estado],
    ]
    
    tabla_general = Table(datos_generales, colWidths=[2*inch, 4*inch])
    tabla_general.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elementos.append(tabla_general)
    elementos.append(Spacer(1, 0.3*inch))
    
    # Información de la máquina
    elementos.append(Paragraph("INFORMACIÓN DE LA MÁQUINA", estilo_subtitulo))
    
    maquina = informe.codigo_maquinaria
    datos_maquina = [
        ['Código:', str(maquina.codigo_maquinaria)],
        ['Marca:', maquina.marca],
        ['Modelo:', maquina.modelo],
        ['Sucursal:', maquina.codigo_sucursal.nombre_sucursal],
        ['Fecha de Compra:', maquina.fecha_compra.strftime('%d/%m/%Y')],
        ['Fecha de Instalación:', maquina.fecha_instalacion.strftime('%d/%m/%Y')],
    ]
    
    if maquina.fecha_ultima_mantencion:
        datos_maquina.append([
            'Último Mantenimiento:', 
            maquina.fecha_ultima_mantencion.strftime('%d/%m/%Y')
        ])
    
    tabla_maquina = Table(datos_maquina, colWidths=[2*inch, 4*inch])
    tabla_maquina.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elementos.append(tabla_maquina)
    elementos.append(Spacer(1, 0.3*inch))
    
    # Descripción del problema/trabajo realizado
    elementos.append(Paragraph("DESCRIPCIÓN DEL TRABAJO", estilo_subtitulo))
    
    # Descripción de la solicitud original
    elementos.append(Paragraph("<b>Problema reportado:</b>", estilo_normal))
    elementos.append(Paragraph(informe.codigo_solicitud.descripcion, estilo_normal))
    elementos.append(Spacer(1, 0.2*inch))
    
    # Descripción del informe
    elementos.append(Paragraph("<b>Trabajo realizado:</b>", estilo_normal))
    elementos.append(Paragraph(informe.descripcion, estilo_normal))
    elementos.append(Spacer(1, 0.4*inch))
    
    # Pie de página
    elementos.append(Spacer(1, 0.5*inch))
    fecha_generacion = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    elementos.append(Paragraph(
        f"<i>Documento generado automáticamente por MantenTask el {fecha_generacion}</i>",
        ParagraphStyle('Footer', parent=estilos['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Construir PDF
    doc.build(elementos)
    
    # Obtener contenido del buffer
    pdf_content = buffer.getvalue()
    buffer.close()
    
    # Guardar en el campo FileField
    filename = f'informe_solicitud_{informe.codigo_solicitud.codigo_solicitud}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    content_file = ContentFile(pdf_content)
    informe.archivo_pdf.save(filename, content_file, save=True)
    return informe.archivo_pdf


def enviar_correo_con_adjunto(subject, message, recipient_list, attachment_path):
    """
    Envía un correo electrónico con un archivo adjunto
    
    Args:
        subject: Asunto del correo
        message: Cuerpo del mensaje
        recipient_list: Lista de destinatarios
        attachment_path: Ruta del archivo a adjuntar
    """
    from django.core.mail import EmailMessage
    from django.conf import settings
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
    )
    
    if attachment_path:
        email.attach_file(attachment_path)
    
    email.send(fail_silently=False)
    return True
