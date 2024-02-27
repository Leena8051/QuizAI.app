import streamlit as st
import openai
import os
from dotenv import load_dotenv
import json
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()

# Set OpenAI API key
#openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key =st.secrets["OPENAI_API_KEY"]

# Template for questions
TEMPLATE = {
    "questions": [
        {
            "id": 1,
            "question": "What is the purpose of assembler directives?",
            "options": [
                "A. To define segments and allocate space for variables",
                "B. To represent specific machine instructions",
                "C. To simplify the programmer's task",
                "D. To provide information to the assembler"
            ],
            "correct_answer": "D. To provide information to the assembler"
        },
        {
            "id": 2,
            "question": "What are opcodes?",
            "options": [
                "A. Instructions for integer addition and subtraction",
                "B. Instructions for memory access",
                "C. Instructions for directing the assembler",
                "D. Mnemonic codes representing specific machine instructions"
            ],
            "correct_answer": "D. Mnemonic codes representing specific machine instructions"
        }
    ]
}

# Function to extract text from PDF
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content
    return text


# Function to extract text from text file
def extract_text_from_txt(file):
    return file.read().decode("utf-8")

# Function to generate questions
def get_questions(text, num_questions=5):
    prompt = f"""
        Act as a teacher and create {num_questions} multiple-choice questions (MCQs) based on the text.
        The response must be formatted in JSON. Each question contains id, question, options as list,
        correct_answer. This is an example of the response: {TEMPLATE}
        The text is: ````{text}````
        """
    response = openai.ChatCompletion.create(
        model="text-davinci-003",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
        ],
    )
    return json.loads(response["choices"][0]["message"]["content"])["questions"]

# Function to display questions
def display_questions(questions):
    st.subheader("Generated Questions:")
    for question in questions:
        st.write(f"**Question:** {question['question']}")
        st.write("**Options:**")
        for option in question['options']:
            st.write(f"- {option}")
        st.write(f"**Correct Answer:** {question['correct_answer']}")
        st.write("---")

# Main function
def main():
    st.set_page_config(page_title="Quizlet App")
    st.title("Quizlet App")
    st.write("This app generates multiple-choice questions from uploaded files.")

    uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "txt"])
    num_questions = st.number_input("Number of questions to generate", min_value=1, max_value=10, value=5)
    generate_button = st.button("Generate Questions")

    if generate_button:
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "text/plain":
                text = extract_text_from_txt(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload a PDF, Word document, or text file.")
                return
            questions = get_questions(text, num_questions)
            display_questions(questions)
        else:
            st.error("Please upload a file.")

# Run the app
if __name__ == "__main__":
    main()
