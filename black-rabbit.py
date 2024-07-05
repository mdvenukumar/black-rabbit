import streamlit as st
import google.generativeai as genai
from tavily import TavilyClient
import requests
from bs4 import BeautifulSoup

# API keys and configurations (consider using environment variables for security)
DEFAULT_GEMINI_API_KEY = "AIzaSyAmm7Dvr2Rr6DbNUo4bV5bCWDYWSU2k3Sg"

TAVILY_API_KEY = "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"

# Initialize clients
genai.configure(api_key=DEFAULT_GEMINI_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)

def get_comprehensive_research(topic, subtopic):
    try:
        search_results = tavily.search(
            query=f"{topic} {subtopic}",
            search_depth="advanced",
            max_results=10
        )
        return search_results
    except Exception as e:
        st.error(f"Error fetching research: {e}")
        return None

def get_blogs(topic, subtopic):
    try:
        blog_results = tavily.search(
            query=f"{topic} {subtopic} site:medium.com OR site:wikipedia.org",
            search_depth="advanced",
            max_results=5
        )
        return blog_results['results']
    except Exception as e:
        st.error(f"Error fetching blog posts: {e}")
        return []

def get_videos(topic, subtopic):
    try:
        video_results = tavily.search(
            query=f"{topic} {subtopic} site:youtube.com",
            search_depth="advanced",
            max_results=4
        )
        return video_results['results']
    except Exception as e:
        st.error(f"Error fetching videos: {e}")
        return []

def process_with_gemini(textual_content, topic, subtopic):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Summarize the following research content about {topic} (specifically {subtopic}) in a concise and informative manner:

    {textual_content}

    Provide a comprehensive summary that captures the main points, key information, and any notable trends or insights. 
    Structure the summary with clear headings and bullet points for easy readability.
    Aim for a summary of about 500 words.
    """
    response = model.generate_content(prompt)
    return response.text

def extract_blog_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([p.text for p in paragraphs[:3]])  # Get first 3 paragraphs
        return content[:500] + "..."  # Truncate to 500 characters
    except Exception as e:
        return f"Error extracting content: {str(e)}"

def main():
    st.set_page_config(page_title="Black Rabbit", page_icon="🌙", layout="wide")

    st.title("🌙 BLACK RABBIT")
    st.info("Powered by Gemini AI")

    with st.expander("ℹ️ How to use this app", expanded=False):
        st.write("""
        1. Enter your main topic and subtopic
        2. Click 'Conduct Research' to gather and process information
        3. Review the research summary, related videos, and blog posts
        """)

    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("📌 Main Topic:", placeholder="E.g., Artificial Intelligence")
    with col2:
        subtopic = st.text_input("🔍 Subtopic:", placeholder="E.g., Ethics in AI")

    if st.button("🔬 Conduct Research", key="research"):
        if topic and subtopic:
            with st.spinner("🕵️ Gathering and processing research..."):
                research_results = get_comprehensive_research(topic, subtopic)
                if research_results:
                    textual_content = "\n\n".join([f"Title: {result['title']}\nContent: {result['content']}" for result in research_results['results']])
                    summary = process_with_gemini(textual_content, topic, subtopic)
                    
                    # Get blogs and videos separately
                    blogs = get_blogs(topic, subtopic)
                    videos = get_videos(topic, subtopic)
                    
                    # Display summary
                    st.subheader("📚 Research Summary")
                    st.markdown(summary)

                    # Display videos in a separate section
                    st.subheader("🎥 Related Videos")
                    if videos:
                        video_cols = st.columns(2)
                        for i, video in enumerate(videos[:4]):  # Limit to 4 videos
                            with video_cols[i % 2]:
                                st.video(video['url'])
                                st.write(f"**{video['title']}**")
                    else:
                        st.info("No related videos found.")
                else:
                    st.error("❌ Failed to gather research.")
        else:
            st.warning("⚠️ Please enter a topic and subtopic for research.")

    st.sidebar.title("⚙️ Settings")
    custom_api_key = st.sidebar.text_input("Custom Gemini API Key (optional):", type="password")
    if custom_api_key:
        genai.configure(api_key=custom_api_key)

    st.sidebar.title("ℹ️ About")
    st.sidebar.info("Strangled by research?  Black Rabbit  hacks the web, feeding your creativity with AI-powered insights. Craft fire content. Less time, more BOOM.")
    hide_streamlit_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
if __name__ == "__main__":
    main()
