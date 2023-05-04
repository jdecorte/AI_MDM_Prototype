import streamlit as st
from streamlit_pandas_profiling import st_profile_report


def generate_profile_report(df, minimal):
    pr = df.profile_report(lazy=True, minimal=minimal)
    st.session_state.profile_report = {'data': df, 'pr': pr}

def file_handler(canvas, data_file):
    with canvas.container():
        # seperators = {" ": " ", "pipe (|)": "|", r"tab (\t)": "\t", "comma (,)":",", "semicolon (;)":";"}
        emptyContainer = st.empty() 
        emptyContainerFlag = False
        file_upload_form = emptyContainer.form(key="file_upload")
        with file_upload_form:
            # data_file = st.file_uploader("Upload CSV File", type=['csv'], key="upload")
            # delimiter = seperators[st.selectbox("Select delimiter", seperators.keys(), key="delims")]
            delimiter = ','
            # minimal = st.checkbox('Minimal report', value=True)
            minimal = True
            if file_upload_form.form_submit_button(label='Submit') and data_file:
                emptyContainerFlag = True
                generate_profile_report(data_file, delimiter, minimal)

        if (data_file and delimiter and st.session_state.profile_report):
            data = st.session_state.profile_report['data']
            pr = st.session_state.profile_report['pr']
            # col = st.selectbox("Select column for summary stats", options=['']+list(data.columns))
            # if col != '':
            #     st.write(pd.DataFrame(data[col].unique(), columns=[col]).T)
            st_profile_report(pr)

        if emptyContainerFlag:
            emptyContainer.empty()
        # else:
        #     st.info('Minimaal Rapport of Uitgebreid Rapport')
        #     st.session_state.profile_report = None
