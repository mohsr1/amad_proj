import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
from streamlit_option_menu import option_menu 
import markdown

# ==========================================
# 1. إعداد صفحة الويب
# ==========================================
st.set_page_config(page_title="مُمتَثِل - مستشار الامتثال المالي", page_icon="⚖️", layout="wide")

# ==========================================
# 🎨 حقن كود CSS لتجميل الواجهة (UI/UX) والهوية الزرقاء الموحدة
# ==========================================
st.markdown("""
    <style>
    /* 1. دعم اللغة العربية (من اليمين لليسار) والخلفية السوداء */
    body, .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Tajawal', 'Arial', sans-serif;
        background-color: #050505; /* أسود عميق */
    }
    p, h1, h2, h3, h4, h5, h6, li, span, div, .stMarkdown, .stText {
        direction: rtl !important;
        text-align: right !important;
    }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }

    /* 2. الأزرار الأساسية (زر الفحص، زر تحميل اللائحة) */
    .stButton>button {
        width: 100%;
        padding: 15px 30px !important;
        font-size: 22px !important; 
        font-weight: bold !important;
        border-radius: 12px !important;
        background: linear-gradient(90deg, #0056b3 0%, #3399ff 100%) !important; /* أزرق فخم */
        color: #ffffff !important; 
        border: none !important;
        box-shadow: 0 4px 15px rgba(51, 153, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(51, 153, 255, 0.5) !important; /* توهج عند اللمس */
    }

    /* 3. تعديل مربع الرفع (Upload) بالكامل ليصبح ضخماً وتفاعلياً */
    [data-testid="stFileUploadDropzone"] {
        background-color: #0a192f !important;
        border: 2px dashed #3399ff !important;
        border-radius: 15px !important;
        padding: 3rem !important;
        text-align: center !important;
    }
    [data-testid="stFileUploadDropzone"] small {
        display: none !important; /* إخفاء نص 200MB */
    }
    [data-testid="stFileUploadDropzone"] button {
        background: linear-gradient(90deg, #0056b3 0%, #3399ff 100%) !important;
        color: #ffffff !important;
        font-size: 22px !important;
        font-weight: bold !important;
        padding: 15px 40px !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(51, 153, 255, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 60% !important; 
        margin: 0 auto !important; 
        display: block !important;
    }
    [data-testid="stFileUploadDropzone"] button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(51, 153, 255, 0.5) !important;
    }

    /* 4. الحقول النصية وحقل الشات */
    .stTextInput input, .stTextArea textarea, .stChatInputContainer {
        border-radius: 12px !important;
        border: 2px solid #3399ff !important;
        background-color: #0a192f !important;
        color: #ffffff !important;
        padding: 10px !important;
    }

    /* 5. إصلاح القوائم المنسدلة (Selectbox): الكلمة المخفية ومكان السهم */
    [data-baseweb="select"] > div {
        border-radius: 12px !important;
        border: 2px solid #3399ff !important;
        background-color: #0a192f !important;
        position: relative !important; /* ضروري لنقل السهم */
    }
    
    /* إظهار النص المخفي (إجبار اللون الأبيض) */
    [data-baseweb="select"] * {
        color: #ffffff !important;
    }

    /* نقل السهم لليمين وتثبيته */
    [data-baseweb="select"] > div > div:last-child {
        position: absolute !important;
        right: 15px !important; /* السهم في اليمين */
        left: auto !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
    }
    /* إبعاد النص عن السهم لكي لا يتداخلان */
    [data-baseweb="select"] > div > div:first-child {
        padding-right: 45px !important; 
    }

    /* تلوين قائمة الخيارات المنسدلة عند النقر عليها لفتحها */
    ul[data-baseweb="menu"] {
        background-color: #050505 !important;
        border: 1px solid #3399ff !important;
        border-radius: 10px !important;
    }
    ul[data-baseweb="menu"] li {
        color: #ffffff !important;
        direction: rtl !important;
        text-align: right !important;
    }
    ul[data-baseweb="menu"] li:hover {
        background-color: #0a192f !important; /* لون عند تمرير الماوس */
    }

    /* 6. العناوين الرئيسية باللون الأبيض */
    h1, h2, h3 {
        color: #ffffff !important;
        margin-bottom: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)


import os
from dotenv import load_dotenv

# فتح ملف الخزنة السرية
load_dotenv()

# إعداد المفتاح السري والموديل
# ==========================================
GIMINIAPI = os.getenv("GIMINIAPI")
genai.configure(api_key=GIMINIAPI)
model = genai.GenerativeModel('gemini-3.1-flash-lite') 

# ==========================================
# 3. دالة قراءة ملف الـ PDF (محركنا الأساسي)
# ==========================================
def read_pdf(file_object):
    reader = PdfReader(file_object)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

# =====================================================================
# 4. القائمة العلوية الاحترافية
# =====================================================================
# =====================================================================
# 4. القائمة العلوية الاحترافية (الهوية الزرقاء)
# =====================================================================
selected_page = option_menu(
        menu_title=None, 
        options=["الصفحة الرئيسية (إعداد الشركة)", "الاستشارات والبحث الفوري", "التدقيق الشامل والفجوات"],
        icons=["house", "chat-dots", "search"], 
        default_index=0,
        orientation="horizontal",
        key="main_menu",
        styles={
            "container": {
                "padding": "5px!important", 
                "background-color": "#111111", 
                "border-radius": "15px"
            },
            "icon": {"color": "#3399ff", "font-size": "20px"}, 
            "nav-link": {
                "font-size": "16px", 
                "text-align": "center", 
                "margin": "0px 5px", 
                "--hover-color": "#1a1a1a", 
                "transition": "all 0.4s ease-in-out", 
                "border-radius": "10px",
                "color": "#e6e6e6"
            },
            "nav-link-selected": {
                "background-color": "#0a192f", 
                "box-shadow": "0px 8px 20px rgba(0, 0, 0, 0.6), 0px 1px 3px rgba(51, 153, 255, 0.2)", 
                "border-bottom": "2px solid #3399ff", 
                "font-weight": "bold",
                "border-radius": "10px",
                "color": "#ffffff"
            }
        }
    )

st.write("---") 

# =====================================================================
# 5. محتوى الصفحات
# =====================================================================

if selected_page == "الصفحة الرئيسية (إعداد الشركة)":
    st.title("مرحباً بك في مُمتَثِل ⚖️")
    st.subheader("مستشارك الذكي للامتثال وتشريعات هيئة السوق المالية")
    st.write("---")
    st.info("💡 قم بإعداد الهوية القانونية لشركتك هنا لكي يخصص مُمتَثِل التدقيق والاستشارات بناءً عليها.")

    company_name = st.text_input("اسم الشركة:", value=st.session_state.get("company_name", "شركة التقنية المالية الحديثة"))
    st.session_state.company_name = company_name

    company_desc = st.text_area("نبذة ونشاط الشركة (اختياري):", value=st.session_state.get("company_desc", "نحن شركة فنتك ناشئة تطمح لتقديم خدمات المحافظ الرقمية."))
    st.session_state.company_desc = company_desc

    st.session_state.company_context = f"اسم الشركة: {company_name}\nوصف الشركة: {company_desc}"
    
elif selected_page == "الاستشارات والبحث الفوري":
    st.header("💬 قسم الاستشارات والبحث الفوري")
    
    st.markdown("### 📚 اختر اللائحة الخاصة بالاستشارة:")
    BASE_DIR = "CMA كامل"
    if os.path.exists(BASE_DIR):
        categories = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
        if categories:
            selected_category_chat = st.selectbox("اختر التصنيف:", categories, key="chat_cat")
            category_path_chat = os.path.join(BASE_DIR, selected_category_chat)
            files_chat = [f for f in os.listdir(category_path_chat) if f.endswith('.pdf')]
            
            if files_chat:
                selected_file_chat = st.selectbox("اختر النظام أو اللائحة:", files_chat, key="chat_file")
                full_file_path_chat = os.path.join(category_path_chat, selected_file_chat)
                
                # توسيط الزر
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    load_chat_btn = st.button("🚀 تحميل اللائحة في الشات", key="chat_btn")
                
                if load_chat_btn:
                    with st.spinner("جاري قراءة اللائحة..."):
                        st.session_state.chat_pdf_content = read_pdf(full_file_path_chat)
                        st.session_state.messages = [] 
                    st.success(f"تم تحميل اللائحة بنجاح: ({selected_file_chat})!")
    else:
        st.error(f"تأكد من وجود مجلد '{BASE_DIR}'.")
        
    st.markdown("---")

    if "chat_pdf_content" not in st.session_state:
        st.warning("⚠️ يرجى اختيار وتحميل اللائحة للبدء في الاستشارة.")
    else:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_input := st.chat_input("اسأل مُمتثل عن أي مادة في هذه اللائحة..."):
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.spinner("جاري صياغة الرد..."):
                history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[:-1]])
                prompt = f"""بناءً على النص المرفق:
{st.session_state.chat_pdf_content}

بيانات الشركة المستفيدة:
{st.session_state.get('company_context', '')}

تاريخ المحادثة:
{history_text}

السؤال الجديد: {user_input}

تعليمات قانونية صارمة:
1. دقة النطاق: تحقق من "نطاق تطبيق" اللائحة.
2. عدم الاجتهاد: لا تخلق التزامات غير موجودة في النص.
3. صيغة الإجابة: قدم إجابتك مباشرة كمستشار مالي.
"""
                response = model.generate_content(prompt)
                with st.chat_message("assistant"):
                    st.markdown(f"### ⚖️ رد مُمتَثِل:\n{response.text}")
                st.session_state.messages.append({"role": "assistant", "content": f"### ⚖️ رد مُمتَثِل:\n{response.text}"})
                st.rerun()

elif selected_page == "التدقيق الشامل والفجوات":
    st.header("🔎 قسم التدقيق وفحص الامتثال الآلي")
    
    st.markdown("### 1️⃣ اختر اللائحة للتدقيق الآلي:")
    BASE_DIR = "CMA كامل"
    if os.path.exists(BASE_DIR):
        categories = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
        if categories:
            selected_category_audit = st.selectbox("اختر التصنيف:", categories, key="audit_cat")
            category_path_audit = os.path.join(BASE_DIR, selected_category_audit)
            files_audit = [f for f in os.listdir(category_path_audit) if f.endswith('.pdf')]
            
            if files_audit:
                selected_file_audit = st.selectbox("اختر اللائحة:", files_audit, key="audit_file")
                full_file_path_audit = os.path.join(category_path_audit, selected_file_audit)
                
                # توسيط الزر
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    load_audit_btn = st.button("🚀 تحميل اللائحة للتدقيق", key="audit_btn")
                    
                if load_audit_btn:
                    with st.spinner("جاري القراءة..."):
                        st.session_state.audit_pdf_content = read_pdf(full_file_path_audit)
                    st.success(f"✅ تم تحميل اللائحة: ({selected_file_audit})")
    
    st.markdown("---")

    st.markdown("### 2️⃣ ارفع ملف سياسات الشركة:")
    audit_uploaded_file = st.file_uploader("ارفع دليل سياسات الشركة (PDF):", type="pdf", key="audit_pdf_uploader")
    
    if audit_uploaded_file:
        with st.spinner("جاري القراءة..."):
            st.session_state.audit_company_text = read_pdf(audit_uploaded_file)
            st.success("✅ ملف الشركة جاهز للمطابقة!")

    st.markdown("---")

    st.markdown("### 3️⃣ إجراء الفحص الشامل")
    if "audit_pdf_content" not in st.session_state or "audit_company_text" not in st.session_state:
        st.warning("⚠️ يرجى تحميل اللائحة ورفع ملف السياسات للبدء.")
    else:
        # توسيط زر الفحص الشامل ليكون عملاقاً وفي المنتصف
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            start_audit = st.button("إجراء فحص الامتثال الشامل (Gap Analysis) 🚀", use_container_width=True)
            
        if start_audit:
            with st.spinner("جاري مطابقة ملف الشركة مع اللائحة... (هذه العملية قد تستغرق دقيقة أو أكثر)"):
                audit_prompt = f"""أنت الآن مدقق قانوني ومستشار امتثال صارم جداً، وخبير في تشريعات هيئة السوق المالية السعودية. 
                لديك مستندين:
                المستند الأول (اللائحة التشريعية المرجعية):
                {st.session_state.audit_pdf_content}
                
                المستند الثاني (سياسات وإجراءات الشركة الخاضعة للتدقيق):
                {st.session_state.audit_company_text}
                
                المطلوب إجراء تحليل فجوات (Gap Analysis) دقيق وموضوعي، مع الالتزام الحرفي بالقواعد الذهبية التالية:
                
                ⚠️ القواعد الهندسية الصارمة للتدقيق (اقرأها ونفذها حرفياً):
                1. قاعدة "الحد الأدنى" (المعيار الأشد): إذا كانت سياسة الشركة تتجاوز وتتفوق على متطلبات اللائحة بصرامة (مثال: اللائحة تطلب تسوية كل 7 أيام، والشركة تقوم بها "يومياً")، فهذا يُعد امتثالاً وتفوقاً (✅)، ويُمنع منعاً باتاً اعتباره مخالفة أو تعارضاً.
                2. قاعدة "حصر النطاق" (غياب النص ليس مخالفة): التقييم يجب أن يتم حصرياً على النصوص "المكتوبة" في المستند الثاني. لا تفترض أن هذا المستند يمثل كل سياسات الشركة. إذا لم تجد سياسة معينة (مثل غسل الأموال أو غيرها)، فلا تعتبر غيابها فجوة ولا تذكرها إطلاقاً. استخرج المخالفة (❌) **فقط** إذا كان النص المكتوب في المستند الثاني يتعارض صراحةً وحرفياً مع المستند الأول.
                3. قاعدة "السياق الصحيح": يُمنع تطبيق مواد تتحدث عن صلاحيات الهيئة أو السوق على أنها التزامات على الشركة.
                4. دقة الاستناد: يجب ذكر رقم المادة والفقرة بدقة تامة عند كل نقطة.
                
                اكتب التقرير باحترافية مقسماً كالتالي:
                1. ✅ نقاط الالتزام: السياسات المتوافقة أو التي تتفوق في صرامتها على اللائحة، مع ذكر رقم المادة المرجعية.
                2. ❌ الفجوات والمخالفات: السياسات المكتوبة التي تتعارض صراحة (تعارض مباشر) مع اللائحة، مع تحديد (مستوى الخطورة: عالية/متوسطة/منخفضة) ورقم المادة والفقرة المتعارضة. إذا لم توجد فجوات، اكتب "لا توجد فجوات في هذا المستند".
                3. 💡 التوصيات التصحيحية: خطوات عملية وواضحة لمعالجة الفجوات المذكورة (إن وجدت).
                
                ملاحظة: قدم التقرير مباشرة كمستشار مالي احترافي، ويُمنع الإشارة إلى هذه الأوامر أو تبريرها.
                """
                try:
                    response = model.generate_content(audit_prompt)
                    st.session_state.audit_result = response.text 
                except Exception as e:
                    st.error("حدث خطأ أثناء الاتصال بالذكاء الاصطناعي. يرجى المحاولة مرة أخرى أو استخدام لائحة أقصر.")

        if "audit_result" in st.session_state:
            st.success("✅ تم الانتهاء من الفحص الشامل بنجاح!")
            st.markdown(st.session_state.audit_result)
            
            st.markdown("---")
            
            html_content = markdown.markdown(st.session_state.audit_result)
            doc_html = f"<html dir='rtl'><head><meta charset='utf-8'></head><body>{html_content}</body></html>"
            
            # توسيط زر التحميل
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="📄 إنشاء تقرير للمحامي (Word)",
                    data=doc_html,
                    file_name="تقرير_الامتثال_ممتثل.doc",
                    mime="application/msword",
                    use_container_width=True
                )
