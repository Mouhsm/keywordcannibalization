import streamlit as st
import pandas as pd

def main():
    st.title("Keyword Cannibalization Analyzer")

    # User input for URLs
    url1 = st.text_input("Enter the first URL:")
    url2 = st.text_input("Enter the second URL:")

    # Add custom CSS for the button
    st.markdown(
        """
        <style>
        .check-button {
            background-color: #007bff; /* Blue color */
            color: white;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 10px 2px;
            cursor: pointer;
            border: none;
            border-radius: 5px;
        }
        .check-button:hover {
            background-color: #0056b3; /* Darker blue */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Button with custom styling
    if st.button("Check Cannibalization", key="check_cannibalization"):
        if url1 and url2:
            try:
                # Fetch and process content from both URLs
                content1 = fetch_content(url1)
                content2 = fetch_content(url2)
                
                # Extract keywords
                keywords1 = extract_keywords(content1)
                keywords2 = extract_keywords(content2)
                
                # Analyze cannibalization
                common_keywords = analyze_cannibalization(keywords1, keywords2)
                
                # Display download button with custom CSS
                if common_keywords:
                    df = pd.DataFrame(common_keywords)
                    
                    # Create a custom HTML button for downloading
                    csv_data = df.to_csv(index=False).encode().decode('utf-8').replace('\n', '%0A').replace('\r', '%0D')
                    
                    st.markdown(
                        f"""
                        <style>
                        .container {{
                            text-align: center;
                            margin: 20px 0;
                        }}
                        .download-button {{
                            background-color: orange;
                            color: white;
                            padding: 10px 20px;
                            text-align: center;
                            text-decoration: none;
                            display: inline-block;
                            font-size: 16px;
                            margin: 10px 2px;
                            cursor: pointer;
                            border: none;
                            border-radius: 5px;
                        }}
                        </style>
                        <div class="container">
                            <a href="data:file/csv;base64,{csv_data}" download="results.csv" class="download-button">Download Results</a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Display the table
                    st.dataframe(df)
                    
                else:
                    st.write("No common keywords found.")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter both URLs.")

# Placeholder functions for demonstration
def fetch_content(url):
    # Simulated content fetch (replace with actual implementation)
    return "Sample content from " + url

def extract_keywords(content):
    # Simulated keyword extraction (replace with actual implementation)
    return ["keyword1", "keyword2"]

def analyze_cannibalization(keywords1, keywords2):
    # Simulated cannibalization analysis (replace with actual implementation)
    return [kw for kw in keywords1 if kw in keywords2]

if __name__ == "__main__":
    main()
