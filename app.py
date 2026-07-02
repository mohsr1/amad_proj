import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os 

# 1. إعداد صفحة الويب وتصميمها
st.set_page_config(page_title="مُمتَثِل - مستشار الامتثال المالي", page_icon="⚖️", layout="centered")

# العناوين الرئيسية للموقع
st.title("مُمتَثِل | Momtathil")
st.subheader("مستشارك الذكي للامتثال وتشريعات هيئة السوق المالية")

# --- إضافة القائمة الجانبية (ملف الشركة: نصوص + PDF) ---
with st.sidebar:
    st.header("🏢 ملف الشركة (Company Profile)")
    st.info("اكتب تفاصيل شركتك أو ارفع ملف الهيكلة ليقوم مُمتَثِل بتخصيص الاستشارات.")
    
    # 1. إدخال اسم الشركة
    company_name = st.text_input("اسم الشركة:", value="شركة التقنية المالية الحديثة")
    
    # 2. إدخال النبذة والنشاط
    company_desc = st.text_area("نبذة ونشاط الشركة (اختياري إذا رفعت ملف):", value="نحن شركة فنتك ناشئة نطمح لتقديم خدمات المحافظ الرقمية.")
    
    # 3. خيار رفع ملف PDF لبيانات الشركة
    st.markdown("---")
    uploaded_company_file = st.file_uploader("أو ارفع هيكل/ملف الشركة (PDF)", type="pdf", key="company_pdf")
    
    company_pdf_text = ""
    if uploaded_company_file:
        with st.spinner("جاري قراءة ملف الشركة..."):
            try:
                reader = PdfReader(uploaded_company_file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        company_pdf_text += page_text + "\n"
                st.success("تم ربط ملف الشركة بنجاح! 📎")
            except Exception as e:
                st.error("حدث خطأ في قراءة ملف الشركة.")
    
    # 4. دمج كل المعلومات وحفظها في الذاكرة
    st.session_state.company_context = f"اسم الشركة: {company_name}\nوصف ونشاط الشركة المكتوب: {company_desc}\n\nبيانات هيكل الشركة من الملف المرفق:\n{company_pdf_text}"
# ----------------------------------------------------

# 2. إعداد المفتاح السري والموديل
genai.configure(api_key="place your API key here")  # ضع مفتاحك السري هنا
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

# 4. اختيار التصنيف واللائحة من المجلدات
BASE_DIR = "CMA كامل"
if os.path.exists(BASE_DIR):
    categories = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    selected_category = st.selectbox("1️⃣ اختر التصنيف التشريعي:", categories)
    
    if selected_category:
        category_path = os.path.join(BASE_DIR, selected_category)
        files = [f for f in os.listdir(category_path) if f.endswith('.pdf')]
        
        if files:
            selected_file = st.selectbox("2️⃣ اختر النظام أو اللائحة المراد فحصها:", files)
            
            if selected_file:
                full_file_path = os.path.join(category_path, selected_file)
                
                # قراءة الملف فقط إذا تم اختيار ملف جديد (عشان ما يعيد القراءة مع كل رسالة بالشات)
                if "current_file" not in st.session_state or st.session_state.current_file != full_file_path:
                    with st.spinner("⏳ جاري قراءة وتحليل اللائحة... انتظر لحظة من فضلك"):
                        st.session_state.pdf_content = read_pdf(full_file_path)
                        st.session_state.current_file = full_file_path # حفظ مسار الملف الحالي
                    st.success("تم رفع وتحليل اللائحة بنجاح! مُمتَثِل جاهز لأسئلتك.")
        else:
            st.info("لا توجد ملفات PDF داخل هذا التصنيف حالياً.")
else:
    st.error(f"لم يتم العثور على المجلد الأساسي '{BASE_DIR}'. تأكد من وجوده.")

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
        prompt = f"بناءً على النص القانوني المرفق {st.session_state.pdf_content}\n\nبيانات الشركة المستفيدة (يجب تخصيص الإجابة بناءً عليها):\n{st.session_state.company_context}\n\nتاريخ المحادثة السابقة :\n{history_text}\n\nالسؤال الجديد : {user_input}\n\nملاحظة هامة: خصص إجابتك لتناسب نشاط الشركة، واذكر أرقام المواد كمرجع (Source Ref)."
        response = model.generate_content(prompt)
    
    # عرض رد ممتثل وحفظه في الذاكرة
    with st.chat_message("assistant"):
        st.markdown(f"### ⚖️ رد مُمتَثِل:\n{response.text}")
    st.session_state.messages.append({"role": "assistant", "content": f"### ⚖️ رد مُمتَثِل:\n{response.text}"})

