# Background Music Remover

A desktop application that removes background music from videos while preserving vocals.

## Features

- User-friendly GUI interface
- Multiple time range processing
- Progress tracking
- Preserves video quality

## Prerequisites

### For Users
- Windows operating system
- FFmpeg installed and added to system PATH ([Download FFmpeg](https://ffmpeg.org/download.html))

### For Developers
- Python 3.8 or higher
- FFmpeg installed and added to system PATH

## Getting Started

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Usage

1. Click "Browse Video" to select your input video
2. Click "Save Output As" to choose where to save the processed video
3. Add time ranges where you want to remove background music
4. Click "Process Video" to start
5. Wait for processing to complete
6. Find your processed video at the specified output location

## Important Notes

- Make sure FFmpeg is installed and added to system PATH
- Processing time depends on video length and selected ranges
- Requires sufficient disk space for temporary files
- For best results, use videos with clear vocal tracks

## Troubleshooting

### Common Issues

1. "FFmpeg not found":
   - Install FFmpeg and add it to system PATH
   - Restart the application

2. "Processing failed":
   - Check available disk space
   - Ensure input video is not corrupted
   - Check if FFmpeg is properly installed

3. "Application won't start":
   - Ensure all dependencies are installed
   - Check Windows Event Viewer for error details

### Getting Help

If you encounter any issues:
1. Check the application logs in `%APPDATA%\BackgroundMusicRemover\app.log`
2. Create an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Log file contents

## License

MIT License - See LICENSE file for details