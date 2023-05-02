import pandas as pd
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from src.backend.ExternalResources.ZeroER.data_loading_helper.data_loader import load_data
from src.backend.ExternalResources.ZeroER.data_loading_helper.feature_extraction import *
from src.backend.ExternalResources.ZeroER.utils import run_zeroer
from src.backend.ExternalResources.ZeroER.blocking_functions import *
from os.path import join
from streamlit.components.v1 import html
from src.frontend import Helper

from src.frontend.enums.DialogEnum import DialogEnum
from src.frontend.enums.VarEnum import VarEnum

# PARAMETERS
data_path = "datasets"
LR_dup_free = False
run_trans = False
LR_identical = True
dataset_name = "fodors_zagats_single"
# dataset_name = "TVs"
dataset_path = join(data_path,dataset_name)
blocking_func = blocking_functions_mapping[dataset_name]

def editSuggestie(suggestieContainer, df):
    suggestieContainer.empty()
    suggestieInnerContainer = suggestieContainer.container()
    with suggestieInnerContainer:
        for col in df:
            title = st.text_input(col, df[col].item(), key='editDeDupe'+col)
            
# Aangepaste code vanuit ZEROER.py
def dedupe(colsToKeep):
    try:
        candset_features_df = pd.read_csv(join(dataset_path,"candset_features_df.csv"), index_col=0)
        candset_features_df.reset_index(drop=True,inplace=True)
        if run_trans==True:
            id_df = candset_features_df[["ltable_id","rtable_id"]]
            id_df.reset_index(drop=True,inplace=True)
            if LR_dup_free==False and LR_identical==False:
                candset_features_df_l = pd.read_csv(join(dataset_path,"candset_features_df_l.csv"), index_col=0)
                candset_features_df_l.reset_index(drop=True,inplace=True)
                candset_features_df_r = pd.read_csv(join(dataset_path,"candset_features_df_r.csv"), index_col=0)
                candset_features_df_r.reset_index(drop=True,inplace=True)
                id_df_l = candset_features_df_l[["ltable_id","rtable_id"]]
                id_df_l.reset_index(drop=True,inplace=True)
                id_df_r = candset_features_df_r[["ltable_id","rtable_id"]]
                id_df_r.reset_index(drop=True,inplace=True)
        print(
            "Features already generated, reading from file: " + dataset_path + "/candset_features_df.csv")

    except FileNotFoundError:
        print("Generating features and storing in: " + dataset_path + "/candset_features_df.csv")

        f = open(join(dataset_path, 'metadata.txt'), "r")
        LEFT_FILE = join(dataset_path, f.readline().strip())
        if LR_identical:
            RIGHT_FILE = LEFT_FILE
        else:
            RIGHT_FILE = join(dataset_path, f.readline().strip())
        DUPLICATE_TUPLES = join(dataset_path, f.readline().strip())
        f.close()
        if run_trans==True and LR_dup_free==False and LR_identical==False:
            ltable_df, rtable_df, duplicates_df, candset_df,candset_df_l,candset_df_r = load_data(LEFT_FILE, RIGHT_FILE, DUPLICATE_TUPLES,
                                                                                              blocking_func,
                                                                                              include_self_join=True)
        else:
            ltable_df, rtable_df, duplicates_df, candset_df = load_data(LEFT_FILE, RIGHT_FILE, DUPLICATE_TUPLES,
                                                                                              blocking_func,
                                                                                              include_self_join=False)
            if LR_identical:
                print("removing self matches")
                candset_df = candset_df.loc[candset_df.ltable_id!=candset_df.rtable_id,:]
                candset_df.reset_index(inplace=True,drop=True)
                candset_df['_id'] = candset_df.index
        if duplicates_df is None:
            duplicates_df = pd.DataFrame(columns=["ltable_id", "rtable_id"])

        # EXTRA TOEGEVOEGDE CODE:
        # candset_df = candset_df[colsToKeep]

        candset_features_df = gather_features_and_labels(ltable_df, rtable_df, duplicates_df, candset_df)
        candset_features_df.to_csv(join(dataset_path,"candset_features_df.csv"))
        id_df = candset_df[["ltable_id", "rtable_id"]]

        if run_trans == True and LR_dup_free == False and LR_identical==False:
            duplicates_df_r = pd.DataFrame()
            duplicates_df_r['l_id'] = rtable_df["id"]
            duplicates_df_r['r_id'] = rtable_df["id"]
            candset_features_df_r = gather_features_and_labels(rtable_df, rtable_df, duplicates_df_r, candset_df_r)
            candset_features_df_r.to_csv(join(dataset_path,"candset_features_df_r.csv"))


            duplicates_df_l = pd.DataFrame()
            duplicates_df_l['l_id'] = ltable_df["id"]
            duplicates_df_l['r_id'] = ltable_df["id"]
            candset_features_df_l = gather_features_and_labels(ltable_df, ltable_df, duplicates_df_l, candset_df_l)
            candset_features_df_l.to_csv(join(dataset_path,"candset_features_df_l.csv"))

            id_df_l = candset_df_l[["ltable_id","rtable_id"]]
            id_df_r = candset_df_r[["ltable_id","rtable_id"]]
            id_df_l.to_csv(join(dataset_path,"id_tuple_df_l.csv"))
            id_df_r.to_csv(join(dataset_path,"id_tuple_df_r.csv"))

    similarity_features_df = gather_similarity_features(candset_features_df)
    similarity_features_lr = (None,None)
    id_dfs = (None, None, None)
    if run_trans == True:
        id_dfs = (id_df, None, None)
        if LR_dup_free == False and LR_identical==False:
            similarity_features_df_l = gather_similarity_features(candset_features_df_l)
            similarity_features_df_r = gather_similarity_features(candset_features_df_r)
            features = set(similarity_features_df.columns)
            features = features.intersection(set(similarity_features_df_l.columns))
            features = features.intersection(set(similarity_features_df_r.columns))
            features = sorted(list(features))
            similarity_features_df = similarity_features_df[features]
            similarity_features_df_l = similarity_features_df_l[features]
            similarity_features_df_r = similarity_features_df_r[features]
            similarity_features_lr = (similarity_features_df_l,similarity_features_df_r)
            id_dfs = (id_df, id_df_l, id_df_r)

    true_labels = candset_features_df.gold.values
    if np.sum(true_labels)==0:
        true_labels = None
    y_pred = run_zeroer(similarity_features_df, similarity_features_lr,id_dfs,
                        true_labels ,LR_dup_free,LR_identical,run_trans)
    pred_df = candset_features_df[["ltable_id","rtable_id"]]
    pred_df['pred'] = y_pred    
    pred_df.to_csv(join(dataset_path,"pred.csv"))
    return pred_df

def initOneDedup(canvas, dataframe):
    with canvas.container():
        outerContainer = st.container()  
        with outerContainer: 
            st.title("De-duplicatie van één dataset")
            st.markdown(f"<h4>Ingeladen Dataset: </h4>", unsafe_allow_html=True)

            # uploaded_file = st.file_uploader("Kies een .csv bestand")
            # if uploaded_file is not None:
            todisplaydf = dataframe.drop('class', axis=1)
            # todisplaydf = dataframe
            gb = GridOptionsBuilder.from_dataframe(todisplaydf)
            
            gb.configure_side_bar()
            gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
            gridOptions = gb.build()
            grid_response = AgGrid(todisplaydf, gridOptions=gridOptions, enable_enterprise_modules=True)

            todisplaydf = grid_response['data']

            # Kolom keuze om rekening mee te houden
            # options = st.multiselect(
            #  'Met welke colommen dient er rekening te worden gehouden:',
            #  list(dataframe.columns),
            #  list(dataframe.columns))

            # Set up parameters voor De-duplicatie
            with st.form("dedupe_form"):
                certainty = 0
                colsToKeep = st.multiselect(
                'Met welke colommen dient er rekening te worden gehouden:',
                list(todisplaydf.columns),
                list(todisplaydf.columns))

                # MOET WEG!!
                # colsToKeep = dataframe.columns

                col1, col2, col3 = st.columns([7,2,2])
                with col1:
                    # certainty = st.slider('U wilt een zekerheid van (Percentage): ', 0, 100, 90)
                   afhankelijkheid = st.select_slider('Tolerantie in duplicaatdetectie:', options= [ "Veel Tolerantie", "Gemiddeld",  "Geen Tolerantie"], value="Gemiddeld")

                with col2:
                    st.write("")
                    # genre = st.radio(
                    #     "Aanpassen van duplicaten",
                    #     ('Automatisch', 'Manueel'), index=1)

                with col3:
                    if st.form_submit_button('De-dupliceer'):
                        with st.spinner('Even geduld a.u.b. ...'):
                            preddf = dedupe(colsToKeep)
                        st.success('Analyseren van data voltooid!')

                        st.session_state["dubbelsDF"] = preddf
                        st.session_state["dubbelsCertainty"] = certainty
                        st.session_state[VarEnum.gb_CURRENT_STATE.value] = "iterateDubbels"



# Dit moet gecached worden
def createDeDupComparison(dataframe, lid, rid):
    df2 = dataframe[(dataframe['id'] == lid) | (dataframe['id'] == rid) ]
    df2 = df2.set_index(df2.columns[0])
    return df2




def createDubbelsMap(preddf, dataframe):
    dictVanReedsBezochteRows = {}
    listVanDFs = []
    counter = 0
    for index, row in preddf.iterrows(): 
        lid = row["ltable_id"]
        rid = row["rtable_id"]
        flag = False

        if lid in dictVanReedsBezochteRows:
            if rid not in dictVanReedsBezochteRows[lid]:
                dictVanReedsBezochteRows[lid].add(rid)
                flag = True
        else:
            dictVanReedsBezochteRows[lid] = set([rid])
            flag = True

        if rid in dictVanReedsBezochteRows:
            if lid not in dictVanReedsBezochteRows[rid]:
                dictVanReedsBezochteRows[rid].add(lid)
                flag = True
        else:
            dictVanReedsBezochteRows[rid] = set([lid])
            flag = True

        if flag:
            df2 = createDeDupComparison(dataframe, lid, rid)
            df2 = df2.drop('class', axis=1)
            # Replacement toevoegen
            df2 = df2.append(df2.head(1))
            listVanDFs.append(df2)
            st.session_state["ListActiveMergeDuplicates"][counter] = True
            
            # if st.session_state["EDITINIT"] == False:
            #     st.session_state["ListEditDuplicates"][counter] = False
            counter += 1

    # st.session_state["EDITINIT"] == True
    return listVanDFs


def iterateDubbels(dataframe, preddf, certainty, canvas):
    preddf
    with canvas.container():
        dictVanReedsBezochteRows = {}
        preddf = preddf[preddf["pred"]>=(certainty/100)]
        st.markdown(f"""<h2>Overzicht: </h2>""",unsafe_allow_html=True)
        st.write("")
        st.write("")
        dubbelsMap = createDubbelsMap(preddf, dataframe)
        sub_rowstoUse = Helper.createPaginering("page_number_Dedupe", dubbelsMap,10)
        duplicatesContainer = st.container()
        with duplicatesContainer:
            customSpan = rf"""
            <span id="containerDuplicateCardsFinder">
            </span>
            """
            st.markdown(customSpan,unsafe_allow_html=True)
            js = '''<script>
            containerElement = window.parent.document.getElementById("containerDuplicateCardsFinder").parentElement.parentElement.parentElement.parentElement.parentElement
            containerElement.setAttribute('id', 'containerDuplicateCards')
            iframes = window.parent.document.getElementsByTagName("iframe")
            for (var i=0, max=iframes.length; i < max; i++) {
                iframes[i].style.display = "none"
            }
            </script>
            '''
            html(js)
            aantalPredictions = len(preddf)         

            for k,v in enumerate(sub_rowstoUse):
                    singleDuplicateContainer = st.container()
                    with singleDuplicateContainer:
                        dubs = v.iloc[:-1]
                        replacement = v.tail(1)

                        dubs = dubs.style.hide_index().apply(Helper.tagDuplicate, axis=0)
                        replacementStyled = replacement.style.set_properties(**{
                            'font-weight': 'bold',
                        })
                        # .applymap(lambda x: f"color: {'red' if isinstance(x,str) else 'black'}")

                        st.write(dubs)
                        st.write(Helper.makeItalic("Vervang door:"))
                        t = v.tail(1)
                        col1, col2, col3 = st.columns([11,1,2])
                        with col1:
                            suggestieContainer = st.empty()
                            # if st.session_state["ListEditDuplicates"][k + (st.session_state["page_number_Dedupe"]*10)] == False:
                            with suggestieContainer:
                                st.write(replacementStyled)
                            # else:
                            #     editSuggestie(suggestieContainer, replacement, k + (st.session_state["page_number_Dedupe"]*10))

                        with col2:
                            iconToUse = '✏️' 
                            # if st.session_state["ListEditDuplicates"][k + (st.session_state["page_number_Dedupe"]*10)] == False else '✅'
                            if st.button(iconToUse, key="singleDuplicateButton" + str(k)):
                                editSuggestie(suggestieContainer, replacement)
                                # st.session_state["ListEditDuplicates"][k + (st.session_state["page_number_Dedupe"]*10)] = True
                                # st.experimental_rerun()
                                
                        with col3:
                            agree = st.checkbox('Voeg samen', key="singleDuplicateCheckbox" + str(k), value=st.session_state["ListActiveMergeDuplicates"][k + (st.session_state["page_number_Dedupe"]*10)])
                            if not agree:
                                st.session_state["ListActiveMergeDuplicates"][k] = False
                        
                        customSpan = rf"""
                        <span id="duplicateCardsFinder{k}">
                        </span>
                        """
                        st.markdown(customSpan,unsafe_allow_html=True)
                        js = f'''<script>
                        containerElement = window.parent.document.getElementById("duplicateCardsFinder{k}").parentElement.parentElement.parentElement.parentElement.parentElement
                        containerElement.setAttribute('class', 'materialcard')
                        iframes = window.parent.document.getElementsByTagName("iframe")
                        for (var i=0, max=iframes.length; i < max; i++) {{
                            iframes[i].style.display = "none"
                        }}
                        </script>
                        '''
                        html(js)
                        
        col1, col11, col2, col3 = st.columns([2,3,4,2])
        with col1:
            # st.write(Helper.makeItalic("Aantal herkende duplicaten:") + " "+ Helper.makeBold(str(len(dubbelsMap))))
            terugDatasetForm =  st.form("terug_dataset_form")
            trgNaarDataset = terugDatasetForm.form_submit_button("<- Terug naar Dataset")
            if trgNaarDataset:
                st.session_state[VarEnum.gb_CURRENT_STATE.value] = None
                st.experimental_rerun()

        with col2:
            st.write(Helper.makeItalic("Aantal geselecteerd om te vervangen:") +" " + Helper.makeBold(str(len([x for x in st.session_state["ListActiveMergeDuplicates"].values() if x == True] ))+"/"+str(len(dubbelsMap))))

        with col3:

            dfToConvert = dataframe.groupby('class').first()
            dfToConvert = dfToConvert.set_index('id')
            # dfToConvert = dfToConvert.drop('class', axis=1)
            csv = Helper.convert_df(dfToConvert)

            st.download_button(
                label="Download data als CSV",
                data=csv,
                file_name='Deduped_Dataset.csv',
                mime='text/csv',
            )

            
  
    # st.write(st.session_state["ListEditDuplicates"])
    return canvas