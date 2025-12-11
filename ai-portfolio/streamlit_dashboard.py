import streamlit as st
import pymongo
import pandas as pd
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="AI Portfolio - Live MongoDB Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# MongoDB connection
@st.cache_resource
def get_mongo_client():
    client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
    return client

def get_database():
    client = get_mongo_client()
    return client['ai_portfolio']

# Title and header
st.title("🚀 AI Portfolio - Live MongoDB Dashboard")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Dashboard Settings")
    auto_refresh = st.checkbox("Auto Refresh", value=True)
    refresh_interval = st.slider("Refresh Interval (seconds)", 5, 60, 10)
    
    st.markdown("---")
    st.header("📊 Collections")
    collection_choice = st.selectbox(
        "Select Collection",
        ["fraud_events", "chats", "users", "artifacts", "classifier_samples", "motivating_quotes"]
    )

# Get database
db = get_database()

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Collections", len(db.list_collection_names()))

with col2:
    collection = db[collection_choice]
    doc_count = collection.count_documents({})
    st.metric(f"{collection_choice} Documents", doc_count)

with col3:
    st.metric("Database", "ai_portfolio")

st.markdown("---")

# Display collection data
st.header(f"📋 {collection_choice.replace('_', ' ').title()} Data")

# Fetch data
try:
    # Get latest documents
    limit = st.slider("Number of documents to display", 5, 100, 20)
    documents = list(collection.find().sort("_id", -1).limit(limit))
    
    if documents:
        # Convert to DataFrame
        df = pd.DataFrame(documents)
        
        # Convert ObjectId to string for display
        if '_id' in df.columns:
            df['_id'] = df['_id'].astype(str)
        
        # Display dataframe
        st.dataframe(df, use_container_width=True, height=400)
        
        # Show statistics
        st.subheader("📈 Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Data Shape:**", df.shape)
            st.write("**Columns:**", list(df.columns))
        
        with col2:
            st.write("**Memory Usage:**", f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB")
            st.write("**Null Values:**", df.isnull().sum().sum())
        
        # Show raw document
        with st.expander("🔍 View Raw Document (Latest)"):
            st.json(documents[0])
    else:
        st.info(f"No documents found in {collection_choice}")
        
except Exception as e:
    st.error(f"Error fetching data: {str(e)}")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Auto refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
