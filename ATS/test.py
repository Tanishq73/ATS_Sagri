import google.generativeai as genai

genai.configure(api_key="AIzaSyA0IdXEFZhTCCqDMpMnZTRw-kxRCBA46Z8")
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Explain how AI works")
print(response.text)