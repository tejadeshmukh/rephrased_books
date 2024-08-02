import streamlit as st
import os
import requests
from pdf2image import convert_from_path
import base64
import tempfile
import json
import time
from io import BytesIO 
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import google.generativeai as genai
import PIL
from IPython.display import display, Markdown
from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv('api_key')
gemini_api_key = os.getenv('gemini_api_key')



#gemini ai api 
genai.configure(api_key=gemini_api_key)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')


def pdf_to_images(pdf_path):
    return convert_from_path(pdf_path)


def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def extract_text_gemini(image):
  response = gemini_model.generate_content([image, "Strictly ignore the tables in the image , and extract only remaining text"])
  return response.text

def rewrite_text_gemini(text):
    prompt = (
        f"{text}\n\n"
        "Rewrite the given text in different wordings, maintaining all original facts."
        "Make sure to keep the title same , and change the headings pattern."
        "Rewrite only the provided text without adding any extra information."
        "Strcitly ensure the rewritten text is grammatically correct and follows standard Hindi conventions ('वर्तनी शुद्ध करे')."
        "Make sure the overall rewritten text makes sense and is coherent"
        
    )
    response = gemini_model.generate_content([prompt])
    return response.text

def main():
    st.title("PDF Text Extractor and Rewriter")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        images = pdf_to_images(tmp_file_path)
        rewritten_texts = []
        
        for i, image in enumerate(images):
            st.subheader(f"Page {i+1}")
            st.image(image, caption=f"Page {i+1}", use_column_width=True)
            encoded_image = encode_image(image)
            with st.spinner(f"Processing page {i+1}..."):
                extracted_text  = extract_text_gemini(image)
                rewritten_text = rewrite_text_gemini(extracted_text)
            # st.markdown(f"## extracted text for page {i+1}")
            # st.markdown(extracted_text, unsafe_allow_html=True)
            st.markdown(f"## Rewritten text for page {i+1}")
            st.markdown(rewritten_text, unsafe_allow_html=True)
            rewritten_texts.append(rewritten_text)
            time.sleep(1)
        
        os.unlink(tmp_file_path)

if __name__ == "__main__":
    main()