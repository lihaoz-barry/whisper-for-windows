# Whisper Transcriber for Windows

A Windows desktop application for transcribing audio files using OpenAI's Whisper model.

## Features
- Transcribe audio files (mp3, wav, m4a, flac, ogg) to text
- Multiple Whisper model options (tiny, base, small, medium, large)
- GPU acceleration support
- Multiple output formats: Plain text, SRT subtitles, VTT subtitles, Word timestamps, and JSON
- Real-time progress tracking with detailed status updates
- Terminal progress bar for monitoring long transcriptions
- Save transcriptions to various file formats

## Installation

### Option 1: Download the installer
1. Go to the [Releases](https://github.com/yourusername/whisper-for-windows/releases) page
2. Download the latest `WhisperTranscriber_Setup.exe`
3. Run the installer and follow the prompts

### Option 2: Download the portable executable
1. Go to the [Releases](https://github.com/yourusername/whisper-for-windows/releases) page
2. Download the latest `Whisper Transcriber.exe`
3. Run the executable directly (no installation required)

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

## Building a Distributable Version

### Building with the included script
The simplest way to build an executable is to use the included build script:

```
# For optimized directory-based distribution (smaller size, recommended)
python build_exe.py

# For single-file executable (larger size)
python build_exe.py --standard

# Using the optimized spec file (recommended for most cases)
python build_exe.py --spec
```

The script will:
1. Check for PyInstaller and install it if needed
2. Package the application and all dependencies
3. Include the necessary Whisper assets
4. Place the result in the `dist` folder

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