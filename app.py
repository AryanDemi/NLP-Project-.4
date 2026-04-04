import os
import tempfile
import streamlit as st
from PIL import Image

# Import the logic from our script
# Note: we are importing functions, not running the CLI block
from medical_report_simplifier import extract_text, extract_and_embed_medical_terms, simplify_medical_report, get_brief_summary, check_if_medical_report

# Configure Streamlit page
st.set_page_config(
    page_title="Medical Report Simplifier",
    page_icon="🩺",
    layout="centered"
)

st.title("🩺 Medical Report Simplifier")
st.markdown("""
Welcome! Upload your medical report (PDF or Image) below. 
Our AI will extract the text, identify key medical terms, and provide a simplified, patient-friendly explanation.

*Disclaimer: This is an AI assistant, not a doctor. Always consult a healthcare professional for medical advice.*
""")

# File uploader
uploaded_file = st.file_uploader("Upload your medical report", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Display the uploaded image (if it's an image)
    if uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
        st.image(uploaded_file, caption="Uploaded Report", use_container_width=True)
    
    st.info("File uploaded successfully. Click the button below to analyze it.")
    
    if st.button("Analyze & Simplify Report"):
        with st.spinner("Processing your report... This may take a minute."):
            try:
                # Save the uploaded file temporarily so our existing functions can process it via file_path
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # Step 1: OCR
                st.text("📝 Extracting text via OCR...")
                raw_text = extract_text(tmp_file_path)
                
                if not raw_text:
                    st.error("upload a valid medical report")
                    os.remove(tmp_file_path)
                    st.stop()
                    
                # Step 2: Validate Document
                st.text("🔍 Checking if document is a medical report...")
                is_medical = check_if_medical_report(raw_text)
                
                if not is_medical:
                    st.error("upload a valid medical report")
                    os.remove(tmp_file_path)
                    st.stop()
                
                # Step 3: Extract Terms
                st.text("🧬 Finding medical terminology...")
                terms, _ = extract_and_embed_medical_terms(raw_text)
                
                # Step 3: LLM Simplification
                st.text("Generating simplified explanation...")
                simplified_output = simplify_medical_report(raw_text, terms)
                
                # Step 4: Brief Summary
                st.text("Generating brief summary...")
                brief_summary = get_brief_summary(simplified_output)
                
                # Clean up temporary file
                os.remove(tmp_file_path)
                
                # Display Results
                st.success("Analysis Complete!")
                st.markdown("---")
                
                tab1, tab2 = st.tabs(["📝 Brief Summary", "🧾 Detailed Simplified Report"])
                
                with tab1:
                    st.subheader("📝 Brief Summary")
                    st.info(brief_summary)
                    
                with tab2:
                    st.subheader("🧾 Detailed Simplified Report")
                    st.markdown(simplified_output)
                
                with st.expander("View Raw Extracted Text (For Reference)"):
                    st.text(raw_text)
                    
            except Exception as e:
                st.error(f"An error occurred during processing: {e}")
