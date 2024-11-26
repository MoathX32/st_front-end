import streamlit as st
import requests

# Define the API endpoints for each language
API_ENDPOINTS = {
    "Arabic": "https://aiar-svc.eduai.tech",
    "English": "https://aien-svc.eduai.tech",
    "French": "https://aifr-svc.eduai.tech",
}

COURSE_IDS = {
    "Arabic":333,
    "English":609,
    "French":614,
}

# Streamlit app starts here
st.title("Language Learning Platform")

# Input for student ID
student_id = st.text_input("Enter your Student ID:", "")

if student_id:
    st.success(f"Student ID: {student_id} accepted.")

    # Sidebar configuration
    st.sidebar.header("Session Management")

    # Subject selection in sidebar
    subject = st.sidebar.selectbox("Choose a subject:", list(API_ENDPOINTS.keys()))

    if subject:
        api_url = API_ENDPOINTS[subject]
        course_id = COURSE_IDS[subject]
        st.sidebar.info(f"You selected {subject}.")

        # Start session button in sidebar
        if st.sidebar.button("Start Session"):
            load_path_response = requests.post(
                f"{api_url}/load_path/",
                data={"studentId": student_id, "courseId": course_id},
            )
            if load_path_response.status_code == 200:
                st.sidebar.success("Session started successfully!")
                st.session_state["session_active"] = True
                st.session_state["quiz_visible"] = True  # Initialize quiz visibility state
            else:
                st.sidebar.error("Failed to start session. Please check the API or your parameters.")

        # Clear session button in sidebar
        if st.sidebar.button("Clear Session"):
            clear_session_response = requests.post(f"{api_url}/clear_sessions/")
            if clear_session_response.status_code == 200:
                st.sidebar.success("Session cleared successfully!")
                st.session_state["session_active"] = False
                st.session_state["quiz_visible"] = False
            else:
                st.sidebar.error("Failed to clear session.")

        # Main area for active session features
if st.session_state.get("session_active", False):
    # Chat feature
    st.markdown("### Chat with the Bot")
    query = st.text_area("Ask a question:")
    
    # Always show the Submit Query button
    submit_query_button = st.button("Submit Query")

    if submit_query_button and query:
        query_response = requests.post(
            f"{api_url}/query/",
            data={
                "studentId": student_id,
                "courseId": course_id,
                "query_request": '{"query": "' + query + '"}',
            },
        )
        if query_response.status_code == 200:
            response_text = query_response.json().get("response", "No response")
            st.write("Bot Response:", response_text)

        else:
            st.error("Failed to submit query. Please try again.")
            st.error(f"Error Details: {query_response.json().get('detail', 'Unknown error')}")

    elif submit_query_button and not query:
        st.warning("Please enter a question before submitting.")

    # Display quiz options only if quiz_visible is True
    if st.session_state.get("quiz_visible", False):
        st.markdown("### Configure Quiz Options")
        question_type = st.selectbox("Choose question type:", ["MCQ", "TF"])
        num_questions = st.number_input(
            "Number of questions:", min_value=1, max_value=50, value=10
        )

        # Submit quiz request
        if st.button("Generate Quiz"):
            quiz_payload = {
                "studentId": student_id,
                "courseId": course_id,
                "question_type": question_type,
                "num_questions": num_questions,
            }
            quiz_response = requests.post(f"{api_url}/quiz/", data=quiz_payload)

            if quiz_response.status_code == 200:
                questions = quiz_response.json().get("questions", [])
                st.success("Quiz generated successfully!")
                for i, question in enumerate(questions, start=1):
                    st.markdown(f"**Q{i}: {question.get('question')}**")
                    for choice in question.get("choices", []):
                        st.markdown(f"- {choice}")
              
                    correct_answer = question.get('correct answer', 'None')
                    st.markdown(f"**Correct Answer:** {correct_answer}")
            else:
                st.error("Failed to generate quiz. Please try again.")
                st.error(f"Error Details: {quiz_response.json().get('detail', 'Unknown error')}")
