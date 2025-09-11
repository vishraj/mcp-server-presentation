from mcpserver import invoke_agent
import asyncio
import os
import boto3
import streamlit as st
import html
st.set_page_config(layout="wide")
import pandas as pd
import matplotlib.pyplot as plt

REGION = "us-east-1"
AGENT_ID = "NDIOYYWRVL"       # The Bedrock Agent ID
AGENT_ALIAS_ID = "NWYFAEELRA" # The alias for your agent

# Create Bedrock Agent Runtime client
client = boto3.client("bedrock-agent-runtime", region_name=REGION)

def plot_bar(df, x, y, title, horizontal=False):
    fig, ax = plt.subplots(figsize=(10,5))
    if horizontal:
        ax.barh(df[x], df[y])
        ax.set_xlabel(y)
        ax.set_ylabel(x)
    else:
        ax.bar(df[x], df[y])
        ax.set_xlabel(x)
        ax.set_ylabel(y)
    ax.set_title(title)
    st.pyplot(fig)


# Streamlit app main function
def main_ui():
    output_text = ""
    #response = ""

    # Query UI
    st.subheader("Ask a question")
    #top_k = int(os.getenv("TOP_K", "4"))

    # Use form so hitting Enter submits
    with st.form(key="query_form"):
        q = st.text_input("e.g., What soil type and pH are best for pistachios?", key="user_query")
        submit_btn = st.form_submit_button("Ask")
    print(q)
    if submit_btn and q.strip():
        with st.spinner("Thinking locally..."):
            agent=invoke_agent()
            print("before calling")
            response=asyncio.run(agent.invoke(q))
            print("after calling")
        #df = pd.DataFrame(data)
        #plot_bar(df, "store_name", "store_sales", "Store Performance by Revenue")
        
        # Check if the response contains an image
        if isinstance(response, dict) and response.get("type") == "image":
            image_bytes = base64.b64decode(response["data"])
            st.image(image_bytes)
        else:
            # Otherwise render text as usual
            st.markdown("### Answer")
            st.text(response)
            
        #st.markdown("### Answer")
        #st.markdown((response))

        #render_sources(response)




# Add custom CSS to set the zoom level to 90%
st.markdown(
    """
    <style>
        body {
            zoom: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
# Adding (css)stye to application
with open('style/final.css') as f:
    st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)


# Adding company logo
# imcol1, imcol2, imcol3, imcol4, imcol5 = st.columns((3,4,.5,4,3))
imcol1, imcol2, imcol5 = st.columns((5,3.5,5))

with imcol2:
    st.write("# ")
    st.image('image/default_logo.png')


st.markdown("<p style='text-align: center; color: black; font-size:25px;'><span style='font-weight: bold'></span>Conversational AI with a Knowledge Base </p>", unsafe_allow_html=True)
st.markdown("<hr style=height:2.5px;margin-top:0px;width:100%;background-color:#5480cb;>",unsafe_allow_html=True)


with st.sidebar:

    st.markdown("<p style='text-align: center; Black: ; font-size:25px;'><span style='font-weight: bold; font-family: century-gothic';></span>Solutions Scope</p>", unsafe_allow_html=True)
    vAR_LLM_model = st.selectbox("",['GEN AI Models',"gpt-3.5-turbo-16k-0613","gpt-4-0314","gpt-3.5-turbo-16k","gpt-3.5-turbo-1106","gpt-4-0613","gpt-4-0314"],key='text_llmmodel')
    vAR_LLM_framework = st.selectbox("",['Framework',"Langchain"],key='text_framework')
    vAR_Gcp_cloud = st.selectbox("",["Cloud Services","VM Instance","Computer Engine","Cloud Storage"],key='text2')
    st.markdown("#### ")
    href = """<form action="#">
            <input type="submit" value="Clear/Reset"/>
            </form>"""
    st.sidebar.markdown(href, unsafe_allow_html=True)
    st.markdown("# ")
    st.markdown("<p style='text-align: center; color: Black; font-size:20px;'>Build & Deployed on<span style='font-weight: bold'></span></p>", unsafe_allow_html=True)
    

    s2,s3,s4=st.columns((4,4,4))

    with s3:
        st.markdown("### ")
        st.image('image/aws.png')

    st.divider()

    uploaded = st.file_uploader(
        "➕ Add more documents",
        type=["pdf", "txt", "md", "docx"],
        accept_multiple_files=True
    )
    add_btn = st.button("Add to Index")

try:
    # if vAR_AI_application == "Lab-6":
    main_ui()
except BaseException as e:
    st.error("An error occurred. Kindly contact the technical support team.")
    print(e)
