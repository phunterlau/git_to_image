# Git-to-Image UI

A retro Nintendo-style web interface for generating artistic portraits from GitHub profiles.

## Features

- 🎮 **Nintendo-style Theme**: Pixel art aesthetics with "Press Start 2P" font
- 🎨 **Text-to-Image Generation**: Create portraits based on GitHub profile analysis
- 🖼️ **Image-to-Image Generation**: Transform GitHub profile pictures using AI
- 📊 **Profile Analysis**: View detailed GitHub profile insights
- 💾 **Download Support**: Save generated images locally

## Quick Start

### Prerequisites

1. **Environment Variables**: Set up your API keys
   ```bash
   export GITHUB_TOKEN="your_github_token_here"
   export GEMINI_API_KEY="your_gemini_api_key_here"
   ```

2. **Python Dependencies**: The startup script will handle this automatically

### Running the UI

**Option 1: Using the startup script (Recommended)**
```bash
cd frontend
python run_ui.py
```

**Option 2: Direct Streamlit launch**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

The UI will open in your browser at `http://localhost:8501`

## Usage

1. **Enter GitHub Username**: Type any valid GitHub username
2. **Choose Generation Mode**:
   - **Text-to-Image**: Generate based on profile analysis
   - **Image-to-Image**: Transform your GitHub profile picture
3. **Select Options**: Choose "I feel lucky" for automatic generation or customize your options
4. **Generate**: Click the "🚀 GENERATE PORTRAIT" button
5. **Download**: Save your generated image

## UI Components

### Input Settings
- GitHub username input field
- Generation mode selection (radio buttons)
- Dynamic options based on selected mode

### Text-to-Image Options
- **🍀 I feel lucky (Let AI decide)**: Default option - let the backend automatically choose the best artistic style, character, and environment based on the GitHub profile analysis
- **🎯 Custom options**: Manual selection mode with:
  - **Artistic Style**: Choose from 8 different art styles
  - **Character Archetype**: Select from 9 character types
  - **Background Environment**: Pick from 6 environments

### Image-to-Image Options
- **Transformation Mode**: 4 different transformation types:
  - **Portrait Enhancement**: Add subtle programming elements while preserving appearance
  - **Character Fusion**: Blend with coding archetype while maintaining recognizable features
  - **Style Transfer**: Apply artistic style based on coding profile analysis
  - **Technical Overlay**: Balanced fusion of person and developer identity
- **Privacy Consent**: Required checkbox for profile picture usage

### Generation Control
- Generate button with loading states
- Status updates during processing
- Results display with download option

## Technical Details

### Architecture
- **Frontend**: Streamlit web application
- **Backend**: Existing git_to_image Python modules
- **Styling**: Custom CSS with Nintendo theme
- **Font**: Google Fonts "Press Start 2P"

### File Structure
```
frontend/
├── app.py              # Main Streamlit application
├── run_ui.py           # Startup script with environment checks
├── requirements.txt    # Frontend dependencies
└── README.md          # This file
```

### Dependencies
- `streamlit>=1.28.0`: Web framework
- `Pillow>=9.0.0`: Image processing

## Troubleshooting

### Common Issues

**"Missing environment variables"**
- Make sure `GITHUB_TOKEN` and `GEMINI_API_KEY` are set
- Check with: `echo $GITHUB_TOKEN` and `echo $GEMINI_API_KEY`

**"Streamlit not found"**
- Install with: `pip install streamlit`
- Or run the startup script which handles installation

**"Failed to analyze GitHub profile"**
- Verify the GitHub username exists
- Check your GitHub token has proper permissions
- Ensure internet connectivity

**"Image generation failed"**
- Verify your Gemini API key is valid
- Check API quota/limits
- Try again after a few minutes

### Performance Notes
- First-time profile analysis takes longer (30-60 seconds)
- Subsequent generations use cached profiles
- Image generation typically takes 10-30 seconds

## Development

### Adding New Features
1. Modify `app.py` for UI changes
2. Update CSS in the `load_css()` function
3. Add new options to the respective sections

### Customizing the Theme
- Edit the CSS styles in `load_css()`
- Modify colors, fonts, and layout
- Add new pixel art elements

## Support

For issues related to:
- **UI/Frontend**: Check this README and frontend code
- **Backend/Generation**: See main project documentation
- **API Issues**: Verify your tokens and API access
