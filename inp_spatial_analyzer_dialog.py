import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

UI_PATH = os.path.join(os.path.dirname(__file__), 'inp_spatial_analyzer_dialog_base.ui')
FORM_CLASS, _ = uic.loadUiType(UI_PATH)

class InpSpatialAnalyzerDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(InpSpatialAnalyzerDialog, self).__init__(parent)
        self.setupUi(self)
        
        # Hubungkan event saat pilihan stadium diubah
        if hasattr(self, 'comboBoxStadium'):
            self.comboBoxStadium.currentIndexChanged.connect(self.on_stadium_changed)
            # Pemanggilan awal agar UI langsung menyesuaikan saat dialog pertama kali terbuka
            self.on_stadium_changed()

    def on_stadium_changed(self):
        if not hasattr(self, 'comboBoxStadium'):
            return

        stadium = self.comboBoxStadium.currentText()
        
        # Ukuran plot default (m²)
        defaults = {
            "Pohon": 400.0,         # 20 x 20 m
            "Tiang": 100.0,         # 10 x 10 m
            "Pancang": 25.0,        # 5 x 5 m
            "Semai": 4.0,           # 2 x 2 m
            "Liana": 400.0,         # 20 x 20 m
            "Tumbuhan Bawah": 4.0   # 2 x 2 m
        }
        
        if hasattr(self, 'spinBoxLuasPlot'):
            self.spinBoxLuasPlot.setValue(defaults.get(stadium, 400.0))
        
        # Stadium tanpa data diameter
        without_dbh = ["Semai", "Liana", "Tumbuhan Bawah", "Pancang"]
        is_no_dbh = stadium in without_dbh
        
        if hasattr(self, 'chkDR'):
            self.chkDR.setChecked(not is_no_dbh)
            self.chkDR.setEnabled(not is_no_dbh)
            
        if hasattr(self, 'cmbFieldDbh'):
            self.cmbFieldDbh.setEnabled(not is_no_dbh)