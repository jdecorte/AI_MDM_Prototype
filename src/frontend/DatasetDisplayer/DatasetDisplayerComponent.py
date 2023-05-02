import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid

from src.frontend.enums.DialogEnum import DialogEnum
from src.frontend.enums.VarEnum import VarEnum

class DatasetDisplayerComponent: 

    def show(self, dataframe:pd.DataFrame):
        # Toon de dataframe -> NIET EDITEERBAAR
        MIN_HEIGHT = 50
        MAX_HEIGHT = 500
        ROW_HEIGHT = 60

        st.markdown(f"<h4>Loaded dataset: </h4>", unsafe_allow_html=True)
        gb = GridOptionsBuilder.from_dataframe(dataframe)
        gb.configure_side_bar()
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
        gridOptions = gb.build()
        return AgGrid(dataframe, gridOptions=gridOptions, enable_enterprise_modules=True, height=min(MIN_HEIGHT + len(dataframe) * ROW_HEIGHT, MAX_HEIGHT))