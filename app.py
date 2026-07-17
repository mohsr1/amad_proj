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
genai.configure(api_key="AQ.Ab8RN6IOSK4gQHFQCa09Wzc1oz3vjfUGIzOVf3WdS7dmKfvY_A")  # ضع مفتاحك السري هنا
model = genai.GenerativeModel('gemini-3.1-flash-lite')  # اختر الموديل المناسب

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
                
                # الكود الجديد لمنع القراءة التلقائية وإضافة زر الاعتماد
                if st.session_state.get("current_file") != full_file_path:
                    st.info("👈 اللائحة مختارة ولكن لم تُقرأ بعد. يرجى الضغط على الزر للبدء.")
                    if st.button("تحليل واعتماد اللائحة 🚀"):
                        with st.spinner("انتظر لحظة من فضلك ... جاري قراءة وتحليل اللائحة..."):
                            st.session_state.pdf_content = read_pdf(full_file_path)
                            st.session_state.current_file = full_file_path
                            st.rerun()
                else:
                    st.success("تم رفع وتحليل اللائحة بنجاح! مُمتَثِل جاهز لأسئلتك.")
                
        else:
            st.info("لا توجد ملفات PDF داخل هذا التصنيف حالياً.")
else:
    st.error(f"لم يتم العثور على المجلد الأساسي '{BASE_DIR}'. تأكد من وجوده.")

    st.write("---")
    
    
    
    
# === إنشاء التبويبات العلوية ===
    tab1, tab2 = st.tabs(["💬 الاستشارات والبحث الفوري", "🔎 التدقيق الشامل والفجوات"])

    # -----------------------------------------
    # التبويب الأول: الاستشارات (الكود القديم مدمج هنا)
    # -----------------------------------------
    with tab1:
        # 1. تهيئة ذاكرة المحادثة إذا لم تكن موجودة
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 2. عرض الرسائل السابقة المعتمدة في الذاكرة
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # 3. خانة إدخال السؤال الذكية في أسفل الشاشة
        if user_input := st.chat_input("اسأل مُمتثل عن أي مادة أو بند في هذه اللائحة..."):
            # عرض سؤال المستخدم فوراً في الشات
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})

            # توليد الرد من الذكاء الاصطناعي
            with st.spinner("جاري صياغة الرد القانوني..."):
                history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[:-1]])
                prompt = f"""بناءً على النص المرفق:
{st.session_state.get('pdf_content', '')}

بيانات الشركة المستفيدة (يجب تخصيص الإجابة بناءً عليها بدقة قانونية):
{st.session_state.get('company_context', '')}

تاريخ المحادثة:
{history_text}

السؤال الجديد: {user_input}

تعليمات قانونية صارمة جداً (يجب الالتزام بها حرفياً):
1. دقة النطاق: قبل الإجابة، تحقق من "نطاق تطبيق" اللائحة. هل تخاطب اللائحة الكيان المذكور في بيانات الشركة بشكل صريح ومباشر؟
2. منع القياس الخاطئ: إذا كان نشاط الشركة (مثلاً: محفظة رقمية) يختلف قانونياً عن الكيانات المستهدفة باللائحة (مثلاً: أسواق أو مراكز إيداع)، يُمنع منعاً باتاً تطبيق شروط الكيانات المستهدفة على الشركة (مثل متطلبات رأس المال أو التراخيص الكبرى).
3. المصارحة المطلقة: إذا كانت اللائحة لا تنطبق، ابدأ إجابتك بوضوح تام قائلاً: "هذه اللائحة لا تنطبق بشكل مباشر على نشاط شركتكم"، ثم اشرح كيف يمكن أن تتقاطع اللائحة معكم بصفة ثانوية فقط (كعضو أو عميل) إذا وُجد ذلك في النص.
4. عدم الاجتهاد: لا تخلق التزامات غير موجودة في النص، واذكر أرقام المواد كمرجع دائم.
5. صيغة الإجابة: قدم إجابتك مباشرة كمستشار مالي، ويُمنع منعاً باتاً الإشارة إلى وجود تعليمات أو أوامر تلقيتها في هذا النص.
"""
                response = model.generate_content(prompt)

                # عرض رد ممتثل وحفظه في الذاكرة
                with st.chat_message("assistant"):
                    st.markdown(f"### ⚖️ رد مُمتَثِل:\n{response.text}")
                st.session_state.messages.append({"role": "assistant", "content": f"### ⚖️ رد مُمتَثِل:\n{response.text}"})

    # -----------------------------------------
    # التبويب الثاني: التدقيق الشامل والفجوات (القسم الجديد)
    # -----------------------------------------
    with tab2:
        st.subheader("🔎 قسم التدقيق وفحص الامتثال الآلي")
        st.info("هذا القسم يقوم بمقارنة سياسة شركتك المرفقة مع اللائحة المختارة لاستخراج الفجوات آلياً.")
        
        # جلب ملف الشركة من الذاكرة إذا كان مرفوعاً
        company_file_content = st.session_state.get("company_pdf_text", "")
        
        # حماية: التأكد من توفر الملفين قبل السماح بالفحص
        if not company_file_content:
            st.warning("⚠️ يرجى رفع ملف سياسات الشركة من القائمة الجانبية (على اليسار) لتفعيل هذه الخاصية.")
        elif "pdf_content" not in st.session_state:
            st.warning("⚠️ يرجى اختيار اللائحة والضغط على زر 'تحليل واعتماد اللائحة' أولاً.")
        else:
            if st.button("إجراء فحص الامتثال الشامل (Gap Analysis) 🚀", use_container_width=True):
                with st.spinner("جاري مطابقة ملف الشركة مع اللائحة واستخراج الفجوات. قد تستغرق هذه العملية ثواني معدودة..."):
                    audit_prompt = f"""أنت الآن مدقق قانوني صارم وخبير في تشريعات هيئة السوق المالية السعودية. 
                    لديك مستندين:
                    المستند الأول (اللائحة التشريعية من هيئة السوق المالية):
                    {st.session_state.pdf_content}
                    
                    المستند الثاني (سياسات وإجراءات الشركة الداخلية):
                    {company_file_content}
                    
                    المطلوب منك إجراء تحليل فجوات (Gap Analysis) دقيق وعملي فوراً، وطباعة تقرير احترافي مقسم كالتالي:
                    1. ✅ نقاط الالتزام: اذكر المواد التي تلتزم بها الشركة في ملفها الداخلي مع رقم المادة.
                    2. ❌ الفجوات والمخالفات: اذكر المواد التي خالفتها الشركة أو أغفلت ذكرها في ملفها الداخلي، مع التنبيه على خطورتها ورقم المادة في اللائحة.
                    3. 💡 التوصيات التصحيحية: خطوات عملية واضحة للمحامي لتعديل ملف الشركة ليصبح ممتثلاً.
                    
                    ملاحظة: قدم التقرير مباشرة كمستشار مالي، ويُمنع منعاً باتاً الإشارة إلى وجود تعليمات أو أوامر خلفية.
                    """
                    audit_response = model.generate_content(audit_prompt)
                    st.success("تم الانتهاء من الفحص الشامل!")
                    st.markdown(audit_response.text)
