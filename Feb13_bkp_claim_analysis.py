import streamlit as st
from PIL import Image
import sys
import re
import json
from google import genai
from google.genai import types
import base64
import os

def format_markdown_json(json_string):
  response_text = re.sub(r"json", "", json_string)
  response_text = re.sub(r"```", "", response_text)
  json_response = json.loads(response_text)
  return json_response

client = genai.Client(
      vertexai=True,
      project="ccinsights3",
      location="us-central1"
  )

def generate_analysis(doc_analysed):
  document1 = types.Part.from_uri(
      file_uri=doc_analysed,
      mime_type="application/pdf",
  )
  text1 = types.Part.from_text(text="""SYSTEM: ```You are an expert Indian lawyer specializing in motor vehicle accident claims. Your task is to meticulously analyze provided supporting documents related to a third-party motor claim. You must apply your deep understanding of Indian motor laws and legal procedures to extract relevant details, assess liability, and provide a reasoned recommendation for the claim. Your analysis should be based solely on the provided documentation. You are to output the final analysis and recommendation in a JSON format.```
INSTRUCTION: ```Carefully review all the provided documents. Your analysis must include, but is not limited to, the following aspects.
1. **Case Overview:** Briefly summarize the accident details including date, time, location and vehicle types involved, and the parties involved.
2. **Claimant Information:** Extract details regarding the claimant, including name, age, address, and nature of injuries sustained, if any. Also include the vehicle registration and its details.
3. **Insured Party Information:** Extract details about the insured party, including name, vehicle registration details, if any.
4. **Witness Testimony:** Identify and summarize witness statements, highlighting their observations of the accident and their assessment of fault, if any. Note the witness names and their contact information if available.
5. **Police Report Analysis:** Analyze any police reports submitted. Identify the key findings of the police investigation, including the assessment of fault, if any. Identify the FIR Number and the location of the police station.
6. **Accident Scene Details:** Describe the accident location including the type of road, condition of road and visibility conditions.
7. **Damage Assessment:** Summarize any damage assessments of the vehicles involved. Include the cost of repairs if available.
8. **Applicable Motor Laws:** Identify relevant sections of Indian motor laws pertinent to the case, e.g., The Motor Vehicles Act, 1988, relevant rules and guidelines for insurance claims, negligence, and liability.
9. **Liability Analysis:** Based on the extracted information, analyze who is at fault for the accident using Indian Motor Law. Explain with reasons. Include all possible scenarios of liabilities of different parties involved.
10. **Claim Recommendation:** Based on your complete analysis, make a clear recommendation on whether to approve the claim or contest it in an Indian court based on the principles of Indian Motor law. Explain the reasoning for your recommendation.
11. **Supporting Evidence:** List all documents that were provided for your review. This should be a list of strings which includes names of all documents used to prepare the analysis.
Your final output must be a single JSON object. The key of the object will be \"analysis\" and the value would be another JSON object containing the 11 points above as per below given output format.```
OUTPUT:
```json
{
 "analysis": {
  "case_overview": "",
  "claimant_information": {
   "name": "",
   "age": "",
   "address": "",
   "family_member": "",
   "vehicle_details": null,
   "injuries": ""
  },
  "insured_party_information": {
   "name": "",
   "vehicle_registration": "",
   "vehicle_type": ""
  },
  "witness_testimony": [
   {
    "name": "",
    "age": "",
    "address": "",
    "statement": ""
   }
  ],
  "police_report_analysis": {
   "fir_number": "",
   "police_station": "",
   "sections_applied": [
   ],
   "key_findings": ""
  },
  "accident_scene_details": {
   "location": "",
   "condition": "",
   "visibility": ""
  },
   "damage_assessment": {
   "vehicle_damage": "",
   "repair_costs": "If any else 'Not Applicable'",
   "losses" : "If any else 'Not Applicable'",
  },
  "applicable_motor_laws": [
  ],
  "liability_analysis": "",
  "actual_judgement" : "",
  "requested_compensation": "If any else 'Not Applicable'",
  "approved_compensation": "If any else 'Not Applicable'",
  "claim_recommendation": "Any recommended based on analyzed document as an Indian lawyer to an Insurance company",
  "defending_against_judgement": "Any recommended options as an Indian lawyer according to Indian Motor Law to avoid penalties in such case or counter the judgement as an Insurance company.",
  "provided_supporting_evidence": [
  ]
 }
}
```""")

  model = "gemini-2.0-flash-exp"
  contents = [
    types.Content(
      role="user",
      parts=[
        document1,
        text1
      ]
    )
  ]
  tools = [
    types.Tool(google_search=types.GoogleSearch())
  ]
  generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    max_output_tokens = 8192,
    response_modalities = ["TEXT"],
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
  )

  response = client.models.generate_content(
    model = model,
    contents = contents,
    config = generate_content_config,
    )
  print(response.text)
  return response.text

def display_json(json_data):
    """Displays JSON data in a structured format using Streamlit."""

    st.write("## Analysis Report")
    try:
        # Check if the input is a valid JSON string and parse it
        if isinstance(json_data, str):
            json_data = json.loads(json_data)

        if isinstance(json_data, dict) and "analysis" in json_data:
            analysis = json_data["analysis"]
            for key, value in analysis.items():
                st.subheader(f"***{key.replace('_', ' ').title()}***", divider="gray")
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        st.write(f"- **{sub_key.replace('_', ' ').title()}**: {sub_value}")
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            for sub_key, sub_value in item.items():
                                st.write(f" - **{sub_key.replace('_',' ').title()}**: {sub_value}")
                        else:
                           st.write(f"- {item}")

                else:
                    st.write(f"- {value}")
        else:
            st.write("Invalid JSON format. 'analysis' key not found.")

    except json.JSONDecodeError:
        st.write("Invalid JSON input.")

# Auth Logic

def creds_entered():
    if st.session_state["user"].strip() == "hdfcergo" and st.session_state ["passwd"].strip() == "GenAIWithGCP$2025#":
        st.session_state["authenticated"] = True
    else:
        st.session_state["authenticated"] = False
        if not st.session_state["passwd"]:
            st.warning("Please enter password.")
        elif not st.session_state["user"]:
            st.warning("Please enter username.")
        else:
            st.error("Invalid Username/Password: face_with_raised_eyebrow:")

def authenticate_user():
    if "authenticated" not in st.session_state:
        st.text_input(label="Username:", value="", key="user", on_change=creds_entered)
        st.text_input(label="Password", value="", key="passwd", type="password", on_change=creds_entered)
        return False
    else:
        if st.session_state["authenticated"]:
            return True
        else:
            st.text_input(label="Username:", value="", key="user", on_change=creds_entered)
            st.text_input(label="Password:", value="", key="passwd", type="password", on_change=creds_entered)
            return False

def upload_to_gcs(uploaded_file, bucket_name, destination_blob_name):
    """Uploads a file to the Google Cloud Storage bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    try:
        blob.upload_from_file(uploaded_file)
        st.success(f"File '{uploaded_file.name}' uploaded to GCS successfully!")
    except Exception as e:
        st.error(f"Error uploading file: {e}")

def download_file_from_gcs(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    try:
        file_bytes = blob.download_as_bytes()
        st.download_button(
            label="Download PDF",
            data=file_bytes,
            file_name=destination_file_name,
            mime="application/pdf",
        )
    except Exception as e:
        st.error(f"Error downloading file: {e}")            

def main():
  #if authenticate_user():
    st.markdown("<h2 style='color: red;'>3rd Party Motor Claims Analysis</h2>", unsafe_allow_html=True)

    # Load the logo image
    logo_image = Image.open("hdfc-ergo-logo.png")
    st.sidebar.image(logo_image, width=150)

    # Recommendation section added to the sidebar
    st.sidebar.write("""                     """)
    st.sidebar.subheader("Join the brand trusted by over 1.6 Crore+ Happy Customers@ today!")

    # Add Car Image
    claim_image = Image.open("magic_claim.png")  
    st.sidebar.image(claim_image, width=250) # Adjust width as needed 

    # Document selection dropdown
    document_options = {
        "Claim-1001-Gujarati-Judgement": "gs://hdfc-ergo-motor-claim-analysis/GUJARATI_JUDGEMENT_SCAN_COPY.pdf",
        "Claim-1002-Bengali-FIR": "gs://hdfc-ergo-motor-claim-analysis/Bengali_Certified_FIR.pdf",
        "Claim-1003-Tamil-Statement": "gs://hdfc-ergo-motor-claim-analysis/TAMIL_STATEMENT.pdf",
        "Claim-1004-Tamil-FIR": "gs://hdfc-ergo-motor-claim-analysis/TAMIL_FIR.pdf",
        "Claim-1005-Bengali-Witness": "gs://hdfc-ergo-motor-claim-analysis/Bengali_161_Witness_Statements.pdf",
    }

    selected_document = st.selectbox("Select Claim Number", list(document_options.keys()))

    if st.button("Analyze"):
        try:
          doc_uri = document_options[selected_document]
          analysis_result = generate_analysis(doc_uri)
          content_compliance_json = format_markdown_json(analysis_result)  # Properly format JSON

          # Display the formatted JSON analysis
          # st.subheader("Analysis Results:")
          # st.json(content_compliance_json)
          display_json(content_compliance_json)

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
