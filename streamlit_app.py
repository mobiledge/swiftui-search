import streamlit as st
import requests
import json
import pandas as pd

# Configure the page with a clean, professional layout
st.set_page_config(
    page_title="SwiftUI Documentation Explorer",
    page_icon="📚",
    layout="centered"
)

# Create a consistent base URL for the documentation
BASE_DOC_URL = "https://developer.apple.com"

# Add title and description to help users understand the purpose of the app
st.title("SwiftUI Documentation Explorer")
st.markdown("""
This application provides easy access to SwiftUI documentation. You can search through all available
SwiftUI components and get direct links to their official documentation. The tool helps developers
quickly find and access the information they need about SwiftUI views and components.
""")


@st.cache_data
def fetch_github_data():
    """
    Fetches the SwiftUI documentation links from GitHub and processes them into a usable format.
    The function includes caching to optimize performance and reduce API calls.

    Returns:
        pandas.DataFrame: A processed dataframe containing the documentation links and titles
        None: If there was an error fetching or processing the data
    """
    # Convert the blob URL to raw content URL for direct access
    url = "https://raw.githubusercontent.com/mobiledge/mobiledge.github.io/master/search/swiftui-views.json"

    try:
        # Fetch the data from GitHub
        response = requests.get(url)
        response.raise_for_status()

        # Parse the JSON data
        data = response.json()

        # Extract the links array and convert to DataFrame
        if 'links' in data:
            df = pd.DataFrame(data['links'])

            # Create full documentation URLs by combining with base URL
            df['full_url'] = df['url'].apply(lambda x: f"{BASE_DOC_URL}{x}")

            return df
        else:
            st.error("The data doesn't contain the expected 'links' structure")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch data: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON data: {str(e)}")
        return None


# Fetch the documentation data
data_df = fetch_github_data()

if data_df is not None:
    # Create the search box in the main content area
    search_term = st.text_input(
        "Search Components",
        placeholder="Enter component name...",
        help="Search is case-insensitive and matches partial names",
        key="search_input"  # Adding a key for state management
    ).lower()

    # Filter the data based on search term
    # The filtering happens automatically with every keystroke due to Streamlit's reactive nature
    if search_term:
        filtered_df = data_df[data_df['title'].str.lower(
        ).str.contains(search_term)]
        st.markdown(f"Found **{len(filtered_df)
                               }** components matching '*{search_term}*'")
    else:
        filtered_df = data_df

    # Create a container for search results to maintain consistent spacing
    results_container = st.container()

    with results_container:
        for _, row in filtered_df.iterrows():
            st.markdown(f"[{row['title']}]({row['full_url']})")

        # Add helpful information when no results are found
        if filtered_df.empty:
            st.warning(
                "No components found matching your search criteria. "
                "Try using a different search term or clearing the search box."
            )

# Add footer with attribution and helpful links
st.markdown("---")
st.markdown("""
**Resources:**
- Data source: [mobiledge/mobiledge.github.io](https://github.com/mobiledge/mobiledge.github.io)
- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui)
""")
