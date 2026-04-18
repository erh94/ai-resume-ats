# 🎯 AI Resume Matcher ATS

An AI-powered Application Tracking System (ATS) that evaluates your resume against job descriptions using Google's cutting-edge Gemini AI models.

Developed by Himanshu Upreti using Vibe Coding Gemini Pro

## Features
- **AI Evaluation:** Uses Gemini 2.5 Flash / 2.0 Flash to calculate JD Match %, extract missing keywords, and provide actionable improvement pointers.
- **Smart JD Extraction:** Automatically scrapes job description text from external URLs.
- **Live PDF Preview:** View your uploaded resume directly within the app interface.
- **Dynamic Model Selection:** Switch between different Gemini models on the fly to manage rate limits and performance.

---

## 🚀 Setup Instructions for Linux / WSL (Ubuntu 20.04)

These instructions assume you are running Windows Subsystem for Linux (WSL) with Ubuntu 20.04 or a native Linux 20.04 environment.

### Prerequisites
* Anaconda or Miniconda installed on your WSL instance.
* A Google AI Studio API Key.

### 1. Create and Activate a Conda Environment

Open your WSL terminal and run the following commands to create a fresh environment using Python 3.10 (required for the latest Google GenAI SDK):

```bash
# Create the environment
conda create -n resume_ats python=3.10 -y

# Activate the environment
conda activate resume_ats
```

### 2. Install Dependencies
Navigate to the directory where your project files (app.py and requirements.txt) are located, then install the required packages:

```bash
# Ensure you are in the project folder
# cd /path/to/ResumeMatcher-ATS

# Install the dependencies via pip
pip install -r requirements.txt
```

### 3. Setup Environment Variables (Optional)

While you can input your API key directly into the app's UI sidebar, you can also set it up locally so you don't have to type it every time.

Create a .env file in the root of your project:
```Bash

nano .env
```
Add your Google API key to the file:
Code snippet

```Bash
GOOGLE_API_KEY="your_api_key_here"
```
Press CTRL+X, then Y, then Enter to save and exit nano.

### 4. Run the Application

Start the Streamlit server:
```Bash

streamlit run app.py
```
Streamlit will provide a local URL (usually http://localhost:8501). CTRL+CLICK the link in your WSL terminal, or copy and paste it into your Windows web browser to open the app!

### 5. 🛠️ Troubleshooting

"ModuleNotFoundError: No module named 'google.genai'"
Make sure your Conda environment is active (conda activate resume_ats) and that you have installed the new SDK via pip (pip install google-genai).

Rate Limit Errors (429)
If you hit a "Resource Exhausted" error, you are making too many requests too quickly on the Google free tier. Switch the model to gemini-2.5-flash-lite in the app sidebar, or wait 60 seconds and try again.

