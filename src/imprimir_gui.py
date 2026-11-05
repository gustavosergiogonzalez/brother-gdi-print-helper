#!/usr/bin/env python3
import sys
import os
import subprocess
import tempfile
import gi
from PIL import Image

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class VentanaImpresionHornero(Gtk.Window):
    def __init__(self, file_path):
        super().__init__(title="Impresión Directa - Brother HL-1200")
        self.file_path = file_path
        self.set_border_width(15)
        self.set_default_size(450, 280)
        self.set_position(Gtk.WindowPosition.CENTER)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(vbox)

        lbl_titulo = Gtk.Label()
        lbl_titulo.set_markup(f"<b>Archivo:</b> {os.path.basename(file_path)}")
        lbl_titulo.set_xalign(0)
        vbox.pack_start(lbl_titulo, False, False, 0)

        vbox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 5)

        grid = Gtk.Grid()
        grid.set_column_spacing(15)
        grid.set_row_spacing(12)
        vbox.pack_start(grid, False, False, 0)

        # Copias
        lbl_copias = Gtk.Label(label="Copias:")
        lbl_copias.set_xalign(0)
        grid.attach(lbl_copias, 0, 0, 1, 1)
        
        self.spn_copias = Gtk.SpinButton()
        self.spn_copias.set_range(1, 99)
        self.spn_copias.set_value(1)
        grid.attach(self.spn_copias, 1, 0, 1, 1)

        # Orientación
        lbl_orient = Gtk.Label(label="Orientación:")
        lbl_orient.set_xalign(0)
        grid.attach(lbl_orient, 0, 1, 1, 1)

        self.cmb_orient = Gtk.ComboBoxText()
        self.cmb_orient.append("auto", "Auto-detectar (Rotar Landscape a A4)")
        self.cmb_orient.append("portrait", "Forzar Vertical")
        self.cmb_orient.append("landscape", "Forzar Horizontal")
        self.cmb_orient.set_active(0)
        grid.attach(self.cmb_orient, 1, 1, 1, 1)

        # Umbral de Binarización
        lbl_umbral = Gtk.Label(label="Contraste Texto/Imagen:")
        lbl_umbral.set_xalign(0)
        grid.attach(lbl_umbral, 0, 2, 1, 1)

        self.cmb_umbral = Gtk.ComboBoxText()
        self.cmb_umbral.append("128", "Normal (Recomendado)")
        self.cmb_umbral.append("160", "Texto Claro / Dibujo Fino")
        self.cmb_umbral.append("96", "Fotos / Imágenes Oscuras")
        self.cmb_umbral.set_active(0)
        grid.attach(self.cmb_umbral, 1, 2, 1, 1)

        vbox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 5)

        self.lbl_status = Gtk.Label(label="Listo para optimizar e imprimir.")
        self.lbl_status.set_xalign(0)
        vbox.pack_start(self.lbl_status, False, False, 0)

        hbox_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        vbox.pack_start(hbox_btn, False, False, 10)

        btn_cancel = Gtk.Button(label="Cancelar")
        btn_cancel.connect("clicked", Gtk.main_quit)
        hbox_btn.pack_start(btn_cancel, True, True, 0)

        btn_print = Gtk.Button(label="🖨️ IMPRIMIR")
        btn_print.get_style_context().add_class("suggested-action")
        btn_print.connect("clicked", self.on_imprimir_clicked)
        hbox_btn.pack_start(btn_print, True, True, 0)

    def on_imprimir_clicked(self, widget):
        self.lbl_status.set_text("Comprimiendo gráfico y enviando...")
        widget.set_sensitive(False)
        
        while Gtk.events_pending():
            Gtk.main_iteration()

        try:
            copias = int(self.spn_copias.get_value())
            orient_modo = self.cmb_orient.get_active_id()
            umbral_val = int(self.cmb_umbral.get_active_id())

            # 1. Procesar con Binarización Limpia (fuerza compresión RLE)
            pdf_procesado = self.procesar_archivo(self.file_path, orient_modo, umbral_val)

            # 2. Enviar a CUPS a 600dpi (Resolución nativa de la impresora)
            cmd_lp = [
                "lp",
                "-d", "HL1200",
                "-n", str(copias),
                "-o", "PageSize=A4",
                "-o", "Resolution=600dpi",
                pdf_procesado
            ]
            subprocess.run(cmd_lp, check=True)

            md = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="¡Enviado a la impresora!"
            )
            md.format_secondary_text("El archivo fue comprimido y enviado correctamente.")
            md.run()
            md.destroy()
            Gtk.main_quit()

        except Exception as e:
            md = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.CLOSE,
                text="Error al procesar",
                secondary_text=str(e)
            )
            md.run()
            md.destroy()
            widget.set_sensitive(True)
            self.lbl_status.set_text("Error al procesar.")

    def procesar_archivo(self, input_path, orientacion, umbral):
        temp_dir = tempfile.mkdtemp()
        output_pdf = os.path.join(temp_dir, "optimizada.pdf")
        ext = os.path.splitext(input_path)[1].lower()

        # 1. Extraer páginas a 300 DPI
        if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']:
            paginas_imgs = [input_path]
        else:
            prefix = os.path.join(temp_dir, "page")
            subprocess.run(["pdftoppm", "-r", "300", "-png", input_path, prefix], check=True)
            paginas_imgs = sorted([os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.startswith("page-")])

        # 2. BINARIZACIÓN LIMPIA (Elimina ruido para activar compresión RLE en brlaser)
        imgs_procesadas = []
        for idx, img_path in enumerate(paginas_imgs):
            out_png_path = os.path.join(temp_dir, f"proc_{idx}.png")
            with Image.open(img_path) as img:
                # Convertir a escala de grises
                gray = img.convert('L')
                w, h = gray.size

                # Rotación si es Landscape
                if (orientacion == "auto" and w > h) or orientacion == "landscape":
                    gray = gray.rotate(-90, expand=True)

                # FILTRO MÁGICO: Convierte a Blanco y Negro puro sin ruido de entramado
                # Esto genera bloques idénticos que la compresión RLE achica a <150KB
                bw = gray.point(lambda p: 255 if p > umbral else 0, mode='1')
                bw.save(out_png_path)
                imgs_procesadas.append(out_png_path)

        # 3. Crear PDF A4
        cmd = ["img2pdf"] + imgs_procesadas + ["--pagesize", "A4", "-o", output_pdf]
        subprocess.run(cmd, check=True)

        return output_pdf

if __name__ == '__main__':
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not file_path or not os.path.exists(file_path):
        dialog = Gtk.FileChooserDialog(title="Seleccionar archivo a imprimir", action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        if dialog.run() == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
        dialog.destroy()

    if file_path:
        win = VentanaImpresionHornero(file_path)
        win.connect("destroy", Gtk.main_quit)
        win.show_all()
        Gtk.main()
