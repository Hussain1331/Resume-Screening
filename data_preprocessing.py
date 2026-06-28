import re
import PyPDF2
import docx
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
SET_STOPWORDS = set(stopwords.words('english'))

def extract_text_from_pdf(pdf_path):
    """Extracts raw text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text

def extract_text_from_docx(docx_path):
    """Extracts raw text from a Word document (.docx)."""
    text = ""
    try:
        doc = docx.Document(docx_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + " "
    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {e}")
    return text

def clean_resume_text(text):
    """Cleans raw text by removing URLs, emails, special characters, and extra whitespaces."""
    if not text:
        return ""
    
    # 1. Convert to lowercase
    text = text.lower()
    
    # 2. Remove URLs
    text = re.sub(r'http\S+\s*', ' ', text)
    
    # 3. Remove Email addresses
    text = re.sub(r'\S+@\S+', ' ', text)
    
    # 4. Remove special characters, punctuation, and digits (optional, but good for basic similarity)
    # We keep letters and spaces
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # 5. Remove stop words and tokenize/rejoin
    words = text.split()
    filtered_words = [word for word in words if word not in SET_STOPWORDS]
    
    # 6. Remove extra whitespaces
    cleaned_text = " ".join(filtered_words)
    
    return cleaned_text
#test
if __name__ == "__main__":
    sample_raw_text = """
    John Doe | Software Engineer 
    Email: john.doe@email.com | Portfolio: https://johndoe.dev
    Developed an awesome AI application using Python, SQL, and Docker!! 
    Experienced with Agile methodologies (Scrum).
    """
    
    print("--- Original Text ---")
    print(sample_raw_text.strip())
    
    print("\n--- Cleaned Text ---")
    print(clean_resume_text(sample_raw_text))