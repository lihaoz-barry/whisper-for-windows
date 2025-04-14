from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QComboBox, QFileDialog, QProgressBar, QTextEdit,
    QListWidget, QLabel, QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import whisper
import os
import warnings
import torch

class TranscriptionWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, model_name, audio_file):
        super().__init__()
        self.model_name = model_name
        self.audio_file = audio_file
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def run(self):
        try:
            self.progress.emit(10)
            model = whisper.load_model(self.model_name).to(self.device)
            self.progress.emit(30)
            
            result = model.transcribe(
                self.audio_file,
                fp16=self.device == "cuda"  # Use FP16 only when on GPU
            )
            self.progress.emit(90)
            
            self.finished.emit(result["text"])
            self.progress.emit(100)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Whisper Transcriber")
        self.setMinimumSize(800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # File selection area
        self.file_list = QListWidget()
        self.add_file_btn = QPushButton("Add Audio Files")
        self.add_file_btn.clicked.connect(self.add_audio_files)
        
        # Model selection
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        
        # Status bar to show GPU/CPU info
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Show GPU status in status bar
        device_info = "Using GPU 🚀" if torch.cuda.is_available() else "Using CPU"
        if torch.cuda.is_available():
            device_info += f" ({torch.cuda.get_device_name(0)})"
        status_bar.showMessage(device_info)
        
        # Progress tracking
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.status_label = QLabel("Ready")
        
        # Transcription output
        self.output_text = QTextEdit()
        
        # Controls
        self.transcribe_btn = QPushButton("Transcribe")
        self.transcribe_btn.clicked.connect(self.start_transcription)
        self.save_btn = QPushButton("Save Transcription")
        self.save_btn.clicked.connect(self.save_transcription)
        
        # Add widgets to layout
        layout.addWidget(QLabel("Audio Files:"))
        layout.addWidget(self.file_list)
        layout.addWidget(self.add_file_btn)
        layout.addWidget(QLabel("Select Whisper Model:"))
        layout.addWidget(self.model_combo)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel("Transcription Output:"))
        layout.addWidget(self.output_text)
        layout.addWidget(self.transcribe_btn)
        layout.addWidget(self.save_btn)
        
        self.save_btn.setEnabled(False)
    
    def add_audio_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio Files",
            "",
            "Audio Files (*.mp3 *.wav *.m4a *.flac *.ogg)"
        )
        if files:
            self.file_list.addItems(files)
    
    def start_transcription(self):
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "No Files", "Please add audio files first.")
            return
            
        self.transcribe_btn.setEnabled(False)
        self.add_file_btn.setEnabled(False)
        self.model_combo.setEnabled(False)
        
        first_item = self.file_list.item(0)
        if (first_item is None):
            QMessageBox.warning(self, "No Files", "Please add audio files first.")
            self.enable_controls()
            return
        current_file = first_item.text()
        model_name = self.model_combo.currentText()
        
        self.worker = TranscriptionWorker(model_name, current_file)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.transcription_finished)
        self.worker.error.connect(self.transcription_error)
        self.worker.start()
        
        self.status_label.setText("Transcribing...")
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def transcription_finished(self, text):
        self.output_text.setPlainText(text)
        self.status_label.setText("Transcription completed")
        self.enable_controls()
        self.save_btn.setEnabled(True)
    
    def transcription_error(self, error_message):
        QMessageBox.critical(self, "Error", f"Transcription failed: {error_message}")
        self.status_label.setText("Error occurred")
        self.enable_controls()
    
    def enable_controls(self):
        self.transcribe_btn.setEnabled(True)
        self.add_file_btn.setEnabled(True)
        self.model_combo.setEnabled(True)
    
    def save_transcription(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Transcription",
            "",
            "Text Files (*.txt);;SubRip Subtitle (*.srt);;Word Document (*.docx)"
        )
        if file_name:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(self.output_text.toPlainText())