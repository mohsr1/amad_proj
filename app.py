import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. إعداد صفحة الويب وتصميمها
st.set_page_config(page_title="مُمتَثِل - مستشار الامتثال المالي", page_icon="⚖️", layout="centered")

# العناوين الرئيسية للموقع
st.title("مُمتَثِل | Momtathil")
st.subheader("مستشارك الذكي للامتثال وتشريعات هيئة السوق المالية")

# 2. إعداد المفتاح السري والموديل
genai.configure(api_key="place your API key here")
model = genai.GenerativeModel('gemini-3.5-flash')

# 3. دالة قراءة ملف الـ PDF
def read_pdf(file_object):
    reader = PdfReader(file_object)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

# 4. خانة السحب والإفلات (Drag & Drop)
uploaded_file = st.file_uploader("قم بسحب وإفلات ملف اللائحة القانونية هنا (PDF)", type="pdf")

# استخدام ذاكرة الجلسة لحفظ النص لمنع اختفائه عند التحديث
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""

# إذا قام المستخدم برفع ملف
if uploaded_file is not None:
    if not st.session_state.pdf_content:
        with st.spinner("جاري قراءة وتحليل اللائحة... انتظر لحظة من فضلك ⏳"):
            st.session_state.pdf_content = read_pdf(uploaded_file)
        st.success("تم رفع وتحليل اللائحة بنجاح! مُمتَثِل جاهز لأسئلتك.")

    st.write("---")
    
    
    
    
    # 1. تهيئة ذاكرة المحادثة إذا لم تكن موجودة
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. عرض الرسائل السابقة المعتمدة في الذاكرة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. خانة إدخال السؤال الذكية في أسفل الشاشة
if user_input := st.chat_input("اسأل مُمتَثِل عن أي مادة أو بند في هذه اللائحة..."):
    
    # عرض سؤال المستخدم فوراً في الشات
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # توليد الرد من الذكاء الاصطناعي
    with st.spinner("...جاري صياغة الرد القانوني"):
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[:-1]])
        prompt = f"بناءً على النص القانوني المرفق: {st.session_state.pdf_content[:15000]}\n\nتاريخ المحادثة السابقة:\n{history_text}\n\nالسؤال الجديد القانوني: {user_input}"
        response = model.generate_content(prompt)
    
    # عرض رد ممتثل وحفظه في الذاكرة
    with st.chat_message("assistant"):
        st.markdown(f"### ⚖️ رد مُمتَثِل:\n{response.text}")
    st.session_state.messages.append({"role": "assistant", "content": f"### ⚖️ رد مُمتَثِل:\n{response.text}"})

