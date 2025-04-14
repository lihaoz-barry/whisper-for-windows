import sys
import unittest
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow

class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)
        cls.window = MainWindow()

    def test_window_title(self):
        self.assertEqual(self.window.windowTitle(), "Whisper Transcriber")

    def test_model_selection(self):
        models = ["tiny", "base", "small", "medium", "large"]
        for i, model in enumerate(models):
            self.assertEqual(self.window.model_combo.itemText(i), model)

    def test_initial_state(self):
        self.assertFalse(self.window.save_btn.isEnabled())
        self.assertEqual(self.window.status_label.text(), "Ready")
        self.assertEqual(self.window.file_list.count(), 0)

if __name__ == '__main__':
    unittest.main()