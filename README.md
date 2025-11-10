# Ollama_FullStack_model
OLLAMA FULL STACK (Front-end Flutter ) and (Backend Python ) (Langchain FrameWork)
Pizza Reviews AI Analysis 🍕
A full-stack application for analyzing pizza restaurant reviews using AI. Features real-time streaming responses through WebSocket connections.


✨ Features
Real-time AI Analysis: Stream AI responses using WebSocket connections

Multiple Frontends: Flutter mobile app + HTML web interface

Local AI Processing: Uses Ollama for privacy and offline capability

CSV Data Integration: Analyze pizza review datasets

Cross-Platform: Works on mobile, web, and desktop

🏗️ Project Structure
```
pizza-reviews-ai/
├── backend/                 # Python FastAPI Server
│   ├── app/
│   │   └── server.py       # Main server with WebSocket endpoints
│   ├── requirements.txt    # Python dependencies
│   ├── pizza_reviews.csv  # Sample dataset
│   └── README.md
├── frontend/               # Client Applications
│   ├── flutter/           # Mobile App
│   │   ├── lib/
│   │   │   └── main.dart  # Flutter application
│   │   ├── pubspec.yaml  # Flutter dependencies
│   │   └── README.md
│   └── web/               # Web Interface
│       └── index.html     # HTML client
└── README.md
```
🚀 Quick Start
Prerequisites
Python 3.8+ with pip

Flutter 3.0+ (for mobile app)

Ollama with llama3.2 model installed

1. Backend Setup
bash
# Navigate to backend
cd backend

# Install Python dependencies
```
pip install -r requirements.txt
```
# Make sure Ollama is running
```
ollama serve
```
# Start the FastAPI server
```
python -m app.server
```
The backend will start at http://localhost:8000

Verify backend is working:
```
Visit http://localhost:8000 - Test interface

Visit http://localhost:8000/health - Health check
```
2. Frontend Setup
Option A: Flutter Mobile App
bash
# Navigate to Flutter app
```
cd frontend/flutter
```
# Install dependencies
```
flutter pub get
```
# Run the app (make sure you have a device/emulator connected)
```
flutter run
```
Option B: Web Interface
Simply open frontend/web/index.html in your web browser.

🔧 Configuration
Backend Configuration
Environment variables (optional):

bash
```
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3.2"
```
Flutter App Configuration
Update the server URL in lib/main.dart:

dart
```
// For local development
final String serverUrl = 'ws://localhost:8000/ws';

// For mobile devices on same network
final String serverUrl = 'ws://192.168.1.100:8000/ws';  // Your computer's IP

// For Android emulator
final String serverUrl = 'ws://10.0.2.2:8000/ws';
```
📱 Usage
Start the backend server

Launch your preferred frontend (Flutter app or web interface)

Ask questions about the pizza reviews:

"What do customers say about the pizza crust?"

"What are the most common complaints?"

"How is the delivery service rated?"

"What's the overall sentiment of reviews?"

🛠️ API Endpoints
Method	Endpoint	Description
GET	/	HTML test interface
GET	/health	Server health check
WebSocket	/ws	Real-time AI chat
WebSocket Message Format:

json
```
{
  "question": "Your question here"
}
```
Response Format:

json
```
{
  "type": "chunk|done|error",
  "text": "Response content"
}
````
📊 Sample Data
The project includes pizza_reviews.csv with:

Review IDs

Review text

Ratings (1-5 stars)

Sentiment analysis

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

🐛 Troubleshooting
Common Issues
Connection Refused

Ensure backend server is running on port 8000

Check if Ollama is running (ollama serve)

Verify IP address in Flutter app matches your computer's IP

Model Not Found

bash
# Install the required Ollama model
ollama pull llama3.2
Flutter Dependencies

bash
```
cd frontend/flutter
flutter clean
flutter pub get
```
📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Ollama for local LLM inference

FastAPI for the modern Python web framework

Flutter for cross-platform mobile development
