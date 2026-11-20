# VisionIQ — AI-Powered Image Analysis System

A Flask web application demonstrating image understanding using Microsoft Azure AI Vision Image Analysis 4.0.

## Features
- Image upload and preview
- Image caption generation
- Visual tags
- Object detection
- OCR (text extraction)
- Demo mode when Azure credentials are not configured

## Requirements
- Windows 10/11
- Python 3.10 or newer
- Internet connection for Azure mode
- Azure Vision resource for live cloud analysis

## Run on Windows

1. Extract the ZIP.
2. Open PowerShell in the extracted `azure_image_analysis_system` folder.
3. Create and activate a virtual environment:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

4. Install packages:

```powershell
pip install -r requirements.txt
```

5. Start the application:

```powershell
python app.py
```

6. Open `http://127.0.0.1:5000` in your browser.

Without Azure credentials, the app runs in **Demo mode**. Demo output is clearly labelled and is not a real AI prediction.

## Enable Azure AI Vision

1. Create or use an Azure AI Vision / Computer Vision resource in the Azure portal.
2. Copy the resource endpoint and key.
3. Copy `.env.example` to a new file named `.env`.
4. Put the endpoint and key in `.env`.
5. Restart the Flask app.

Example `.env`:

```env
AZURE_VISION_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com
AZURE_VISION_KEY=your-secret-key
```

The app calls the Image Analysis REST API with the `caption`, `denseCaptions`, `objects`, `read`, and `tags` features. Captioning availability depends on the Azure region. API credentials stay on the server and are not exposed in browser JavaScript.

## Important academic note
The demo mode returns sample placeholder insights solely to demonstrate the interface. For genuine AI results, configure a valid Azure resource and verify the response. Do not describe demo-mode sample output as a real Azure prediction.

Microsoft currently documents Image Analysis 4.0 as deprecated, with retirement scheduled for September 25, 2028. Review Microsoft's migration guidance for future deployments.

## Suggested presentation flow
1. Introduce Computer Vision and the project objective.
2. Open the application.
3. Upload a clear image containing several objects.
4. Run analysis.
5. Explain caption, tags, detected objects and OCR.
6. Explain the Azure endpoint/key configuration and responsible handling of images and credentials.

## References
- Microsoft Learn: https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/overview-image-analysis
- Microsoft Learn: https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/how-to/call-analyze-image-40
- Microsoft Learn: https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/concept-ocr
