# Whisper for Windows: Accurate, Local, GPU-Accelerated Audio Transcription

**Whisper for Windows** is a user-friendly desktop application that brings the power of OpenAI's Whisper models directly to your Windows PC. It allows you to accurately transcribe audio files locally, ensuring privacy and control over your data. A key feature is its robust **NVIDIA CUDA support**, enabling significantly faster transcriptions by leveraging your GPU's processing power. The application intelligently manages dependencies, including dynamic selection of the most compatible PyTorch CUDA version for your hardware, ensuring a smooth experience even with an embedded Python environment.

<img src="https://github.com/user-attachments/assets/b1fbeaec-ad09-4a6a-9cad-ac644d9e7ff8" width="333">

## Key Features:
*   **Local Transcription**: Process audio files on your own machine, no internet connection required after initial model download.
*   **High Accuracy**: Utilizes OpenAI's state-of-the-art Whisper models (tiny, base, small, medium, large) for precise speech-to-text conversion.
*   **NVIDIA GPU Acceleration**: Dynamically detects your CUDA version and installs the optimal PyTorch build for significantly faster processing on compatible NVIDIA GPUs.
*   **CPU Fallback**: Works efficiently on systems without a dedicated NVIDIA GPU by using CPU-based PyTorch.
*   **Multiple Audio Formats**: Supports common audio files like MP3, WAV, M4A, FLAC, and OGG.
*   **Versatile Output Formats**: Save transcriptions as plain text, SRT, VTT, Word Timestamps, or JSON.
*   **User-Friendly Interface**: Simple and intuitive GUI for easy file management and transcription.
*   **Efficient Dependency Management**: Smart flag system in the embedded version minimizes re-installation of packages, saving time and bandwidth.
*   **FFmpeg Integration**: Bundled FFmpeg for robust audio file handling.

# Download the recent releases:

## [Download Windows installer_x64](https://drive.google.com/file/d/1Ee-vesuzrYWkYWEuq1S1sBFmca5_wZBb/view?usp=sharing)
## [Download Windows installer_x32](https://drive.google.com/file/d/1NkNoxtngnxjCsYrEZ_uLLss8-m9zNuWA/view?usp=sharing)
## [Download Windows installer_ARM](https://drive.google.com/file/d/1NkNoxtngnxjCsYrEZ_uLLss8-m9zNuWA/view?usp=sharing)

## Demo

[[Whisper Transcriber Demo]](https://youtu.be/e_6lQ-FR7Wk)

*Click the image above to watch the demo video*

## Release Notes

See [RELEASE_NOTES.md](RELEASE_NOTES.md) for details on the latest changes and features.

## Prerequisites

Before installing Whisper Transcriber, please ensure you have the following installed:

1. **Python 3.8 to 3.12** - [Download from Python.org](https://www.python.org/downloads/)
   - During installation, make sure to check "Add Python to PATH"
   - Python 3.12 is recommended for optimal performance
   - Python 3.7 and earlier are not supported
   - Python 3.13+ has not been tested and may not be compatible

2. **Microsoft Visual C++ Redistributable 2015-2022 (x64)** - [Download from Microsoft](https://aka.ms/vs/17/release/vc_redist.x64.exe)
   - This is required for PyQt6 and other dependencies to work properly
   - Without this, you may see "Microsoft Visual C++ 14.0 or greater is required" errors

3. **NVIDIA CUDA Toolkit** (Optional, for GPU acceleration only)
   - Only needed if you want to use GPU acceleration
   - The app will guide you through installation if you choose to use GPU features

The installer will check for these prerequisites and guide you through installing any that are missing.

## Features
- Transcribe audio files (mp3, wav, m4a, flac, ogg) to text
- Multiple Whisper model options (tiny, base, small, medium, large)
- GPU acceleration support with on-demand CUDA installation
- Multiple output formats: Plain text, SRT subtitles, VTT subtitles, Word timestamps, and JSON
- Real-time progress tracking with detailed status updates
- Terminal progress bar for monitoring long transcriptions
- Save transcriptions to various file formats

## Installation

### Option 1: Download the installer
1. Go to the [Releases](https://github.com/yourusername/whisper-for-windows/releases) page
2. Download the latest `WhisperTranscriber_Setup.exe`
3. Run the installer and follow the prompts
4. The installer will check for prerequisites and help you install any that are missing

### Option 2: Download the portable executable
1. Go to the [Releases](https://github.com/yourusername/whisper-for-windows/releases) page
2. Download the latest `Whisper Transcriber.exe`
3. Run the executable directly (no installation required)
4. Note: You'll still need to manually install the prerequisites listed above

## GPU Acceleration

### How GPU Acceleration Works
This application supports GPU acceleration to significantly speed up transcription times:

- **Small executable size**: The application ships without CUDA dependencies to keep the download small
- **On-demand installation**: If you want to use GPU acceleration:
  1. The application will detect if you have CUDA-capable hardware
  2. A GPU Setup Help button will appear if CUDA is not detected
  3. Follow the guided installation to set up NVIDIA drivers and CUDA
  4. After installation, the application will automatically detect and use your GPU

### Windows vs. Mac Differences
- **Windows**: Requires NVIDIA GPU with CUDA drivers (setup help is provided in the app)
- **Mac with Apple Silicon**: Uses Metal for GPU acceleration automatically (no setup required)

### GPU Requirements for Windows
- NVIDIA GPU with Compute Capability 3.5 or higher (most GPUs from 2014 onwards)
- NVIDIA Display Drivers
- CUDA Toolkit 11.8 (recommended)

## Development Setup
1. Clone the repository
   ```
   git clone https://github.com/yourusername/whisper-for-windows.git
   cd whisper-for-windows
   ```

2. Create and activate a virtual environment (optional but recommended)
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Run the application
   ```
   python src/run.py
   ```

## Using the Application

### Basic Usage
1. Add audio files using the "Add Audio Files" button
2. Select a Whisper model (tiny, base, small, medium, large)
   - Smaller models are faster but less accurate
   - Larger models are more accurate but require more resources
3. Choose your preferred output format
4. Click "Transcribe" to begin processing
5. Once complete, review the transcription in the output area
6. Click "Save Transcription" to save the result

### Available Output Formats
- **Text Only**: Simple text without timestamps (fastest)
- **SRT Subtitles**: Standard subtitle format with timestamps for video
- **VTT Subtitles**: Web-friendly subtitle format
- **Word Timestamps**: Shows timestamps for individual words
- **JSON Output**: Complete data in developer-friendly format

### First Run Note
On first use for each model, Whisper will download the model files from the internet. These are stored in:
- Windows: `C:\Users\<username>\.cache\whisper`
- File sizes range from ~75MB (tiny) to ~3GB (large)

### Dependency Installation and Flag Files (Embedded Version)
When using the version of the application built with an embedded Python environment (typically via `build_exe_embedded.py`), the `Run Whisper Transcriber.bat` script manages the installation of dependencies. To optimize subsequent launches, it uses flag files:

- **`_base_deps_installed.flag`**: Created after base dependencies (like PyQt6, numpy, librosa) are successfully installed. If this file exists, the script skips reinstalling these base packages.
- **`_whisper_installed.flag`**: Created after `openai-whisper` is successfully installed. If this file exists, its installation is skipped.
- **`_pytorch_configured.flag`**: Created after PyTorch (either CPU or a specific CUDA version) is successfully installed and configured. If this file exists, the script skips CUDA detection and the entire PyTorch installation/verification process.

**To force a re-installation of specific dependencies:**
- **All dependencies (including PyTorch reconfiguration)**: Delete all `_*.flag` files (e.g., `_base_deps_installed.flag`, `_whisper_installed.flag`, `_pytorch_configured.flag`) in the application's root directory (where `Run Whisper Transcriber.bat` is located).
- **Base dependencies only**: Delete `_base_deps_installed.flag`.
- **Whisper only**: Delete `_whisper_installed.flag`.
- **PyTorch only (will trigger CUDA re-detection and PyTorch re-installation)**: Delete `_pytorch_configured.flag`. The script will then redetect your CUDA version (if applicable) and install the appropriate PyTorch version, then recreate the `_pytorch_configured.flag`.

This system ensures that you only download and install packages when necessary, saving time and bandwidth on subsequent application starts.

## Building a Distributable Version

### Building Different Versions
You can build different versions of the application depending on your needs:

```
# Build a minimal version without CUDA (smallest download size)
python build_tiny.py

# Build with CUDA support included (larger but no separate CUDA installation needed)
python build_tiny.py --cuda

# Build a medium-sized version with the base model
python build_tiny.py --small

# Build from the spec file
python build_tiny.py --spec
```

The standard build excludes CUDA to keep the download size manageable. Users can install CUDA separately if they need GPU acceleration.

### Creating a Windows Installer
To create a professional installer for distribution:

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Build the executable first using the build script
3. Run Inno Setup and open the `installer.iss` file
4. Click "Compile" to create the installer
5. The installer will be created in the `release` folder as `WhisperTranscriber_Setup.exe`

### Manual build with PyInstaller
For advanced users who need more control:

```
# Basic build with Whisper assets included
pyinstaller --name "Whisper Transcriber" --windowed --add-data "path/to/whisper/assets;whisper/assets" src/run.py

# Build with debug information
pyinstaller --name "Whisper Transcriber" --windowed --debug=all src/run.py
```

## Distribution Checklist
Before distributing your application:

1. Test the executable thoroughly on a clean Windows system
2. Make sure all dependencies are included in the package
3. Check if antiviruses might flag your executable (false positive)
4. Consider signing the executable for better trust
5. Update version numbers in the installer script

## Troubleshooting

### GPU Acceleration Issues
- **GPU Setup Help**: Click this button in the application if GPU acceleration isn't available
- **NVIDIA Drivers**: Make sure you have the latest drivers from the [NVIDIA website](https://www.nvidia.com/Download/index.aspx)
- **CUDA Toolkit**: Install [CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-downloads) for best compatibility
- **System Restart**: After installing drivers or CUDA, restart your computer
- **Check GPU Status**: The application's status bar shows if your GPU is detected and enabled

### Build Issues
- If you encounter "missing Whisper assets" errors, use the `--spec` option with the build script
- For CUDA/GPU errors, check that you have the appropriate NVIDIA drivers installed
- If the executable is too large, use the default build mode instead of `--standard`

### Runtime Issues
- If you see "Failed to launch Triton kernels" warnings, these can be safely ignored
- If transcription seems stuck, check the terminal for progress updates
- Models are downloaded only once and cached for future use

### Common Solutions
- Ensure you have a working internet connection for first-time model downloads
- For GPU acceleration issues, make sure you have compatible NVIDIA hardware and drivers
- If experiencing crashes, try using a smaller model (tiny or base)
- Audio files should be clear and in supported formats (MP3, WAV, M4A, FLAC, OGG)
