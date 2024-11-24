# File: app_ui.py

import streamlit as st
from IPython.display import IFrame

# Function to generate Neuronpedia Dashboard HTML iframe
html_template = "https://neuronpedia.org/{}/{}/{}?embed=true&embedexplanation=true&embedplots=true&embedtest=true&height=300"
def get_dashboard_html(sae_release="gemma-2-2b", sae_id="20-gemmascope-res-16k", feature_idx=0):
    return html_template.format(sae_release, sae_id, feature_idx)

# Streamlit App Layout
st.set_page_config(page_title="Custom UI Dashboard", layout="wide")

# Title and Header
st.title("Custom Dashboard - BA and BB Inspired")
st.markdown("This application replicates the UI from the provided images.")

# Sidebar for Options
st.sidebar.header("Settings")
option1 = st.sidebar.selectbox("Select Dataset:", ["Dataset A", "Dataset B"])
option2 = st.sidebar.radio("Visualization Type:", ["Histogram", "Bar Chart", "Line Chart"])
sidebar_slider = st.sidebar.slider("Select Data Range", 0, 100, (20, 80))

# Main Layout
tab1, tab2, tab3 = st.tabs(["Overview", "Detailed View", "Neuronpedia Integration"])

# Tab 1: Overview
with tab1:
    st.subheader("Overview Section")
    st.text("Provide a summary or quick insight into the dataset.")
    st.metric(label="Metric A", value="42", delta="+2%")
    st.metric(label="Metric B", value="85", delta="-5%")
    st.metric(label="Metric C", value="60", delta="+8%")
    st.bar_chart([1, 2, 3, 4, 5])  # Placeholder for Bar Chart

# Tab 2: Detailed View
with tab2:
    st.subheader("Detailed View Section")
    st.text("Visualize the data in detail here.")
    st.slider("Adjust Threshold", 0, 100, 50, key="threshold_slider")
    if option2 == "Histogram":
        st.hist_chart([10, 20, 15, 25, 30])  # Placeholder for histogram
    elif option2 == "Bar Chart":
        st.bar_chart([10, 30, 20, 40, 25])  # Placeholder for bar chart
    else:
        st.line_chart([10, 15, 20, 25, 30])  # Placeholder for line chart

# Tab 3: Neuronpedia Integration
with tab3:
    st.subheader("Neuronpedia Dashboard")
    sae_release = st.text_input("SAE Release:", "gemma-2-2b")
    sae_id = st.text_input("SAE ID:", "20-gemmascope-res-16k")
    feature_idx = st.number_input("Feature Index:", min_value=0, value=10004, step=1)
    
    # Generate and display the IFrame
    html = get_dashboard_html(sae_release=sae_release, sae_id=sae_id, feature_idx=feature_idx)
    st.markdown("Neuronpedia Dashboard:")
    st.components.v1.html(html, height=600)

# Footer
st.markdown("---")
st.text("Created by Streamlit - Custom UI inspired by BA and BB images.")
