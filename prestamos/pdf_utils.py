from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from io import BytesIO
from django.utils import timezone
from django.shortcuts import get_object_or_404
from prestamos.models import Prestamo

def generar_pdf_prestamo(prestamo, download=False ):
    """
    Genera un PDF profesional para un préstamo de equipo.
    
    Args:
        prestamo: Objeto Prestamo con la información del préstamo
        download: Boolean que indica si el PDF debe descargarse o mostrarse en el navegador
        
    Returns:
        HttpResponse con el PDF generado
    """
    # Crear buffer para el PDF (memoria temporal)
    buffer = BytesIO()
    
    # IMPORTANTE: Configurar el documento con márgenes específicos
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=2.54*cm,    # 1 pulgada exacta
        leftMargin=2.54*cm,     # 1 pulgada exacta
        topMargin=2.54*cm,      # 1 pulgada exacta
        bottomMargin=2.54*cm    # 1 pulgada exacta
    )
    
    # Lista para almacenar todos los elementos del PDF
    elements = []
    
    # ============================================================================
    # DEFINICIÓN DE ESTILOS PERSONALIZADOS
    # ============================================================================
    styles = getSampleStyleSheet()
    
    # Estilo para el título principal (ESPOCH)
    styles.add(ParagraphStyle(
        name='Titulo',
        fontName='Helvetica-Bold',
        fontSize=16,           # Tamaño especificado: 16pt
        alignment=TA_CENTER,
        spaceAfter=6
    ))
    
    # Estilo para el subtítulo (PRÉSTAMO DE EQUIPOS - LABORATORIO...)
    styles.add(ParagraphStyle(
        name='Subtitulo',
        fontName='Helvetica',
        fontSize=14,           # Tamaño especificado: 14pt
        alignment=TA_CENTER,
        spaceAfter=10
    ))
    
    # Modificar el estilo Normal existente en lugar de añadir uno nuevo
    styles['Normal'].fontName = 'Helvetica'
    styles['Normal'].fontSize = 11  # Tamaño especificado: 11pt
    styles['Normal'].spaceAfter = 6
    
    # Estilo para texto justificado (usado en el texto de responsabilidad)
    styles.add(ParagraphStyle(
        name='Justificado',
        fontName='Helvetica',
        fontSize=10,          # Tamaño especificado: 10pt
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        leading=12           # Interlineado especificado: 12pt
    ))
    
    # Estilo para encabezados de sección
    styles.add(ParagraphStyle(
        name='Encabezado',
        fontName='Helvetica-Bold',
        fontSize=12,          # Tamaño especificado: 12pt
        alignment=TA_LEFT,
        spaceAfter=6
    ))
    
    # ============================================================================
    # ENCABEZADO DEL DOCUMENTO
    # ============================================================================
    elements.append(Paragraph("ESCUELA SUPERIOR POLITÉCNICA DE CHIMBORAZO", styles['Titulo']))

    # Obtener información de laboratorio del primer equipo en los detalles
    if prestamo.detalles.exists():
        primer_detalle = prestamo.detalles.first()
        tipo_lab = primer_detalle.equipo.laboratorio.get_tipo_display().upper()
        if "LABORATORIO DE" in primer_detalle.equipo.laboratorio.nombre.upper():
            subtitulo = f"PRÉSTAMO DE EQUIPOS - {primer_detalle.equipo.laboratorio.nombre.upper()}"
        else:
            if tipo_lab == "LABORATORIO":
                subtitulo = f"PRÉSTAMO DE EQUIPOS - {primer_detalle.equipo.laboratorio.nombre.upper()}"
            else:
                subtitulo = f"PRÉSTAMO DE EQUIPOS - {tipo_lab} DE {primer_detalle.equipo.laboratorio.nombre.upper()}"
    elif prestamo.equipo:  # Compatibilidad con préstamos antiguos
        tipo_lab = prestamo.equipo.laboratorio.get_tipo_display().upper()
        if "LABORATORIO DE" in prestamo.equipo.laboratorio.nombre.upper():
            subtitulo = f"PRÉSTAMO DE EQUIPOS - {prestamo.equipo.laboratorio.nombre.upper()}"
        else:
            if tipo_lab == "LABORATORIO":
                subtitulo = f"PRÉSTAMO DE EQUIPOS - {prestamo.equipo.laboratorio.nombre.upper()}"
            else:
                subtitulo = f"PRÉSTAMO DE EQUIPOS - {tipo_lab} DE {prestamo.equipo.laboratorio.nombre.upper()}"
    else:
        subtitulo = "PRÉSTAMO DE EQUIPOS"

    elements.append(Paragraph(subtitulo, styles['Subtitulo']))

    # Espacio después del encabezado principal: 0.6cm
    elements.append(Spacer(1, 0.6*cm))
    
    # ============================================================================
    # FECHA Y TÉCNICO ENCARGADO
    # ============================================================================
    fecha_actual = timezone.now().strftime("%d/%m/%Y")
    
    # Crear tabla profesional para fecha y técnico
    info_header_data = [
        ["Fecha:", fecha_actual, "Técnico Encargado:", "Ing. Felix Ruiz M"]
    ]
    
    # Tabla profesional con bordes y estilo mejorado
    info_header_table = Table(info_header_data, colWidths=[2.5*cm, 3*cm, 4*cm, 6.5*cm])
    info_header_table.setStyle(TableStyle([
        # Bordes de tabla para aspecto profesional
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        
        # Fondos alternados para mejor visualización
        ('BACKGROUND', (0, 0), (0, 0), colors.Color(0.9, 0.9, 0.9)),  # Gris claro para etiquetas
        ('BACKGROUND', (2, 0), (2, 0), colors.Color(0.9, 0.9, 0.9)),  # Gris claro para etiquetas
        
        # Alineación y estilos de texto
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('ALIGN', (3, 0), (3, 0), 'CENTER'),
        
        # Formato de texto - etiquetas en negrita, valores en normal
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica'),
        ('FONTNAME', (3, 0), (3, 0), 'Helvetica'),  # Técnico sin negrillas
        
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Padding para mejor espaciado
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('LEFTPADDING', (0, 0), (-1, 0), 6),
        ('RIGHTPADDING', (0, 0), (-1, 0), 6),
    ]))
    elements.append(info_header_table)

    # Espaciado antes de cada sección de tabla: 0.8cm
    elements.append(Spacer(1, 0.8*cm))
    
    # ============================================================================
    # INFORMACIÓN DEL PRÉSTAMO (TABLA DE PERSONA)
    # ============================================================================
    elements.append(Paragraph("Información del Préstamo", styles['Encabezado']))
    elements.append(Spacer(1, 0.3*cm))
    
    # Tabla con información de la persona
    data_persona = [
        ["Solicitante", prestamo.persona.nombre],
        ["Cédula", prestamo.persona.cedula],
        ["Carrera", prestamo.persona.get_carrera_display()],
    ]
    
    # Agregar código institucional si existe
    if prestamo.persona.codigo_institucional:
        data_persona.append(["Código Institucional", prestamo.persona.codigo_institucional])
    
    # Fechas de préstamo y devolución
    data_persona.append(["Fecha de Préstamo", prestamo.fecha_prestamo.strftime("%d/%m/%Y %H:%M")])
    data_persona.append(["Fecha de Devolución Esperada", prestamo.fecha_devolucion_esperada.strftime("%d/%m/%Y %H:%M")])
    
    # Convertir texto a Paragraph para que se ajuste dentro de la celda
    for i in range(len(data_persona)):
        for j in range(len(data_persona[i])):
            if j == 0:  # Primera columna en negrita
                if not isinstance(data_persona[i][j], Paragraph):
                    data_persona[i][j] = Paragraph(str(data_persona[i][j]), ParagraphStyle(
                        name='CellBold',
                        fontName='Helvetica-Bold',
                        fontSize=11,
                        alignment=TA_LEFT
                    ))
            else:  # Resto del contenido normal
                if not isinstance(data_persona[i][j], Paragraph):
                    data_persona[i][j] = Paragraph(str(data_persona[i][j]), ParagraphStyle(
                        name='CellNormal',
                        fontName='Helvetica',
                        fontSize=11,
                        alignment=TA_LEFT
                    ))
    
    # Ancho de columnas especificado: 4.5cm (primera columna), 11.5cm (segunda columna)
    tabla_persona = Table(data_persona, colWidths=[4.5*cm, 11.5*cm])
    
    # Estilo de la tabla de persona
    tabla_persona.setStyle(TableStyle([
        # Fondo gris muy claro: RGB 237,237,237
        ('BACKGROUND', (0, 0), (0, -1), colors.Color(237/255, 237/255, 237/255)),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        # Grosor de líneas: 0.5pt
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        # Padding de celdas: 6pt
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        # Ajuste de texto
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    
    elements.append(tabla_persona)
    
    # Espaciado antes de cada sección de tabla: 0.8cm
    elements.append(Spacer(1, 0.8*cm))
    
    # ============================================================================
    # INFORMACIÓN DEL EQUIPO (TABLA DE EQUIPO)
    # ============================================================================
    elements.append(Paragraph("Equipo Prestado", styles['Encabezado']))
    elements.append(Spacer(1, 0.3*cm))
    
    # Cabecera de la tabla de equipos
    data_equipo = [
        ["Código", "Nombre del Equipo", "Laboratorio"],
    ]
    
    # Añadir equipos de los detalles
    if prestamo.detalles.exists():
        for detalle in prestamo.detalles.all():
            data_equipo.append([
                detalle.equipo.codigo, 
                detalle.equipo.nombre, 
                detalle.equipo.laboratorio.nombre
            ])
    elif prestamo.equipo:  # Compatibilidad con préstamos antiguos
        data_equipo.append([
            prestamo.equipo.codigo, 
            prestamo.equipo.nombre, 
            prestamo.equipo.laboratorio.nombre
        ])
    
    # Agregar observaciones si existen
    if prestamo.observaciones:
        data_equipo.append(["Observaciones", prestamo.observaciones, ""])
    
    # Convertir texto a Paragraph y aplicar estilos específicos
    for i in range(len(data_equipo)):
        for j in range(len(data_equipo[i])):
            if i == 0:  # Encabezados de columna en negrita
                if not isinstance(data_equipo[i][j], Paragraph):
                    data_equipo[i][j] = Paragraph(str(data_equipo[i][j]), ParagraphStyle(
                        name='HeaderBold',
                        fontName='Helvetica-Bold',
                        fontSize=11,
                        alignment=TA_LEFT
                    ))
            else:  # Contenido normal
                if not isinstance(data_equipo[i][j], Paragraph):
                    data_equipo[i][j] = Paragraph(str(data_equipo[i][j]), ParagraphStyle(
                        name='CellNormal',
                        fontName='Helvetica',
                        fontSize=11,
                        alignment=TA_LEFT
                    ))
    
    # Anchos de columnas especificados: 3.5cm, 7.5cm, 5cm
    tabla_equipo = Table(data_equipo, colWidths=[3.5*cm, 7.5*cm, 5*cm])
    
    # Estilo de la tabla de equipo
    tabla_equipo.setStyle(TableStyle([
        # Fondo gris muy claro: RGB 237,237,237 para los encabezados
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(237/255, 237/255, 237/255)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        # Grosor de líneas: 0.5pt
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        # Padding de celdas: 6pt
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        # Si hay observaciones, combinar las celdas
        ('SPAN', (1, len(data_equipo)-1), (2, len(data_equipo)-1)) if prestamo.observaciones else ('SPAN', (0, 0), (0, 0)),
        # Ajuste de texto
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    
    elements.append(tabla_equipo)
    
    # ============================================================================
    # SECCIÓN DE FIRMA
    # ============================================================================
    # Antes de la sección de firma: 2.5cm
    elements.append(Spacer(1, 2.5*cm))
    
    # Crear tabla para la línea de firma y el nombre
    firma_data = [
        ["_______________________________"],  # Ancho de línea: 7cm
        [prestamo.persona.nombre],
        [f"C.I. {prestamo.persona.cedula}"]
    ]
    
    # Configurar la tabla de firma
    firma_table = Table(firma_data, colWidths=[7*cm])  # Ancho especificado: 7cm
    firma_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        # Nombre del firmante: Negrita, 11pt
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 11),  # Línea de firma: 11pt
        ('FONTSIZE', (0, 1), (0, 1), 11),  # Nombre: 11pt
        ('FONTSIZE', (0, 2), (0, 2), 11),  # CI: 11pt
        # Ajustar espaciado
        ('BOTTOMPADDING', (0, 0), (0, 0), 0),
        ('TOPPADDING', (0, 1), (0, 1), 0),
    ]))
    
    # Centrar la tabla de firma en la página
    firma_wrapper = Table([[firma_table]], colWidths=[16*cm])
    firma_wrapper.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
    ]))
    
    elements.append(firma_wrapper)
    
    # ============================================================================
    # TEXTO DE RESPONSABILIDAD
    # ============================================================================
    # Antes del texto de responsabilidad: 1.2cm
    elements.append(Spacer(1, 1.2*cm))
    
    # Determinar el laboratorio principal y preparar la lista de equipos
    equipos_texto = ""
    nombre_lab = ""
    
    if prestamo.detalles.exists():
        # Obtenemos el primer laboratorio para el texto principal
        primer_detalle = prestamo.detalles.first()
        nombre_lab = primer_detalle.equipo.laboratorio.nombre
        
        # Generar texto con todos los equipos
        equipos = []
        for i, detalle in enumerate(prestamo.detalles.all()):
            if i == 0:
                equipos.append(f"<b>{detalle.equipo.nombre}</b> (código: <b>{detalle.equipo.codigo}</b>)")
            else:
                equipos.append(f"<b>{detalle.equipo.nombre}</b> (código: <b>{detalle.equipo.codigo}</b>)")
        
        # Unir la lista de equipos con comas y "y" para el último
        if len(equipos) == 1:
            equipos_texto = equipos[0]
        elif len(equipos) == 2:
            equipos_texto = f"{equipos[0]} y {equipos[1]}"
        else:
            equipos_texto = ", ".join(equipos[:-1]) + f" y {equipos[-1]}"
            
    elif prestamo.equipo:  # Compatibilidad con préstamos antiguos
        nombre_lab = prestamo.equipo.laboratorio.nombre
        equipos_texto = f"<b>{prestamo.equipo.nombre}</b> (código: <b>{prestamo.equipo.codigo}</b>)"
    else:
        nombre_lab = "laboratorio correspondiente"
        equipos_texto = "los equipos prestados"
    
    # Eliminar la repetición de "Laboratorio de" si existe
    if "Laboratorio de " in nombre_lab:
        nombre_lab = nombre_lab.replace("Laboratorio de Laboratorio de", "Laboratorio de")
    
    # Texto de responsabilidad con partes específicas en negrita e itálica (letra inclinada)
    verbo = "los" if prestamo.detalles.count() > 1 else "lo"
    texto_responsabilidad = (
        f"Yo, <b>{prestamo.persona.nombre}</b>, con número de cédula <b>{prestamo.persona.cedula}</b>, "
        f"me responsabilizo por {equipos_texto} "
        f"que estoy retirando del {nombre_lab}. "
        f"Me comprometo a devolverlos en la fecha acordada y en las mismas condiciones en que {verbo} recibo. "
        f"Entiendo que cualquier daño o pérdida será mi responsabilidad."
    )
    
    # Usar el estilo justificado para el texto de responsabilidad y aplicar letra inclinada
    styles.add(ParagraphStyle(
        name='JustificadoItalica',
        fontName='Helvetica-Oblique',  # Cambiar a letra inclinada (itálica)
        fontSize=10,                   # Tamaño especificado: 10pt
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        leading=12                     # Interlineado especificado: 12pt
    ))
    
    # Usar el estilo con letra inclinada
    elements.append(Paragraph(texto_responsabilidad, styles['JustificadoItalica']))
    
    # ============================================================================
    # GENERAR EL PDF
    # ============================================================================
    doc.build(elements)
    
    # Obtener el contenido del PDF del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Crear respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    
    # Configurar para descarga o visualización en el navegador
    if download:
        filename = f"prestamo_{prestamo.id}.pdf"
        content = f"attachment; filename={filename}"
        response['Content-Disposition'] = content
    
    response.write(pdf)
    return response

# ============================================================================
# VISTA PARA GENERAR EL PDF
# ============================================================================
def vista_generar_pdf_prestamo(request, pk):
    """
    Vista que genera el PDF de un préstamo.
    
    Args:
        request: Objeto HttpRequest
        pk: ID del préstamo
        
    Returns:
        PDF del préstamo para visualizar o descargar
    """
    # Obtener el préstamo o devolver 404 si no existe
    prestamo = get_object_or_404(Prestamo, pk=pk)
    
    # Verificar si se debe descargar o solo visualizar
    download = request.GET.get('download', False)
    
    # Generar y devolver el PDF
    return generar_pdf_prestamo(prestamo, download)
