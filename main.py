import google.generativeai as genai
from pypdf import PdfReader
import os

# 1. إعداد المفتاح (ضع مفتاحك السري بين علامات التنصيص)
genai.configure(api_key="place your API key here")

# 2. تعريف الموديل
model = genai.GenerativeModel('gemini-3.5-flash')

# 3. دالة قراءة ملفات الـ PDF
def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# 4. التفاعل مع المستخدم
print("Welcome to Momtathil - Your Saudi Financial Compliance Advisor.")
file_name = input("Please enter the PDF file name: ")

# التأكد من وجود الملف ثم تحليله
if os.path.exists(file_name):
    print("Processing regulation file... Please wait a moment.")
    pdf_content = read_pdf(file_name)
    
   
    # حلقة تكرار للسماح بسؤال "مُمتَثِل" أكثر من مرة
    while True:
        user_input = input("\nAsk Momtathil a question (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        
        # دمج محتوى اللائحة مع سؤال المستخدم في طلب واحد
        prompt = f"Based on the provided legal text: {pdf_content[:15000]} \n\nQuestion: {user_input}"
        
        response = model.generate_content(prompt)
        print("\n--- Momtathil's Response ---")
        print(response.text)
        
else:
    print("Error: File not found. Please ensure the file is in the same folder as the code.")
