import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

class DataExtractorInitPage:
    def __init__(self, canvas, handler):
        self.canvas = canvas
        self.handler = handler
    
    def show(self):

        count = st_autorefresh(interval=2000, limit=5, key="fizzbuzzcounter")
        # The function returns a counter for number of refreshes. This allows the
        # ability to make special requests at different intervals based on the count
        if count == 0:
            st.write("Count is zero")
        elif count % 2 == 0:
            st.write(f"Count: {count} is even")
        else:
            st.write(f"Count: {count}" + " is odd")

    