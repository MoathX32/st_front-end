import streamlit as st
import requests
import json

# FastAPI backend URL
BASE_URL = "http://57.128.91.158"

# User information (student ID)
STUDENT_ID = "500"

# Custom CSS for right-aligned Arabic content
st.markdown("""
    <style>
    .rtl-text {
        text-align: right;
        direction: rtl;
        font-size: 18px;
    }
    .large-button {
        width: 100%;
        height: 70px;
        font-size: 20px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Streamlit UI
st.title("مساعد التعلم بالذكاء الاصطناعي")

# Step 1: Subject Selection
subject_map = {
    "اللغة العربية": 314,
    "الرياضيات": 315,
    "العلوم": 316
}

# Display subject options as large clickable buttons
st.markdown("<div class='rtl-text'>اختر مادة للبدء:</div>", unsafe_allow_html=True)

# Using Streamlit's columns to display buttons in a row
col1, col2, col3 = st.columns(3)

# Initialize variables
selected_subject = None
course_id = None

# Handle button clicks for each subject
with col1:
    if st.button("اللغة العربية", key="arabic", help="اختر مادة اللغة العربية"):
        selected_subject = "اللغة العربية"
        course_id = subject_map[selected_subject]

with col2:
    if st.button("الرياضيات", key="math", help="اختر مادة الرياضيات"):
        selected_subject = "الرياضيات"
        course_id = subject_map[selected_subject]

with col3:
    if st.button("العلوم", key="science", help="اختر مادة العلوم"):
        selected_subject = "العلوم"
        course_id = subject_map[selected_subject]

# Start session automatically if a subject button is clicked
if selected_subject and course_id:
    payload = {
        "courseId": course_id,
        "studentId": STUDENT_ID
    }
    response = requests.post(f"{BASE_URL}/load_path/", data=payload)

    if response.status_code == 200:
        st.success(f"تم بدء الجلسة بنجاح لمادة {selected_subject}!")
        session_id = response.json().get("session_id")
        st.session_state["session_id"] = session_id
        st.session_state["course_id"] = course_id
        st.session_state["selected_subject"] = selected_subject
        st.session_state["quiz_visible"] = False
    else:
        error_message = response.json().get("detail", "فشل في بدء الجلسة. حاول مرة أخرى.")
        st.error(error_message)

# Check if session is active
if "session_id" in st.session_state:
    st.markdown(f"<div class='rtl-text'>استفسر عن {st.session_state['selected_subject']}:</div>", unsafe_allow_html=True)

    # Step 2: Enter a query
    query = st.text_input("اكتب سؤالك هنا:")
    if st.button("الحصول على إجابة"):
        query_request = {
            "query": query,
            "optional_param": ""
        }
        payload = {
            "query_request": json.dumps(query_request),
            "courseId": st.session_state["course_id"],
            "studentId": STUDENT_ID
        }

        response = requests.post(f"{BASE_URL}/query/", data=payload)
        if response.status_code == 200:
            answer = response.json().get("response", "")
            st.markdown(f"<div class='rtl-text'>الإجابة:</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='rtl-text'>{answer}</div>", unsafe_allow_html=True)
            st.session_state["last_response"] = answer
        else:
            st.error(response.json().get("detail", "حدث خطأ أثناء الاستفسار."))

    # Step 3: Generate Quiz (hidden until button click)
    if "last_response" in st.session_state:
        if st.button("عرض قسم الاختبار"):
            st.session_state["quiz_visible"] = True

    # Only display the quiz section if the button was clicked
    if st.session_state.get("quiz_visible", False):
        st.markdown("<div class='rtl-text'>توليد اختبار:</div>", unsafe_allow_html=True)
        question_type = st.selectbox("اختر نوع الأسئلة:", ["اختيار من متعدد", "صح أو خطأ"])
        num_questions = st.slider("عدد الأسئلة:", min_value=1, max_value=10, value=5)

        if st.button("توليد الاختبار"):
            quiz_payload = {
                "courseId": st.session_state["course_id"],
                "studentId": STUDENT_ID,
                "question_type": question_type,
                "num_questions": num_questions
            }

            quiz_response = requests.post(f"{BASE_URL}/quiz/", data=quiz_payload)
            if quiz_response.status_code == 200:
                questions = quiz_response.json().get("questions", [])
                st.success("تم توليد الاختبار بنجاح!")
                for i, question in enumerate(questions, start=1):
                    st.markdown(f"<div class='rtl-text'>س{str(i)}: {question['question']}</div>", unsafe_allow_html=True)
                    for choice in question['choices']:
                        st.markdown(f"<div class='rtl-text'>- {choice}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='rtl-text'>الإجابة الصحيحة: {question['correct_answer']}</div>", unsafe_allow_html=True)
            else:
                st.error("فشل في توليد الاختبار.")

# Step 4: Clear sessions (optional)
if st.sidebar.button("مسح الجلسات"):
    clear_response = requests.post(f"{BASE_URL}/clear_sessions/")
    if clear_response.status_code == 200:
        st.success("تم مسح جميع الجلسات بنجاح!")
        st.session_state.clear()
    else:
        st.error("فشل في مسح الجلسات.")
