Prerequisites
1. Installation
Ensure you have the following packages installed:

bash
Copy code
pip install fastapi uvicorn python-dotenv pydantic langchain langchain-google-genai langchain-core langchain-community faiss-cpu pymupdf google-generativeai requests
2. Environment Variables
Set up your environment variables using a .env file:

bash
Copy code
GENAI_API_KEY=<your_google_genai_api_key>
3. Project Structure
Your project directory should look like this:

bash
Copy code
project-root/
├── main.py
├── .env
├── subject/
├── Data/
├── logs/
└── requirements.txt
API Endpoints
1. /load_path/ - Load and Process PDF Files
Method: POST

Description: Loads PDF files for a specific course, processes them, and creates a vector store for similarity search.

Parameters:

courseId (Form): The course identifier.
studentId (Form): The student identifier.
Returns:

message: Confirmation that PDF files were processed.
session_id: Unique session identifier.
Example Request:

bash
Copy code
curl -X 'POST' 'http://localhost:8000/load_path/' \
-F 'courseId=course_1' \
-F 'studentId=123'
Example Response:

json
Copy code
{
    "message": "PDF files processed successfully",
    "session_id": "123_course_1"
}
2. /query/ - Query PDF Content
Method: POST

Description: Allows querying of processed PDF content using a similarity search.

Parameters:

query_request (Form): JSON string with query parameters (query and optional_param).
courseId (Form): The course identifier.
studentId (Form): The student identifier.
Returns:

response: The AI-generated response based on the query.
Example Request:

bash
Copy code
curl -X 'POST' 'http://localhost:8000/query/' \
-F 'query_request={"query": "What is the main topic of lesson 1?"}' \
-F 'courseId=course_1' \
-F 'studentId=123'
Example Response:

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
Returns:

questions: List of generated quiz questions.
Example Request:

bash
Copy code
curl -X 'POST' 'http://localhost:8000/quiz/' \
-F 'courseId=course_1' \
-F 'studentId=123' \
-F 'question_type=MCQ' \
-F 'num_questions=5'
Example Response:

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

Returns:

message: Confirmation that all sessions were cleared.
Example Request:

bash
Copy code
curl -X 'POST' 'http://localhost:8000/clear_sessions/'
Example Response:

json
Copy code
{
    "message": "All sessions and folders have been cleared successfully."
}
Code Overview
1. get_single_pdf_chunks()
Extracts text from a single PDF file and splits it into chunks using RecursiveCharacterTextSplitter.
Each chunk is stored as a Document object with metadata.
2. get_all_pdfs_chunks()
Iterates through all PDF files, extracts chunks, and aggregates them.
3. get_vector_store()
Creates a vector store using FAISS from the extracted PDF chunks.
Embeddings are generated using GoogleGenerativeAIEmbeddings.
4. process_lessons()
Reads PDF files from a specified folder and processes them into a vector store for similarity search.
5. get_response()
Generates a response using the Gemini AI model based on the provided context and query.
Handles specific flags like "OUT_OF_TOPIC" and "INCORRECT_QUESTION".
6. generate_questions_from_response()
Generates quiz questions based on the response text using the Gemini AI model.
Supports both MCQ and True/False question types.
7. clean_json_response()
Cleans and parses the AI response text into a JSON format.
8. get_new_token()
Retrieves a new authentication token from an external API.
Startup Event
The application automatically schedules a daily session clear task at midnight using BackgroundTasks.

Running the Application
To start the FastAPI server, use the following command:

bash
Copy code
uvicorn main:app --host 0.0.0.0 --port 8000
Logging
The application uses Python's logging module to provide information and error messages. Logs are displayed in the console.

Error Handling
The application uses FastAPI's HTTPException to handle errors gracefully and provide meaningful responses.

Notes for Developers
Session Management: The application uses a global sessions dictionary to manage user sessions. Ensure to clear sessions regularly to avoid memory issues.
Token Retrieval: The token for API requests is retrieved using the get_new_token() function. Update the credentials and API URL as needed.
Vector Store: The vector store is stored in memory using FAISS. For larger datasets, consider using a persistent storage option.
