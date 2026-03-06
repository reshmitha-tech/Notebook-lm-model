📄 DocIntel AI – PDF Question Answering System
📌 Project Overview

DocIntel AI is an intelligent document analysis system that allows users to upload PDF files and interact with them using natural language questions. The system processes the uploaded document, indexes its content, and generates answers based on the information present in the PDF.

The application uses Retrieval Augmented Generation (RAG) with the Gemini 1.5 Flash model to provide accurate and context-aware responses.

🚀 Features

📤 Upload PDF documents

📑 Automatic document indexing

❓ Ask questions related to the uploaded PDF

🤖 AI-generated answers based on document content

📊 Document analytics and workspace interface

💾 Local Vector Database storage

⚡ Fast responses using Gemini AI model

🖥️ System Interface

The application includes the following components:

Upload Section – Upload and index PDF documents

Workspace Chat – Ask questions related to the document

Source Viewer – Displays the document content

Analytics Panel – Shows model status and system readiness

Once a PDF is uploaded, the system indexes the document and allows users to query the information interactively.

🛠️ Technologies Used

Python

AI API Integration

Retrieval Augmented Generation (RAG)

PDF Processing Libraries

HTML / CSS / JavaScript

Local Vector Database

📂 Project Structure
docintel-ai/
│
├── app.py
├── requirements.txt
├── README.md
├── static/
│   └── styles.css
├── templates/
│   └── index.html
├── uploads/
│   └── pdf_files
└── .env
⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/your-username/docintel-ai.git
2️⃣ Navigate to Project Folder
cd docintel-ai
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Add API Key

Create a .env file and add your API key:

GEMINI_API_KEY=your_api_key_here
5️⃣ Run the Application
python app.py

The application will start on:

http://127.0.0.1:5000
📖 How the System Works

User uploads a PDF document.

The system extracts text from the document.

The document content is converted into vector embeddings.

The embeddings are stored in a Local Vector Database.

When the user asks a question:

Relevant document sections are retrieved.

The AI model generates an answer using those sections.

📊 Example Workflow

1️⃣ Upload a PDF
2️⃣ System indexes the document
3️⃣ Ask questions like:

Summarize the document

4️⃣ AI generates a contextual answer based on the document.

🔐 Security Note

API keys are not included in this repository.
Users must create a .env file and add their own API keys.

📌 Future Improvements

Multi-document querying

Cloud deployment

Improved document visualization

Chat history storage

Support for DOCX and TXT files

👩‍💻 Author

Developed by Reshmitha
