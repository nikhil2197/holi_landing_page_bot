import streamlit as st
import os
from utils.pdf_processor import PDFProcessor
from utils.vector_store import VectorStore
from utils.chat_helper import ChatHelper

# Page configuration
st.set_page_config(
    page_title="Holi Playdate Info Assistant",
    page_icon="🎨",
    layout="wide"
)

# Load custom CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None

def load_pdf_and_create_index():
    """Load PDF and create vector store index"""
    pdf_path = "attached_assets/The Holi Playdate_ Consolidated Information.pdf"
    pdf_processor = PDFProcessor(pdf_path)
    
    if pdf_processor.load_pdf():
        chunks = pdf_processor.get_chunks()
        vector_store = VectorStore()
        vector_store.create_index(chunks)
        return vector_store
    return None

def create_sidebar():
    """Create and populate the sidebar"""
    with st.sidebar:
        st.header("🎨 Holi Playdate")
        st.markdown("---")
        
        with st.container():
            st.markdown("""
            <div class="sidebar-content">
                <div class="event-highlight">
                    <h3>Event Highlights</h3>
                    <ul>
                        <li>Family-friendly Holi celebration</li>
                        <li>Interactive activities</li>
                        <li>Safe colors and fun</li>
                        <li>Cultural experience</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.button(
            "🎟️ Book Now",
            key="book_now",
            help="Click to proceed to ticket booking"
        )

def main():
    initialize_session_state()
    
    # Load vector store if not already loaded
    if not st.session_state.vector_store:
        st.session_state.vector_store = load_pdf_and_create_index()
    
    # Create sidebar
    create_sidebar()
    
    # Main chat interface
    st.title("👋 Welcome to Holi Playdate Assistant")
    
    # Display welcome message if no messages yet
    if not st.session_state.messages:
        welcome_message = """
        Hi! I'm Alfred, your Holi Playdate Assistant. I'm here to help you learn more about the Holi Playdate event at Openhouse.
        
        You can ask me questions like:
        - 🎨 What activities will be happening?
        - 📍 Where is the event located?
        - 💰 How much does it cost?
        - 🕒 What are the timings?
        - 👪 Is it suitable for all ages?
        
        Feel free to ask anything about the event, and I'll do my best to help!
        """
        st.session_state.messages.append({"role": "assistant", "content": welcome_message})
    
    # Initialize chat helper
    chat_helper = ChatHelper()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about the Holi Playdate event!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            if st.session_state.vector_store:
                context = st.session_state.vector_store.get_relevant_context(prompt)
                response = chat_helper.generate_response(prompt, context)
            else:
                response = chat_helper.generate_response(prompt)
            
            st.markdown(response["answer"])
            st.session_state.messages.append(
                {"role": "assistant", "content": response["answer"]}
            )

if __name__ == "__main__":
    main()
