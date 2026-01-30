# Installation Guide

## Prerequisites

- Windows 10 or 11
- Python 3.8 or higher (for source installation)
- Administrator privileges (for keyboard hooks)

## Installation Methods

### Option 1: Download Executable (Recommended for Users)

1. Go to [Releases](https://github.com/YOUR_USERNAME/peak-aim-assistant/releases)
2. Download the latest `PeakAimAssistant.exe`
3. Run the executable
4. Windows may show a security warning - click "More info" → "Run anyway"

### Option 2: Install from Source (Recommended for Developers)

1. **Install Python**
```bash
   # Download from https://www.python.org/downloads/
   # Make sure to check "Add Python to PATH"
```

2. **Clone Repository**
```bash
   git clone https://github.com/YOUR_USERNAME/peak-aim-assistant.git
   cd peak-aim-assistant
```

3. **Create Virtual Environment (Optional but Recommended)**
```bash
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on Linux/Mac
   source venv/bin/activate
```

4. **Install Dependencies**
```bash
   pip install -r requirements.txt
```

5. **Run Application**
```bash
   python peak_aim_assistant.py
```

## Building Executable

To create your own executable:
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --icon=icon.ico --name=PeakAimAssistant peak_aim_assistant.py

# Executable will be in dist/ folder
```

## Troubleshooting

### "Python is not recognized"
- Reinstall Python and check "Add Python to PATH"
- Restart your terminal/command prompt

### "Access Denied" or "Permission Error"
- Run terminal/command prompt as Administrator
- Windows Defender may block keyboard hooks

### "DLL load failed"
- Install Visual C++ Redistributable
- Download from Microsoft's website

### App doesn't start
- Check Windows Event Viewer for errors
- Run from command prompt to see error messages

## First Run

1. Application will create `settings.json` in the same directory
2. Configure overlay position
3. Test in GameLoop before using in games
