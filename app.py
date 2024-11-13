import streamlit as st
import requests
import json

# رابط واجهة FastAPI الخلفية
BASE_URL = "http://57.128.91.158"

# معلومات المستخدم (رقم الطالب)
STUDENT_ID = "500"

# تنسيق النص العربي لليمين
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

# واجهة المستخدم
st.title("مساعد التعلم بالذكاء الاصطناعي")

# عرض خيار المادة (اللغة العربية فقط)
st.markdown("<div class='rtl-text'>اختر مادة للبدء:</div>", unsafe_allow_html=True)

# زر اختيار اللغة العربية
if st.button("اللغة العربية", key="arabic"):
    selected_subject = "اللغة العربية"
    course_id = 314  # رقم المادة للغة العربية

    # بدء الجلسة
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

# التأكد من أن الجلسة نشطة
if "session_id" in st.session_state:
    st.markdown(f"<div class='rtl-text'>استفسر عن {st.session_state['selected_subject']}:</div>", unsafe_allow_html=True)

    # خطوة 2: إدخال السؤال
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

    # خطوة 3: توليد اختبار (مخفي حتى الضغط على زر إظهار الاختبار)
    if "last_response" in st.session_state:
        if st.button("عرض قسم الاختبار"):
            st.session_state["quiz_visible"] = True

    # عرض قسم الاختبار فقط إذا تم الضغط على الزر
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

# خطوة 4: مسح الجلسات (اختياري)
if st.sidebar.button("مسح الجلسات"):
    clear_response = requests.post(f"{BASE_URL}/clear_sessions/")
    if clear_response.status_code == 200:
        st.success("تم مسح جميع الجلسات بنجاح!")
        st.session_state.clear()
    else:
        st.error("فشل في مسح الجلسات.")
