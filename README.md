AI Knowledge Transformer is an intelligent learning assistant that converts traditional study materials into interactive learning formats.
Students often spend hours reading PDFs, notes, and slides but still struggle to understand concepts quickly, revise before exams, and remember key points.
This project solves that problem by automatically transforming study material into:
📄 Concise summaries
🧠 Key concepts
❓ Multiple-choice quizzes
🔊 Audio explanations
🎥 Short AI-generated learning videos
💡 Flashcards for quick revision
The goal is to make learning faster, smarter, and more engaging.
🎯 Problem Statement
Students face challenges such as:
Spending too much time reading lengthy PDFs
Difficulty understanding complex concepts
Inefficient exam revision
Forgetting important points after studying
Traditional learning methods are time-consuming and passive.
💡 Solution
AI Knowledge Transformer uses Artificial Intelligence to automatically convert study material into multiple learning formats.
Users simply upload a PDF file, and the system generates:
✔ Short summary
✔ Key concepts
✔ MCQ quiz questions
✔ Audio explanation
✔ AI-generated learning video
✔ Flashcards for quick revision
This transforms boring notes into interactive learning content.
🚀 Features
📄 PDF Processing
Users can upload study materials in PDF format, and the system extracts text automatically.
🧠 AI Content Generation
Using LLM APIs like Gemini/OpenAI, the system generates:
Short summaries
Key concept lists
Multiple-choice quiz questions
🔊 Audio Explanation
The summary is converted into speech using gTTS, allowing students to listen to explanations.
🎥 AI Learning Video
A short learning video is generated using MoviePy, combining:
Text slides
Audio narration
Smooth transitions
💡 Flashcards
Quick revision flashcards are generated from key concepts.
🏗 System Architecture
Frontend
Technologies used:
HTML
CSS
JavaScript
Bootstrap
Features:
PDF upload interface
Generate AI results button
Summary display
Quiz display
Audio player
Video player
Backend
Technology:
Python
Flask
Responsibilities:
Handle PDF uploads
Extract text from PDFs
Send content to AI APIs
Generate audio and video outputs
AI APIs
Gemini / OpenAI API → Text generation
gTTS → Audio generation
MoviePy → Video generation
⚙️ System Workflow


User Uploads PDF
        │
        ▼
PDF Text Extraction
        │
        ▼
AI Processing (LLM API)
        │
 ┌───────────────┬───────────────┬───────────────┐
 ▼               ▼               ▼
Summary      Quiz Generator    Key Points
        │
        ▼
Audio Generator
        │
        ▼
Video Generator
        │
        ▼
Display Results on Web Page
📂 Project Structure
Copy code

AI-Knowledge-Transformer
│
├── app.py
│
├── templates
│   └── index.html
│
├── static
│   ├── audio
│   ├── video
│   └── uploads
│
└── README.md
🛠 Installation
1️⃣ Clone the Repository
Bash

git clone https://github.com/your-username/ai-knowledge-transformer.git
2️⃣ Navigate to the Project Folder
Bash

cd ai-knowledge-transformer
3️⃣ Install Required Dependencies
Bash

pip install -r requirements.txt
4️⃣ Run the Flask Application
Bash

python app.py
5️⃣ Open in Browser


http://127.0.0.1:5000
📸 Application Interface
The web dashboard allows users to:
Upload PDF documents
Generate AI learning material
View summaries and key concepts
Attempt quiz questions
Listen to audio explanations
Watch AI-generated videos
🎯 Use Cases
Exam revision
Quick lecture summaries
AI-powered note transformation
Interactive learning tools
Educational platforms
🔒 Security
API keys are stored securely using environment variables and are not pushed to GitHub.
Example:


.env
API_KEY=your_api_key_here
📈 Future Improvements
Multi-language learning support
AI-generated mind maps
Personalized learning recommendations
Mobile-friendly interface
Real-time lecture summarization
