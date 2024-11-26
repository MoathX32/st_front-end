import streamlit as st
import requests

# Define the API endpoints for each language
API_ENDPOINTS = {
    "Arabic": "https://aiar-svc.eduai.tech",
    "English": "https://aien-svc.eduai.tech",
    "French": "https://aifr-svc.eduai.tech",
}

# Define the course IDs for subjects
COURSE_IDS = {
    "English": 609,
    "French": 614,
    "علوم": 941,
    "عربي": 314,
    "فلسفة": 335,
    "إسلامية": 333,
    "دراسات": 339,
}

# Streamlit app starts here
st.title("منصة التعلم")

# Input for student ID
student_id = st.text_input("أدخل رقم الطالب:", "")

if student_id:
    st.success(f"تم قبول رقم الطالب: {student_id}")

    # Sidebar configuration
    st.sidebar.header("إدارة الجلسة")

    # Subject selection in sidebar
    subject = st.sidebar.selectbox("اختر مادة:", list(COURSE_IDS.keys()))

    if subject:
        course_id = COURSE_IDS[subject]
        api_url = (
            API_ENDPOINTS["Arabic"]
            if subject in ["علوم", "عربي", "فلسفة", "إسلامية", "دراسات"]
            else API_ENDPOINTS[subject]
        )
        st.sidebar.info(f"لقد اخترت مادة {subject}.")

        # Start session button in sidebar
        if st.sidebar.button("بدء الجلسة"):
            load_path_response = requests.post(
                f"{api_url}/load_path/",
                data={"studentId": student_id, "courseId": course_id},
            )
            if load_path_response.status_code == 200:
                st.sidebar.success("تم بدء الجلسة بنجاح!")
                st.session_state["session_active"] = True
                st.session_state["quiz_visible"] = True  # Initialize quiz visibility state
            else:
                st.sidebar.error("فشل في بدء الجلسة. يرجى التحقق من API أو المعلمات.")

        # Clear session button in sidebar
        if st.sidebar.button("مسح الجلسة"):
            clear_session_response = requests.post(f"{api_url}/clear_sessions/")
            if clear_session_response.status_code == 200:
                st.sidebar.success("تم مسح الجلسة بنجاح!")
                st.session_state["session_active"] = False
                st.session_state["quiz_visible"] = False
            else:
                st.sidebar.error("فشل في مسح الجلسة.")

# Main area for active session features
if st.session_state.get("session_active", False):
    # Chat feature
    st.markdown("### تحدث مع الروبوت")
    query = st.text_area("اطرح سؤالًا:")
    
    # Always show the Submit Query button
    submit_query_button = st.button("إرسال السؤال")

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
            response_text = query_response.json().get("response", "لا توجد استجابة")
            st.write("رد الروبوت:", response_text)

        else:
            st.error("فشل في إرسال السؤال. يرجى المحاولة مرة أخرى.")
            st.error(f"تفاصيل الخطأ: {query_response.json().get('detail', 'خطأ غير معروف')}")

    elif submit_query_button and not query:
        st.warning("يرجى إدخال سؤال قبل الإرسال.")

    # Display quiz options only if quiz_visible is True
    if st.session_state.get("quiz_visible", False):
        st.markdown("### إعداد خيارات الاختبار")
        question_type = st.selectbox("اختر نوع الأسئلة:", ["MCQ", "TF"])
        num_questions = st.number_input(
            "عدد الأسئلة:", min_value=1, max_value=50, value=10
        )

        # Submit quiz request
        if st.button("إنشاء اختبار"):
            quiz_payload = {
                "studentId": student_id,
                "courseId": course_id,
                "question_type": question_type,
                "num_questions": num_questions,
            }
            quiz_response = requests.post(f"{api_url}/quiz/", data=quiz_payload)

            if quiz_response.status_code == 200:
                questions = quiz_response.json().get("questions", [])
                st.success("تم إنشاء الاختبار بنجاح!")
                for i, question in enumerate(questions, start=1):
                    st.markdown(f"**السؤال {i}: {question.get('question')}**")
                    for choice in question.get("choices", []):
                        st.markdown(f"- {choice}")
              
                    correct_answer = question.get('correct answer', 'None')
                    st.markdown(f"**الإجابة الصحيحة:** {correct_answer}")
            else:
                st.error("فشل في إنشاء الاختبار. يرجى المحاولة مرة أخرى.")
                st.error(f"تفاصيل الخطأ: {quiz_response.json().get('detail', 'خطأ غير معروف')}")
