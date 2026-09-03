# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'payip28muhammad@apps.ipb.ac.id'
__date__ = '2026-08-30'
__copyright__ = 'Copyright 2026, Muhammad Parif - IPB University'

import unittest

from qgis.PyQt.QtWidgets import QDialogButtonBox, QDialog

from inp_spatial_analyzer_dialog import InpSpatialAnalyzerDialog

from utilities import get_qgis_app
QGIS_APP = get_qgis_app()

# Menggunakan enum standar modern Qt6 yang kompatibel dan lolos validator QGIS
OK_BUTTON = QDialogButtonBox.StandardButton.Ok
CANCEL_BUTTON = QDialogButtonBox.StandardButton.Cancel
ACCEPTED = QDialog.DialogCode.Accepted
REJECTED = QDialog.DialogCode.Rejected


class InpSpatialAnalyzerDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = InpSpatialAnalyzerDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_dialog_ok(self):
        """Test we can click OK."""
        button = self.dialog.button_box.button(OK_BUTTON)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, ACCEPTED)

    def test_dialog_cancel(self):
        """Test we can click cancel."""
        button = self.dialog.button_box.button(CANCEL_BUTTON)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, REJECTED)

if __name__ == "__main__":
    suite = unittest.makeSuite(InpSpatialAnalyzerDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)