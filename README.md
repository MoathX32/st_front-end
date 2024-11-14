This FastAPI application allows users to process PDF files, generate vector embeddings using Google Generative AI, perform similarity searches, and create quiz questions based on the extracted content.

🚀 Features
PDF Processing: Extracts text from PDF files and splits it into chunks for efficient processing.
Vector Embeddings: Uses Google Generative AI embeddings for creating vector stores with FAISS.
Similarity Search: Allows querying of processed PDF content for relevant answers.
Quiz Generation: Generates multiple-choice or True/False questions based on AI responses.
Session Management: Manages user sessions and schedules automatic session clearance.
🛠️ Prerequisites
1. Install Dependencies
bash
Copy code
pip install fastapi uvicorn python-dotenv pydantic langchain langchain-google-genai langchain-core langchain-community faiss-cpu pymupdf google-generativeai requests
2. Set Up Environment Variables
Create a .env file with your Google Generative AI API key:

bash
Copy code
GENAI_API_KEY=<your_google_genai_api_key>
3. Project Structure
bash
Copy code
project-root/
├── main.py
├── .env
├── subject/
├── Data/
├── logs/
└── requirements.txt
📋 API Endpoints
1. /load_path/ - Load and Process PDF Files
Method: POST

Description: Loads PDF files for a specific course, processes them, and creates a vector store for similarity search.

Parameters:

courseId (Form): The course identifier.
studentId (Form): The student identifier.
Example:

bash
Copy code
curl -X 'POST' 'http://localhost:8000/load_path/' \
-F 'courseId=course_1' \
-F 'studentId=123'
Response:

json
Copy code
{
    "message": "PDF files processed successfully",
    "session_id": "123_course_1"
}
2. /query/ - Query PDF Content
Method: POST

Description: Query the processed PDF content using a similarity search.

Parameters:

query_request (Form): JSON string with query and optional_param.
courseId (Form): The course identifier.
studentId (Form): The student identifier.
Example:

bash
Copy code
curl -X 'POST' 'http://localhost:8000/query/' \
-F 'query_request={"query": "What is the main topic of lesson 1?"}' \
-F 'courseId=course_1' \
-F 'studentId=123'
Response:

json
Copy code
{
    "response": "The main topic of lesson 1 is the introduction to basic mathematics."
}
3. /quiz/ - Generate Quiz Questions
Method: POST

Description: Generates quiz questions based on the last valid AI response.

Parameters:

courseId (Form): The course identifier.
studentId (Form): The student identifier.
question_type (Form): The type of questions (MCQ or True/False).
num_questions (Form): The number of questions to generate.
Example:

bash
Copy code
curl -X 'POST' 'http://localhost:8000/quiz/' \
-F 'courseId=course_1' \
-F 'studentId=123' \
-F 'question_type=MCQ' \
-F 'num_questions=5'
Response:

json
Copy code
{
    "questions": [
        {
            "question": "What is 2 + 2?",
            "choices": ["1", "2", "3", "4"],
            "correct_answer": "4"
        }
    ]
}
4. /clear_sessions/ - Clear All Sessions
Method: POST

Description: Clears all active sessions and deletes stored PDF data.

Example:

bash
Copy code
curl -X 'POST' 'http://localhost:8000/clear_sessions/'
Response:

json
Copy code
{
    "message": "All sessions and folders have been cleared successfully."
}
🗂️ Code Overview
Core Functions
get_single_pdf_chunks(): Extracts text from a PDF and splits it into chunks.
get_all_pdfs_chunks(): Processes multiple PDFs and aggregates chunks.
get_vector_store(): Creates a FAISS vector store using Google Generative AI embeddings.
process_lessons(): Reads PDF files and processes them into a vector store.
get_response(): Generates a response using Gemini AI based on the query and context.
generate_questions_from_response(): Creates quiz questions from AI responses.
clean_json_response(): Cleans and parses AI response text into JSON format.
get_new_token(): Retrieves an authentication token for external API requests.
Startup Event
The application schedules a daily task to clear all active sessions at midnight using BackgroundTasks.

Running the Application
To start the FastAPI server, run:

bash
Copy code
uvicorn main:app --host 0.0.0.0 --port 8000
🔍 Logging
The application uses Python's logging module for information and error messages. Logs are displayed in the console.

⚠️ Error Handling
The application uses FastAPI's HTTPException to handle errors and provide meaningful responses.

📈 Future Improvements
Persistent Storage: Add support for persistent vector storage (e.g., SQLite, MongoDB).
Enhanced Security: Improve handling of sensitive data (e.g., API keys, credentials).
Scalability: Implement distributed processing for handling larger datasets.
