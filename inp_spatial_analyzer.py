import os
import math
import csv
import tempfile
import processing

from qgis.PyQt.QtCore import QVariant, Qt
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QFileDialog
from qgis.PyQt.QtGui import QIcon

from qgis.core import (
    QgsProject, 
    QgsVectorLayer, 
    QgsField, 
    QgsFields,
    QgsRasterLayer,
    QgsColorRampShader, 
    QgsRasterShader, 
    QgsSingleBandPseudoColorRenderer,
    QgsRasterBandStats,
    QgsGeometry,
    QgsFeature,
    QgsVectorFileWriter
)

from .inp_spatial_analyzer_dialog import InpSpatialAnalyzerDialog

class InpSpatialAnalyzer:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dlg = InpSpatialAnalyzerDialog()

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.action = QAction(QIcon(icon_path), 'Analisis Spasial INP', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu('&Analisis Vegetasi', self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removePluginMenu('&Analisis Vegetasi', self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        self.dlg.comboBoxLayer.clear()
        layers = QgsProject.instance().mapLayers().values()
        
        # Saring layer point untuk data vegetasi
        point_layers = [lyr for lyr in layers if isinstance(lyr, QgsVectorLayer) and lyr.geometryType() == 0]
        if not point_layers:
            QMessageBox.warning(self.dlg, "Peringatan", "Tidak ada Vector Layer tipe Point di proyek QGIS!")
            return

        for layer in point_layers:
            self.dlg.comboBoxLayer.addItem(layer.name(), layer)

        # Sambungkan sinyal perubahan layer untuk memperbarui pilihan field
        try:
            self.dlg.comboBoxLayer.currentIndexChanged.disconnect()
        except TypeError:
            pass
        self.dlg.comboBoxLayer.currentIndexChanged.connect(self.populate_field_combos)

        # Populasikan pilihan field untuk layer pertama
        self.populate_field_combos()

        # Saring layer polygon untuk pilihan batas AOI
        if hasattr(self.dlg, 'comboBoxAOI'):
            self.dlg.comboBoxAOI.clear()
            polygon_layers = [lyr for lyr in layers if isinstance(lyr, QgsVectorLayer) and lyr.geometryType() == 2]
            self.dlg.comboBoxAOI.addItem("-- Seluruh Area (Tanpa Batas AOI) --", None)
            for lyr in polygon_layers:
                self.dlg.comboBoxAOI.addItem(lyr.name(), lyr)

        self.dlg.comboBoxStadium.clear()
        self.dlg.comboBoxStadium.addItems(["Pohon", "Tiang", "Pancang", "Semai", "Liana", "Tumbuhan Bawah"])
        
        if hasattr(self.dlg, 'on_stadium_changed'):
            self.dlg.on_stadium_changed()

        # Hubungkan Tombol Browse CSV
        try:
            self.dlg.btnBrowseCsv.clicked.disconnect()
        except TypeError:
            pass
        self.dlg.btnBrowseCsv.clicked.connect(self.browse_csv)

        # Hubungkan Tombol Proses
        try:
            self.dlg.btnProcess.clicked.disconnect()
        except TypeError:
            pass
        self.dlg.btnProcess.clicked.connect(self.process_analysis)

        self.dlg.show()
        self.dlg.exec()

    def populate_field_combos(self):
        """Memuat daftar kolom/field atribut dari layer vector yang dipilih."""
        layer = self.dlg.comboBoxLayer.currentData()
        field_combos = [
            self.dlg.cmbFieldPlot,
            self.dlg.cmbFieldStadium,
            self.dlg.cmbFieldSpesies,
            self.dlg.cmbFieldJumlah,
            self.dlg.cmbFieldDbh
        ]
        
        for combo in field_combos:
            combo.clear()

        if not layer:
            return

        fields = [field.name() for field in layer.fields()]
        
        for combo in field_combos:
            combo.addItems(fields)

        # Set perkiraan pencocokan default jika kolom dinamai sesuai standar umum
        self._set_default_field(self.dlg.cmbFieldPlot, fields, ["plot_id", "plot", "id_plot"])
        self._set_default_field(self.dlg.cmbFieldStadium, fields, ["stadium", "tingkat", "stage"])
        self._set_default_field(self.dlg.cmbFieldSpesies, fields, ["spesies", "species", "nama_jenis", "jenis"])
        self._set_default_field(self.dlg.cmbFieldJumlah, fields, ["jumlah", "count", "n_ind"])
        self._set_default_field(self.dlg.cmbFieldDbh, fields, ["dbh_cm", "dbh", "diameter"])

    def _set_default_field(self, combo, fields, keywords):
        """Membantu memilih field secara otomatis berdasarkan kemiripan nama."""
        for kw in keywords:
            for field in fields:
                if kw.lower() in field.lower():
                    combo.setCurrentText(field)
                    return

    def browse_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.dlg, "Simpan Berkas CSV", "", "CSV Files (*.csv)"
        )
        if file_path:
            if not file_path.lower().endswith('.csv'):
                file_path += '.csv'
            self.dlg.lineEditCsvPath.setText(file_path)

    def process_analysis(self):
        layer = self.dlg.comboBoxLayer.currentData()
        stadium_target = self.dlg.comboBoxStadium.currentText()
        luas_plot_m2 = self.dlg.spinBoxLuasPlot.value()
        pixel_size = self.dlg.spinBoxPixelSize.value()
        csv_path = self.dlg.lineEditCsvPath.text().strip()

        # Pembacaan nama field dari pilihan pengguna
        f_plot = self.dlg.cmbFieldPlot.currentText()
        f_stadium = self.dlg.cmbFieldStadium.currentText()
        f_spesies = self.dlg.cmbFieldSpesies.currentText()
        f_jumlah = self.dlg.cmbFieldJumlah.currentText()
        f_dbh = self.dlg.cmbFieldDbh.currentText()

        aoi_layer = self.dlg.comboBoxAOI.currentData() if hasattr(self.dlg, 'comboBoxAOI') else None
        aoi_geometry = None

        if aoi_layer:
            for aoi_feat in aoi_layer.getFeatures():
                if aoi_geometry is None:
                    aoi_geometry = aoi_feat.geometry()
                else:
                    aoi_geometry = aoi_geometry.combine(aoi_feat.geometry())

        # HANYA Pohon dan Tiang yang menggunakan perhitungan DR & LBDS
        is_tree_level = stadium_target in ["Pohon", "Tiang"]

        selected_metrics = []
        if self.dlg.chkKR.isChecked(): selected_metrics.append('KR')
        if self.dlg.chkFR.isChecked(): selected_metrics.append('FR')
        if self.dlg.chkDR.isChecked() and is_tree_level: selected_metrics.append('DR')
        if self.dlg.chkINP.isChecked(): selected_metrics.append('INP')

        if not csv_path:
            QMessageBox.warning(self.dlg, "Peringatan", "Tentukan lokasi penyimpanan berkas CSV terlebih dahulu!")
            return

        if not selected_metrics:
            QMessageBox.warning(self.dlg, "Peringatan", "Pilih minimal satu indikator spasial (KR, FR, DR, atau INP)!")
            return

        try:
            self.dlg.close()
            self.iface.messageBar().pushMessage("Proses", "Menganalisis data vegetasi...", level=0)

            # 1. HITUNG TOTAL SELURUH PLOT TERLEBIH DAHULU
            all_plots_global = set()
            for feat in layer.getFeatures():
                if aoi_geometry and not aoi_geometry.contains(feat.geometry()):
                    continue
                plot_id = str(feat[f_plot]).strip()
                all_plots_global.add(plot_id)

            total_plots_count = len(all_plots_global)
            if total_plots_count == 0:
                raise ValueError("Tidak ada data plot sama sekali di area/layer yang dipilih!")

            # 2. PROSES DATA SPESIES BERDASARKAN STADIUM & FIELD PILIHAN
            species_data = {}
            
            for feat in layer.getFeatures():
                stadium_val = str(feat[f_stadium]).strip() if feat[f_stadium] is not None else ""
                if stadium_val.lower() != stadium_target.lower():
                    continue

                if aoi_geometry and not aoi_geometry.contains(feat.geometry()):
                    continue

                plot_id = str(feat[f_plot]).strip()
                spesies = str(feat[f_spesies]).strip()
                
                # Baca nilai jumlah (default 1 jika kosong)
                jumlah_raw = feat[f_jumlah]
                jumlah = int(jumlah_raw) if (jumlah_raw is not None and str(jumlah_raw).isdigit()) else 1

                # Baca DBH
                dbh_raw = feat[f_dbh]
                dbh_cm = float(dbh_raw) if (dbh_raw is not None and is_tree_level) else 0.0

                if dbh_cm > 0 and is_tree_level:
                    dbh_m = dbh_cm / 100.0  
                    lbds = (1/4) * math.pi * (dbh_m ** 2)
                else:
                    lbds = 0.0

                if spesies not in species_data:
                    species_data[spesies] = {'ind': 0, 'lbds': 0.0, 'plots': set()}

                species_data[spesies]['ind'] += jumlah
                species_data[spesies]['lbds'] += lbds
                species_data[spesies]['plots'].add(plot_id)

            total_luas_ha = (total_plots_count * luas_plot_m2) / 10000.0

            raw_calc = {}
            sum_K = sum_F = sum_D = 0.0

            for sp, val in species_data.items():
                K = val['ind'] / total_luas_ha
                F = len(val['plots']) / total_plots_count
                D = val['lbds'] / total_luas_ha if is_tree_level else 0.0

                sum_K += K
                sum_F += F
                sum_D += D
                raw_calc[sp] = {'K': K, 'F': F, 'D': D}

            csv_rows = []
            species_metrics = {}

            for idx, (sp, val) in enumerate(raw_calc.items(), start=1):
                KR = (val['K'] / sum_K * 100.0) if sum_K > 0 else 0.0
                FR = (val['F'] / sum_F * 100.0) if sum_F > 0 else 0.0

                if is_tree_level:
                    DR = (val['D'] / sum_D * 100.0) if sum_D > 0 else 0.0
                    INP = KR + FR + DR
                    d_str, dr_str = round(val['D'], 4), round(DR, 2)
                else:
                    DR = 0.0
                    INP = KR + FR
                    d_str, dr_str = "-", "-"

                species_metrics[sp] = {'KR': KR, 'FR': FR, 'DR': DR, 'INP': INP}

                csv_rows.append([
                    idx, sp, round(val['K'], 2), round(KR, 2),
                    round(val['F'], 4), round(FR, 2), d_str, dr_str, round(INP, 2)
                ])

            # Simpan File CSV Output
            with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['No', 'Nama Jenis (Ilmiah)', 'K (ind/ha)', 'KR (%)', 'F', 'FR (%)', 'D (m2/ha)', 'DR (%)', 'INP (%)'])
                writer.writerows(csv_rows)

            # Hitung akumulasi metrik per plot_id HANYA UNTUK SPESIES UNIK (mencegah penghitungan ganda)
            plot_metric_sums = {m: {} for m in selected_metrics}
            counted_plot_species = set()

            for feat in layer.getFeatures():
                stadium_val = str(feat[f_stadium]).strip() if feat[f_stadium] is not None else ""
                if stadium_val.lower() != stadium_target.lower():
                    continue
                if aoi_geometry and not aoi_geometry.contains(feat.geometry()):
                    continue

                p_id = str(feat[f_plot]).strip()
                sp = str(feat[f_spesies]).strip()

                if sp in species_metrics and (p_id, sp) not in counted_plot_species:
                    counted_plot_species.add((p_id, sp))
                    for metric in selected_metrics:
                        if p_id not in plot_metric_sums[metric]:
                            plot_metric_sums[metric][p_id] = 0.0
                        plot_metric_sums[metric][p_id] += species_metrics[sp][metric]

            # Geometri unik per plot
            plot_geometries = {}
            for feat in layer.getFeatures():
                stadium_val = str(feat[f_stadium]).strip() if feat[f_stadium] is not None else ""
                if stadium_val.lower() != stadium_target.lower():
                    continue
                if aoi_geometry and not aoi_geometry.contains(feat.geometry()):
                    continue
                p_id = str(feat[f_plot]).strip()
                if p_id not in plot_geometries:
                    plot_geometries[p_id] = feat.geometry()

            # Buat Temporary GeoPackage
            temp_dir = tempfile.gettempdir()
            temp_gpkg_path = os.path.join(temp_dir, f"temp_metrics_{stadium_target}.gpkg")

            if os.path.exists(temp_gpkg_path):
                try:
                    os.remove(temp_gpkg_path)
                except PermissionError:
                    pass

            crs_id = layer.crs()
            fields = QgsFields()
            for m in selected_metrics:
                fields.append(QgsField(f"{m}_Plot", QVariant.Double))

            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "GPKG"
            options.fileEncoding = "UTF-8"
            
            transform_context = QgsProject.instance().transformContext()
            
            temp_writer = QgsVectorFileWriter.create(
                temp_gpkg_path,
                fields,
                layer.wkbType(),
                crs_id,
                transform_context,
                options
            )

            if temp_writer.hasError() != QgsVectorFileWriter.WriterError.NoError:
                raise RuntimeError(f"Gagal membuat file GeoPackage sementara: {temp_writer.errorMessage()}")

            field_indices = {m: idx for idx, m in enumerate(selected_metrics)}

            for p_id, geom in plot_geometries.items():
                has_metric = any(p_id in plot_metric_sums[m] for m in selected_metrics)
                if not has_metric:
                    continue
                
                fet = QgsFeature(fields)
                fet.setGeometry(geom)
                
                attributes = [round(plot_metric_sums[metric].get(p_id, 0.0), 2) for metric in selected_metrics]
                fet.setAttributes(attributes)
                temp_writer.addFeature(fet)

            del temp_writer  
            
            temp_plot_layer = QgsVectorLayer(temp_gpkg_path, f"Temp_Metrics_{stadium_target}", "ogr")

            # Interpolasi IDW
            for metric in selected_metrics:
                field_idx = field_indices[metric]
                target_extent = aoi_layer.extent() if aoi_layer else layer.extent()

                params = {
                    'INTERPOLATION_DATA': f"{temp_plot_layer.source()}::~::0::~::{field_idx}::~::0",
                    'DISTANCE_COEFFICIENT': 2.0,
                    'EXTENT': target_extent,
                    'PIXEL_SIZE': pixel_size,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                }

                result = processing.run("qgis:idwinterpolation", params)
                raster_output_path = result['OUTPUT']

                if aoi_layer:
                    clip_params = {
                        'INPUT': raster_output_path,
                        'MASK': aoi_layer,
                        'CROP_TO_CUTLINE': True,
                        'OUTPUT': 'TEMPORARY_OUTPUT'
                    }
                    clip_result = processing.run("gdal:cliprasterbymasklayer", clip_params)
                    raster_output_path = clip_result['OUTPUT']

                raster_layer = QgsRasterLayer(raster_output_path, f"Interpolasi IDW {metric} ({stadium_target})")

                r_provider = raster_layer.dataProvider()
                stats = r_provider.bandStatistics(1, QgsRasterBandStats.Stats.All)

                color_items = [
                    QgsColorRampShader.ColorRampItem(stats.minimumValue, Qt.GlobalColor.yellow, f"{metric} Rendah"),
                    QgsColorRampShader.ColorRampItem((stats.minimumValue + stats.maximumValue) / 2, Qt.GlobalColor.green, f"{metric} Sedang"),
                    QgsColorRampShader.ColorRampItem(stats.maximumValue, Qt.GlobalColor.darkGreen, f"{metric} Tinggi")
                ]

                shader = QgsRasterShader()
                color_shader = QgsColorRampShader()
                color_shader.setColorRampType(QgsColorRampShader.Type.Interpolated)
                color_shader.setColorRampItemList(color_items)
                shader.setRasterShaderFunction(color_shader)

                renderer = QgsSingleBandPseudoColorRenderer(r_provider, 1, shader)
                raster_layer.setRenderer(renderer)

                QgsProject.instance().addMapLayer(raster_layer)

            self.iface.messageBar().pushMessage(
                "Sukses", 
                f"Analisis selesai! CSV tersimpan dan {len(selected_metrics)} raster interpolasi IDW berhasil dibuat.", 
                level=3
            )

        except Exception as e:
            QMessageBox.critical(self.dlg, "Error Eksekusi", str(e))