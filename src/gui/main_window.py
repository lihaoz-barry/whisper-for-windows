from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QComboBox, QFileDialog, QProgressBar, QTextEdit,
    QListWidget, QLabel, QMessageBox, QStatusBar,
    QHBoxLayout, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDir
import whisper
import os
import warnings
import torch
import time
import pathlib
import threading
import sys
import json
from datetime import timedelta
import configparser

# Filter out specific Whisper warnings about Triton kernels
warnings.filterwarnings("ignore", message="Failed to launch Triton kernels")

# App settings
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".whisper_transcriber_settings.ini")

def save_settings(settings_dict):
    """Save application settings to config file"""
    config = configparser.ConfigParser()
    config['Settings'] = settings_dict
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def load_settings():
    """Load application settings from config file"""
    default_settings = {
        'use_gpu': 'True' if torch.cuda.is_available() else 'False'
    }
    
    if not os.path.exists(CONFIG_FILE):
        return default_settings
    
    config = configparser.ConfigParser()
    try:
        config.read(CONFIG_FILE)
        settings = dict(config['Settings']) if 'Settings' in config else {}
        
        # Validate settings
        if 'use_gpu' not in settings:
            settings['use_gpu'] = default_settings['use_gpu']
            
        return settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        return default_settings

# Dictionary of transcription format options
TRANSCRIPTION_FORMATS = {
    "Text Only": {
        "description": "Simple text without timestamps or special formatting",
        "options": {"word_timestamps": False, "verbose": False},
        "output_format": "text"  # Plain text output
    },
    "SRT Subtitles": {
        "description": "Standard subtitle format with timestamps",
        "options": {"word_timestamps": False, "verbose": True},
        "output_format": "srt"  # SRT format
    },
    "Word Timestamps": {
        "description": "Text with timestamps for each word",
        "options": {"word_timestamps": True, "verbose": False},
        "output_format": "word_timestamps"  # Word-level timestamps
    },
    "JSON Output": {
        "description": "Complete data in JSON format for developers",
        "options": {"word_timestamps": True, "verbose": True},
        "output_format": "json"  # Raw JSON output
    },
    "VTT Subtitles": {
        "description": "WebVTT subtitle format for web videos",
        "options": {"word_timestamps": False, "verbose": True},
        "output_format": "vtt"  # VTT subtitle format
    }
}

def format_timestamp(seconds, always_include_hours=False, decimal_marker='.'):
    """Convert seconds to HH:MM:SS.MS format"""
    hours = int(seconds / 3600)
    seconds = seconds - (hours * 3600)
    minutes = int(seconds / 60)
    seconds = seconds - (minutes * 60)
    
    if always_include_hours or hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace('.', decimal_marker)
    else:
        return f"{minutes:02d}:{seconds:06.3f}".replace('.', decimal_marker)

def format_srt(segments):
    """Format segments as SRT subtitle format"""
    srt_content = ""
    for i, segment in enumerate(segments, start=1):
        # Format: sequential number, timestamp range, text content, blank line
        start = format_timestamp(segment['start'], always_include_hours=True, decimal_marker=',')
        end = format_timestamp(segment['end'], always_include_hours=True, decimal_marker=',')
        srt_content += f"{i}\n{start} --> {end}\n{segment['text'].strip()}\n\n"
    return srt_content

def format_vtt(segments):
    """Format segments as WebVTT subtitle format"""
    vtt_content = "WEBVTT\n\n"
    for i, segment in enumerate(segments, start=1):
        start = format_timestamp(segment['start'], always_include_hours=True)
        end = format_timestamp(segment['end'], always_include_hours=True)
        vtt_content += f"{start} --> {end}\n{segment['text'].strip()}\n\n"
    return vtt_content

def format_word_timestamps(result):
    """Format result with word-level timestamps"""
    if not result.get('segments'):
        return "No word timestamps available in results."
    
    formatted_text = ""
    for segment in result['segments']:
        if 'words' in segment:
            for word in segment['words']:
                timestamp = format_timestamp(word['start'])
                formatted_text += f"[{timestamp}] {word['word']} "
            formatted_text += "\n"
        else:
            # Fallback if word timestamps aren't available
            start = format_timestamp(segment['start'])
            formatted_text += f"[{start}] {segment['text'].strip()}\n"
    
    return formatted_text

def get_cuda_details():
    """Get detailed CUDA capabilities information if available"""
    cuda_info = {
        'available': False,
        'version': None,
        'device_count': 0,
        'device_name': None,
        'compute_capability': None,
        'memory_gb': None
    }
    
    # Try to get CUDA info from PyTorch first
    try:
        cuda_info['available'] = torch.cuda.is_available()
        
        if cuda_info['available']:
            cuda_info['device_count'] = torch.cuda.device_count()
            
            if cuda_info['device_count'] > 0:
                cuda_info['device_name'] = torch.cuda.get_device_name(0)
                
                # Get compute capability and other detailed info
                try:
                    props = torch.cuda.get_device_properties(0)
                    cuda_info['compute_capability'] = f"{props.major}.{props.minor}"
                    cuda_info['memory_gb'] = round(props.total_memory / (1024**3), 1)
                except Exception as e:
                    print(f"Could not get detailed GPU properties from PyTorch: {e}")
    except Exception as e:
        print(f"Error getting CUDA information from PyTorch: {e}")
    
    # Try to get CUDA version using a simpler approach with nvidia-smi
    try:
        import subprocess
        import re
        import os
        import shutil
        
        # Check if nvidia-smi is available using shutil.which
        nvidia_smi_path = shutil.which("nvidia-smi")
        if nvidia_smi_path:
            print(f"Found nvidia-smi at: {nvidia_smi_path}")
            
            # First try a simple call with no arguments to verify it works
            try:
                result = subprocess.run([nvidia_smi_path], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("Basic nvidia-smi call succeeded")
                    
                    # Extract CUDA version from the direct output (which contains a header with the version)
                    version_match = re.search(r"CUDA Version: (\d+\.\d+)", result.stdout)
                    if version_match:
                        cuda_info['version'] = version_match.group(1)
                        print(f"Extracted CUDA version from nvidia-smi output: {cuda_info['version']}")
                    else:
                        # Fallback to the query approach if version not found in basic output
                        try:
                            # Try with explicit arguments
                            query_result = subprocess.run(
                                [nvidia_smi_path, "--query-gpu=cuda_version", "--format=csv,noheader"],
                                capture_output=True, text=True, timeout=5
                            )
                            if query_result.returncode == 0 and query_result.stdout.strip():
                                cuda_info['version'] = query_result.stdout.strip()
                                print(f"Got CUDA version via query: {cuda_info['version']}")
                        except Exception as e:
                            print(f"Query attempt failed: {e}")
                else:
                    print(f"Basic nvidia-smi call failed with error: {result.stderr}")
            except subprocess.TimeoutExpired:
                print("nvidia-smi command timed out")
            except Exception as e:
                print(f"Error running basic nvidia-smi: {e}")
        else:
            print("nvidia-smi not found in PATH")
            
            # Try looking for it manually in common locations
            possible_paths = [
                os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'NVIDIA Corporation\\NVSMI\\nvidia-smi.exe'),
                os.path.join(os.environ.get('ProgramW6432', 'C:\\Program Files'), 'NVIDIA Corporation\\NVSMI\\nvidia-smi.exe')
            ]
            
            for possible_path in possible_paths:
                if os.path.exists(possible_path):
                    print(f"Found nvidia-smi at: {possible_path}")
                    try:
                        result = subprocess.run([possible_path], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            print("nvidia-smi call succeeded")
                            
                            # Extract CUDA version from output
                            version_match = re.search(r"CUDA Version: (\d+\.\d+)", result.stdout)
                            if version_match:
                                cuda_info['version'] = version_match.group(1)
                                print(f"Extracted CUDA version from nvidia-smi output: {cuda_info['version']}")
                                break
                    except Exception as e:
                        print(f"Error running nvidia-smi from {possible_path}: {e}")
    except Exception as e:
        print(f"Error in nvidia-smi detection: {e}")
        
    print(f"CUDA detection summary: Available={cuda_info['available']}, Version={cuda_info['version']}, Device={cuda_info['device_name']}")
    return cuda_info

# Terminal progress bar helper class
class TerminalProgressBar:
    def __init__(self, title="Progress", total=100, width=50, show_percent=True, show_time=True):
        self.title = title
        self.total = total
        self.width = width
        self.show_percent = show_percent
        self.show_time = show_time
        self.start_time = time.time()
        self.last_update_time = 0
        self.update_interval = 0.1  # Update terminal every 0.1 seconds to avoid flickering

    def update(self, current):
        # Limit terminal updates to avoid flickering
        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval:
            return
        
        self.last_update_time = current_time
        percent = min(100, int((current / self.total) * 100))
        filled_width = int(self.width * current / self.total)
        bar = '█' * filled_width + '-' * (self.width - filled_width)
        elapsed = current_time - self.start_time
        
        # Prepare the progress line
        line = f"\r{self.title}: |{bar}|"
        
        if self.show_percent:
            line += f" {percent}%"
            
        if self.show_time:
            line += f" [{elapsed:.1f}s]"
            
        # Print the progress bar with carriage return to stay on the same line
        print(line, end='', flush=True)
        
        # Add a newline when completed
        if current >= self.total:
            print()

class TranscriptionWorker(QThread):
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    finished = pyqtSignal(object)  # Changed to return the complete result object
    error = pyqtSignal(str)

    def __init__(self, model_name, audio_file, use_gpu=None, show_terminal_progress=True):
        super().__init__()
        self.model_name = model_name
        # Normalize the file path to handle Windows paths properly and ensure it's an absolute path
        self.audio_file = os.path.abspath(os.path.normpath(audio_file))
        
        # Print debug info about the file
        print(f"Audio file path: {self.audio_file}")
        print(f"File exists: {os.path.exists(self.audio_file)}")
        
        # Determine device to use based on user preference and availability
        self.use_gpu = use_gpu if use_gpu is not None else torch.cuda.is_available()
        self.gpu_available = torch.cuda.is_available()
        
        # Only use GPU if both requested and available
        if self.use_gpu and self.gpu_available:
            self.device = "cuda"
        else:
            self.device = "cpu"
            
        self.is_running = True
        self.show_terminal_progress = show_terminal_progress
        self.terminal_progress_bar = None
        self.format_options = {}  # Initialize format options with default empty dict
        self.output_format = "text"  # Default output format

    def check_model_exists(self):
        """Check if the model already exists in the cache directory"""
        # Get the cache directory path for whisper models
        home_dir = pathlib.Path.home()
        cache_dir = home_dir / '.cache' / 'whisper'
        # Model filename follows pattern: <model_name>.pt
        model_path = cache_dir / f"{self.model_name}.pt"
        return model_path.exists()

    def progress_monitor(self, start_time, estimated_duration):
        """Run progress updates in the background"""
        last_progress = 0
        
        # Create terminal progress bar if enabled
        if self.show_terminal_progress:
            self.terminal_progress_bar = TerminalProgressBar(
                title=f"Transcribing with {self.model_name} model",
                total=100,
                width=40,
                show_percent=True,
                show_time=True
            )
            print(f"\nProcessing file: {os.path.basename(self.audio_file)}")
            print(f"Model: {self.model_name} | Device: {self.device}")
            
        while self.is_running and last_progress < 90:
            elapsed = time.time() - start_time
            # Map the elapsed time to a percentage between 50-90%
            if elapsed < estimated_duration:
                progress_percent = min(int(50 + (elapsed / estimated_duration) * 40), 90)
                self.progress.emit(progress_percent)
                est_percent = min(int((elapsed / estimated_duration) * 100), 99)
                status_msg = f"Transcribing... (estimated {est_percent}% complete)"
                self.status_update.emit(status_msg)
                
                # Update terminal progress bar if enabled
                if self.show_terminal_progress and self.terminal_progress_bar:
                    self.terminal_progress_bar.update(progress_percent)
                
                last_progress = progress_percent
            time.sleep(0.5)  # Update every half second

    def run(self):
        try:
            self.is_running = True
            self.status_update.emit("Initializing transcription...")
            self.progress.emit(5)
            
            # Terminal output for initialization
            if self.show_terminal_progress:
                print(f"\n=== Whisper Transcriber ===")
                print(f"Initializing {self.model_name} model...")
            
            # Check if model exists or needs to be downloaded
            model_exists = self.check_model_exists()
            if not model_exists:
                download_msg = f"Downloading {self.model_name} model (this may take a while)..."
                self.status_update.emit(download_msg)
                if self.show_terminal_progress:
                    print(f"\n{download_msg}")
                self.progress.emit(10)
            else:
                loading_msg = f"Loading {self.model_name} model..."
                self.status_update.emit(loading_msg)
                if self.show_terminal_progress:
                    print(f"\n{loading_msg}")
                self.progress.emit(10)
            
            # Load model - this will download it if not available
            start_time = time.time()
            model = whisper.load_model(self.model_name).to(self.device)
            load_time = time.time() - start_time
            
            loaded_msg = f"Model loaded in {load_time:.1f}s. Preparing audio..."
            self.status_update.emit(loaded_msg)
            if self.show_terminal_progress:
                print(loaded_msg)
            self.progress.emit(30)
            
            # Audio loading indication
            audio_msg = "Processing audio file..."
            self.status_update.emit(audio_msg)
            if self.show_terminal_progress:
                print(audio_msg)
            self.progress.emit(40)
            
            # Use manual time-based progress updates instead
            begin_msg = "Beginning transcription..."
            self.status_update.emit(begin_msg)
            if self.show_terminal_progress:
                print(begin_msg)
            self.progress.emit(50)
            
            # Start the transcription
            start_time = time.time()
            
            # Estimate duration based on file size and model size
            try:
                file_size_mb = os.path.getsize(self.audio_file) / (1024 * 1024)
                # Adjust based on model size (larger models are slower)
                model_factor = {'tiny': 0.5, 'base': 1.0, 'small': 2.0, 'medium': 3.0, 'large': 5.0}
                model_speed = model_factor.get(self.model_name, 1.0)
                # Rough estimate: 10 seconds per MB * model factor, with minimum of 10 seconds
                estimated_duration = max(10, file_size_mb * 10 * model_speed)
            except:
                # Default if we can't estimate
                estimated_duration = 60  # seconds
            
            # Start a thread to monitor progress
            monitor_thread = threading.Thread(
                target=self.progress_monitor, 
                args=(start_time, estimated_duration)
            )
            monitor_thread.daemon = True  # This ensures the thread exits when the main thread exits
            monitor_thread.start()
            
            # Double check that file exists before transcribing
            if not os.path.exists(self.audio_file):
                raise FileNotFoundError(f"File not found: {self.audio_file}")
            
            # Wrap the file loading with a custom loader to handle paths more reliably
            try:
                # Try to preload the audio before passing to whisper
                import numpy as np
                import subprocess
                
                # Log what we're about to do
                print(f"Using audio file path: {self.audio_file}")

                # Create a custom audio data loader to bypass the potential path issues
                def custom_audio_loader():
                    """Custom function to load audio data from file and return as numpy array"""
                    try:
                        # Check if FFmpeg is available
                        from shutil import which
                        ffmpeg_path = which("ffmpeg")
                        if not ffmpeg_path:
                            print("Warning: FFmpeg not found in PATH, will rely on Whisper's internal audio loading")
                            return None  # Let whisper handle it
                            
                        # Ensure absolute file path with proper slashes for Windows
                        file_path = os.path.abspath(self.audio_file).replace('\\', '/')
                        
                        # Set up the FFmpeg command for proper audio conversion
                        # Similar to what whisper.audio.load_audio does
                        cmd = [
                            "ffmpeg",
                            "-nostdin",
                            "-threads", "0",
                            "-i", file_path,
                            "-f", "s16le",
                            "-ac", "1",
                            "-acodec", "pcm_s16le",
                            "-ar", "16000",
                            "-"
                        ]
                        
                        # Run FFmpeg and get the audio data
                        print(f"Running FFmpeg command to load audio data")
                        process = subprocess.run(cmd, capture_output=True, check=True)
                        audio_data = np.frombuffer(process.stdout, np.int16).flatten().astype(np.float32) / 32768.0
                        print(f"Successfully loaded audio data: {len(audio_data)} samples")
                        return audio_data
                    except Exception as e:
                        print(f"Error in custom audio loader: {e}")
                        return None  # Let whisper handle it
                
                # Try to pre-load the audio
                audio_data = custom_audio_loader()
                
                # Run the actual transcription
                if audio_data is not None:
                    # If we successfully loaded the audio, use it directly
                    print("Using pre-loaded audio data for transcription")
                    result = model.transcribe(
                        audio_data,  # Pass the pre-loaded audio numpy array
                        fp16=(self.device == "cuda"),
                        **self.format_options  # Pass the format options to the transcribe method
                    )
                else:
                    # Fall back to the standard approach if our custom loader failed
                    print("Falling back to Whisper's audio loading")
                    # Use pathlib for safer path handling
                    audio_path = pathlib.Path(self.audio_file).resolve()
                    print(f"Resolved path: {audio_path}")
                    
                    result = model.transcribe(
                        str(audio_path),  # Ensure it's a string
                        fp16=(self.device == "cuda"),
                        **self.format_options  # Pass the format options to the transcribe method
                    )
            
            except Exception as e:
                print(f"ERROR: Transcription failed: {str(e)}")
                import traceback
                traceback.print_exc()
                self.is_running = False
                self.error.emit(f"Transcription failed: {str(e)}")
                return
            
            # Stop the progress monitor
            self.is_running = False
            
            # Finalize
            transcribe_time = time.time() - start_time
            complete_msg = f"Transcription completed in {transcribe_time:.1f}s. Finalizing..."
            self.progress.emit(95)
            self.status_update.emit(complete_msg)
            
            # Update terminal with completion status
            if self.show_terminal_progress:
                if self.terminal_progress_bar:
                    self.terminal_progress_bar.update(100)  # Complete the progress bar
                print(f"\n{complete_msg}")
                
                # If verbose mode, print some segments in the terminal
                if self.format_options.get('verbose', False) and 'segments' in result:
                    print("\nSample output (first few segments):")
                    # Get up to 3 segments to display as samples
                    sample_segments = result['segments'][:3] if isinstance(result['segments'], list) else []
                    
                    for i, segment in enumerate(sample_segments):
                        # Check if segment is a dictionary before attempting to access keys
                        if isinstance(segment, dict):
                            # Use safe dictionary access
                            start = format_timestamp(segment.get('start', 0))
                            end = format_timestamp(segment.get('end', 0))
                            text = segment.get('text', '').strip()
                            print(f"[{start} --> {end}]  {text}")
                        elif isinstance(segment, str):
                            # Handle case where segment is a string
                            print(f"Segment {i+1}: {segment}")
                        else:
                            # Handle any other type
                            print(f"Segment {i+1}: {str(segment)}")
                    print("...\n")
                
                # Safely get text length
                text_length = 0
                if isinstance(result, dict) and 'text' in result:
                    if isinstance(result['text'], str):
                        text_length = len(result['text'])
                    
                print(f"Output length: {text_length} characters")
                print("=" * 40)
            
            # Send the complete result object to the UI
            self.finished.emit(result)
            self.progress.emit(100)
            
        except Exception as e:
            self.is_running = False
            error_msg = str(e)
            self.error.emit(error_msg)
            
            # Display error in terminal too
            if self.show_terminal_progress:
                print(f"\nERROR: Transcription failed: {error_msg}")
                # Print traceback for debugging in terminal
                import traceback
                print(traceback.format_exc())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Whisper Transcriber")
        self.setMinimumSize(800, 600)
        
        # Load user settings
        self.settings = load_settings()
        
        # Get CUDA details
        self.cuda_info = get_cuda_details()
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # File selection area
        self.file_list = QListWidget()
        self.add_file_btn = QPushButton("Add Audio Files")
        self.add_file_btn.clicked.connect(self.add_audio_files)
        
        # Create settings group box
        settings_group = QGroupBox("Transcription Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        model_layout.addWidget(self.model_combo)
        settings_layout.addLayout(model_layout)
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        for format_name in TRANSCRIPTION_FORMATS.keys():
            self.format_combo.addItem(format_name)
        self.format_combo.setCurrentIndex(0)  # Default to "Text Only"
        self.format_combo.setToolTip("Select the transcription format and detail level")
        format_layout.addWidget(self.format_combo)
        settings_layout.addLayout(format_layout)
        
        # Format description label
        self.format_description = QLabel(TRANSCRIPTION_FORMATS["Text Only"]["description"])
        self.format_description.setStyleSheet("font-style: italic; color: #666;")
        settings_layout.addWidget(self.format_description)
        
        # GPU Acceleration option
        self.use_gpu_checkbox = QCheckBox("Use GPU acceleration (CUDA)")
        
        # Set initial checkbox state from saved settings
        try:
            use_gpu = self.settings.get('use_gpu', 'True').lower() == 'true'
        except:
            use_gpu = torch.cuda.is_available()
            
        self.use_gpu_checkbox.setChecked(use_gpu)
        
        # Disable checkbox if GPU is not available
        if not torch.cuda.is_available():
            self.use_gpu_checkbox.setEnabled(False)
            self.use_gpu_checkbox.setToolTip("GPU acceleration is not available on this system")
        else:
            gpu_name = torch.cuda.get_device_name(0)
            self.use_gpu_checkbox.setToolTip(f"Use GPU acceleration with {gpu_name}")
        
        # Connect checkbox state change to save settings
        self.use_gpu_checkbox.stateChanged.connect(self.save_gpu_setting)
        
        settings_layout.addWidget(self.use_gpu_checkbox)
        
        # Connect format combo change to update description
        self.format_combo.currentTextChanged.connect(self.update_format_description)
        
        # Add settings group to main layout
        layout.addWidget(settings_group)
        
        # Status bar to show GPU/CPU info
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Show GPU status in status bar
        if torch.cuda.is_available():
            device_info = f"GPU available: {torch.cuda.get_device_name(0)}"
            if use_gpu:
                device_info += " (enabled 🚀)"
            else:
                device_info += " (disabled ⚠️)"
        else:
            device_info = "GPU not available, using CPU"
        status_bar.showMessage(device_info)
        
        # Progress tracking
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.status_label = QLabel("Ready")
        
        # File selection area
        layout.addWidget(QLabel("Audio Files:"))
        layout.addWidget(self.file_list)
        layout.addWidget(self.add_file_btn)
        
        # Add progress indicators
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
        # Transcription output
        layout.addWidget(QLabel("Transcription Output:"))
        self.output_text = QTextEdit()
        layout.addWidget(self.output_text)
        
        # Controls
        button_layout = QHBoxLayout()
        self.transcribe_btn = QPushButton("Transcribe")
        self.transcribe_btn.clicked.connect(self.start_transcription)
        self.save_btn = QPushButton("Save Transcription")
        self.save_btn.clicked.connect(self.save_transcription)
        button_layout.addWidget(self.transcribe_btn)
        button_layout.addWidget(self.save_btn)
        layout.addLayout(button_layout)
        
        self.save_btn.setEnabled(False)
    
    def save_gpu_setting(self):
        """Save the GPU acceleration setting when changed"""
        use_gpu = self.use_gpu_checkbox.isChecked()
        self.settings['use_gpu'] = str(use_gpu)
        save_settings(self.settings)
        
        # Update status bar (fix: use the class variable instead of method)
        if torch.cuda.is_available():
            device_info = f"GPU available: {torch.cuda.get_device_name(0)}"
            if use_gpu:
                device_info += " (enabled 🚀)"
            else:
                device_info += " (disabled ⚠️)"
        else:
            device_info = "GPU not available, using CPU"
        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage(device_info)    
    def update_format_description(self, format_name):
        """Update the description when the format selection changes"""
        if format_name in TRANSCRIPTION_FORMATS:
            self.format_description.setText(TRANSCRIPTION_FORMATS[format_name]["description"])
    
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
        self.format_combo.setEnabled(False)
        self.use_gpu_checkbox.setEnabled(False)
        
        first_item = self.file_list.item(0)
        if (first_item is None):
            QMessageBox.warning(self, "No Files", "Please add audio files first.")
            self.enable_controls()
            return
        
        current_file = first_item.text()
        
        # Ensure we're using an absolute path and it exists
        current_file = os.path.abspath(current_file)
        if not os.path.exists(current_file):
            QMessageBox.warning(self, "File Not Found", f"The file '{current_file}' does not exist or cannot be accessed.")
            self.enable_controls()
            return
            
        # Debug: Print the file path to help with troubleshooting
        print(f"Attempting to transcribe file: {current_file}")
        
        model_name = self.model_combo.currentText()
        use_gpu = self.use_gpu_checkbox.isChecked()
        
        # Get selected format options
        format_name = self.format_combo.currentText()
        format_options = TRANSCRIPTION_FORMATS[format_name]["options"]
        output_format = TRANSCRIPTION_FORMATS[format_name]["output_format"]
        
        # Create worker with format options and GPU preference
        self.worker = TranscriptionWorker(model_name, current_file, use_gpu=use_gpu)
        self.worker.progress.connect(self.update_progress)
        self.worker.status_update.connect(self.update_status)
        self.worker.finished.connect(self.transcription_finished)
        self.worker.error.connect(self.transcription_error)
        
        # Store format options to use in the worker
        self.worker.format_options = format_options
        self.worker.output_format = output_format
        
        # Show device being used in status
        device_msg = f"Using {'GPU' if use_gpu and torch.cuda.is_available() else 'CPU'} for processing"
        self.status_label.setText(device_msg)
        
        self.worker.start()
        
        format_info = f" ({format_name})" if format_name != "Text Only" else ""
        self.status_label.setText(f"Transcribing{format_info}...")
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def update_status(self, message):
        self.status_label.setText(message)
    
    def transcription_finished(self, result):
        try:
            output_format = getattr(self.worker, 'output_format', 'text')
            formatted_text = ""
            
            # Ensure result is a dictionary
            if not isinstance(result, dict):
                formatted_text = str(result)
            else:
                if output_format == "srt" and 'segments' in result:
                    try:
                        formatted_text = format_srt(result['segments'])
                    except Exception as e:
                        formatted_text = f"Error formatting SRT: {str(e)}\n\n{result['text']}"
                
                elif output_format == "vtt" and 'segments' in result:
                    try:
                        formatted_text = format_vtt(result['segments'])
                    except Exception as e:
                        formatted_text = f"Error formatting VTT: {str(e)}\n\n{result['text']}"
                
                elif output_format == "word_timestamps":
                    try:
                        formatted_text = format_word_timestamps(result)
                    except Exception as e:
                        formatted_text = f"Error formatting word timestamps: {str(e)}\n\n{result['text']}"
                
                elif output_format == "json":
                    try:
                        formatted_text = json.dumps(result, indent=2)
                    except Exception as e:
                        formatted_text = f"Error formatting JSON: {str(e)}"
                
                else:  # Default to plain text
                    formatted_text = result.get("text", "No text output available")
                    
            self.output_text.setPlainText(formatted_text)
            self.status_label.setText("Transcription completed")
            self.enable_controls()
            self.save_btn.setEnabled(True)
            
        except Exception as e:
            error_msg = f"Error processing transcription results: {str(e)}"
            QMessageBox.warning(self, "Output Processing Error", error_msg)
            if 'text' in result and isinstance(result['text'], str):
                # Fallback to plain text if formatting fails
                self.output_text.setPlainText(result['text'])
            self.enable_controls()
    
    def transcription_error(self, error_message):
        QMessageBox.critical(self, "Error", f"Transcription failed: {error_message}")
        self.status_label.setText("Error occurred")
        self.enable_controls()
    
    def enable_controls(self):
        self.transcribe_btn.setEnabled(True)
        self.add_file_btn.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.format_combo.setEnabled(True)
        
        # Only enable GPU checkbox if GPU is available
        if torch.cuda.is_available():
            self.use_gpu_checkbox.setEnabled(True)
    
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