# Whisper Transcriber Release Notes

## Version 1.1.0 (April 15, 2025)

This release introduces significant improvements to the Whisper Transcriber application, enhancing its functionality, usability, and development workflow.

### New Features

- **Multiple Output Formats**: Added support for various transcription output formats:
  - Text Only: Simple text without timestamps or special formatting
  - SRT Subtitles: Standard subtitle format with timestamps
  - Word Timestamps: Text with timestamps for each word
  - JSON Output: Complete data in JSON format for developers
  - VTT Subtitles: WebVTT subtitle format for web videos

- **GPU/CPU Processing Choice**: Enhanced control over processing hardware:
  - Option to manually select between GPU and CPU processing
  - User preference for GPU usage is now saved between sessions
  - Clear indication of GPU status in the user interface
  - Automatic detection of CUDA compatibility

- **Multi-Format Audio Support**: Expanded support for various audio formats:
  - MP3, WAV, M4A, FLAC, OGG formats supported natively
  - No need for external audio conversion tools

- **Automatic Language Detection**: Leverages Whisper's language detection capabilities:
  - Automatically identifies the spoken language in audio files
  - Supports multilingual content without manual configuration

- **VS Code Integration**: Added development workflow improvements:
  - VS Code tasks for building, running, and debugging
  - Improved project configuration for developers

### Enhancements

- **Model Selection**: Improved model selection interface:
  - Choose between tiny, base, small, medium, and large Whisper models
  - Balance between speed and accuracy based on your needs
  - Clear indication of processing time estimates

- **User Interface Improvements**:
  - Added detailed format descriptions to help users choose the right output format
  - Improved progress monitoring with more accurate status updates
  - Enhanced terminal output for better diagnostics
  - Status bar displaying current GPU/CPU configuration

- **Settings System**:
  - Complete settings persistence between sessions
  - Configuration stored in user's home directory
  - Automatic loading of previous settings

- **File Handling**:
  - Better support for various audio formats
  - Improved file selection interface

### Bug Fixes

- Fixed issues with settings persistence
- Improved error handling during transcription
- Fixed progress bar accuracy issues

### Under the Hood

- Code refactoring for better maintainability
- Improved project structure
- Added Git configurations for development
- Enhanced terminal progress reporting for technical users

## Version 1.0.0 (Initial Release)

First working version of Whisper Transcriber with GPU support.

### Features

- Basic audio transcription using OpenAI's Whisper models
- Support for various model sizes (tiny, base, small, medium, large)
- GPU acceleration support (CUDA)
- Simple user interface for file selection and transcription
- Basic progress monitoring
- Ability to save transcription results