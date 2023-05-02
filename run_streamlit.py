import pandas as pd
import streamlit as st
import uuid
import hashlib
import uuid
# KEEP NESTED LAYOUT!
import streamlit_nested_layout
from src.frontend.Handler.LocalHandler import LocalHandler
from src.frontend.Handler.RemoteHandler import RemoteHandler
from src.frontend.Router import Router
from src.frontend.StateManager import StateManager
from streamlit_javascript import st_javascript
import json
import config as cfg



import asyncio
import time

import streamlit.components.v1 as components
import websockets
import config as cfg

from src.frontend.enums.DialogEnum import DialogEnum
from src.frontend.enums.VarEnum import VarEnum


def getOrCreateUID():
    if 'uid' not in st.session_state:
        st.session_state['uid'] = ''
    st.session_state['uid'] = st.session_state['uid'] or str(uuid.uuid1())
    cfg.logger.debug('getOrCreateUID: ', st.session_state['uid'])
    return st.session_state['uid']


# Generate a unique uid that gets embedded in components.html for frontend
# Both frontend and server connect to ws using the same uid
# server sends commands like localStorage_get_key, localStorage_set_key, localStorage_clear_key etc. to the WS server,
# which relays the commands to the other connected endpoint (the frontend), and back
def injectWebsocketCode(hostPort, uid):
    code = '<script>function connect() { console.log("in connect uid: ", "' + uid + '"); var ws = new WebSocket("' + hostPort + '/?uid=' + uid + '");' + """
  ws.onopen = function() {
    // subscribe to some channels
    // ws.send(JSON.stringify({ status: 'connected' }));
    console.log("onopen");
  };
  ws.onmessage = function(e) {
    console.log('Message:', e.data);
    var obj = JSON.parse(e.data);
    if (obj.cmd == 'localStorage_get_key') {
        var val = localStorage[obj.key] || '';
        ws.send(JSON.stringify({ status: 'success', val }));
        console.log('returning: ', val);
    } else if (obj.cmd == 'localStorage_set_key') {
        localStorage[obj.key] = obj.val;
        ws.send(JSON.stringify({ status: 'success' }));
        console.log('set: ', obj.key, obj.val);
    }
  };
  ws.onclose = function(e) {
    console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
    setTimeout(function() {
      connect();
    }, 1000);
  };
  ws.onerror = function(err) {
    console.error('Socket encountered error: ', err.message, 'Closing socket');
    ws.close();
  };
}
connect();
</script>
        """
    components.html(code, height=0)
    time.sleep(1)       # Without sleep there are problems
    return WebsocketClient(hostPort, uid)


class WebsocketClient:
    def __init__(self, hostPort, uid):
        self.hostPort = hostPort
        self.uid = uid
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def sendCommand(self, value, waitForResponse=True):

        async def query(future):
            async with websockets.connect(self.hostPort + "/?uid=" + self.uid) as ws:
                await ws.send(value)
                if waitForResponse:
                    response = await ws.recv()
                    print('response: ', response)
                    future.set_result(response)
                else:
                    future.set_result('')

        future1 = asyncio.Future()
        self.loop.run_until_complete(query(future1))
        print('future1.result: ', future1.result())
        return future1.result()

    def getLocalStorageVal(self, key):
        result = self.sendCommand(json.dumps({ 'cmd': 'localStorage_get_key', 'key': key }))
        return json.loads(result)['val']

    def setLocalStorageVal(self, key, val):
        cfg.logger.debug(f"Going to set {key} with {val} in local storage")
        result = self.sendCommand(json.dumps({ 'cmd': 'localStorage_set_key', 'key': key, 'val': val }))
        return result


def _reload_dataframe(uploaded_file):
    t2 = st.session_state[VarEnum.sb_LOADED_DATAFRAME.value]
    t3 = st.session_state[VarEnum.sb_LOADED_DATAFRAME_NAME.value]
    t4 = st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value]
    t5 = st.session_state[VarEnum.gb_SESSION_ID.value]
    seperator_input = st.session_state[VarEnum.sb_LOADED_DATAFRAME_SEPERATOR.value]
    t8 = st.session_state[VarEnum.gb_SESSION_MAP.value]
    t9 = st.session_state[VarEnum.sb_TYPE_HANDLER.value]
    t10 = st.session_state[VarEnum.sb_CURRENT_FUNCTIONALITY.value]
    t11 = st.session_state[VarEnum.sb_CURRENT_PROFILING.value]


    # st.session_state = {}
    for key in st.session_state.keys():
        del st.session_state[key]

    st.session_state[VarEnum.gb_CURRENT_STATE.value] = None
    st.session_state[VarEnum.sb_LOADED_DATAFRAME.value] = pd.read_csv(uploaded_file, delimiter= seperator_input if seperator_input else ',')
    st.session_state[VarEnum.sb_LOADED_DATAFRAME_NAME.value] = uploaded_file.name
    st.session_state[VarEnum.gb_SESSION_ID.value] = t5
    st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value] = f"{st.session_state[VarEnum.gb_SESSION_ID.value]}-{hashlib.md5(st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].to_json().encode('utf-8')).hexdigest()}"
    st.session_state[VarEnum.sb_LOADED_DATAFRAME_SEPERATOR.value] = seperator_input

    st.session_state[VarEnum.gb_SESSION_MAP.value] = t8
    st.session_state[VarEnum.sb_TYPE_HANDLER.value] = t9
    st.session_state[VarEnum.sb_CURRENT_FUNCTIONALITY.value] = t10
    st.session_state[VarEnum.sb_CURRENT_PROFILING.value] = t11

    st.experimental_rerun()

def get_from_local_storage(k):
    v = st_javascript(
        f"JSON.parse(localStorage.getItem('{k}'));"
    )
    return v or {}

def set_to_local_storage(k, v):
    jdata = json.dumps(v)
    st_javascript(
        f"localStorage.setItem('{k}', JSON.stringify({jdata}));"
    )

def main():

    # Pagina Stijl:
    st.set_page_config(page_title=DialogEnum.gb_PAGE_TITLE.value, layout = "wide") 
    with open("src/frontend/Resources/css/style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # StateManagement init
    StateManager.initStateManagement()
    # Cookie Management
    if st.session_state[VarEnum.sb_LOADED_DATAFRAME.value] is None and (st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value] is None):
        if VarEnum.gb_SESSION_ID.value not in st.session_state:
            url = cfg.configuration[VarEnum.cfg_WEBSOCKET_SERVER_URL.value]
            conn = injectWebsocketCode(hostPort=url, uid=getOrCreateUID())
            ret = conn.getLocalStorageVal(key=VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value)
            if not ret:
                temp_id = uuid.uuid4()                
                _ = conn.setLocalStorageVal(key=VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value, val=str(temp_id))
                st.session_state[VarEnum.gb_SESSION_ID.value] = temp_id
            else:
                st.session_state[VarEnum.gb_SESSION_ID.value] = ret

    # Limit session_flask_local_id to 20 characters to avoid problems with
    # very long file names later.
    st.session_state[VarEnum.gb_SESSION_ID.value] = \
        f'{st.session_state[VarEnum.gb_SESSION_ID.value]}'[:20]

    if st.session_state[VarEnum.sb_LOADED_DATAFRAME.value] is not None:
        st.session_state[VarEnum.gb_SESSION_ID_WITH_FILE_HASH.value] = f"{st.session_state[VarEnum.gb_SESSION_ID.value]}-{hashlib.md5(st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].to_json().encode('utf-8')).hexdigest()}"

    if st.session_state[VarEnum.gb_CURRENT_STATE.value] != None:
        st.sidebar.button(DialogEnum.sb_PREVIOUS_STATE_button.value, on_click=StateManager.go_back_to_previous_in_flow, args=(st.session_state[VarEnum.gb_CURRENT_STATE.value],))

    # Sidebar vullen met functionaliteit-mogelijkheden
    st.session_state[VarEnum.sb_CURRENT_FUNCTIONALITY.value] = st.sidebar.selectbox(
        DialogEnum.sb_FUNCTIONALITY_selectbox,
        (DialogEnum.sb_FUNCTIONALITY_option_DATA_PROFILING.value,
        DialogEnum.sb_FUNCTIONALITY_option_DATA_CLEANING.value,
        DialogEnum.sb_FUNCTIONALITY_option_DATA_EXTRACTION.value,
        DialogEnum.sb_FUNCTIONALITY_option_DEDUPLICATION.value,
        DialogEnum.sb_FUNCTIONALITY_option_RULE_LEARNING.value),
        index=3
    )

    # Extra opties voor data profiling
    if st.session_state[VarEnum.sb_CURRENT_FUNCTIONALITY.value] == DialogEnum.sb_FUNCTIONALITY_option_DATA_PROFILING.value:
        profiling_radio = st.sidebar.radio(
            DialogEnum.sb_DATA_PROFILING_radio.value,
            (DialogEnum.sb_DATA_PROFILING_option_dataprep.value, DialogEnum.sb_DATA_PROFILING_option_pandas.value), index=0, horizontal=True
        )
        st.session_state[VarEnum.sb_CURRENT_PROFILING.value] = profiling_radio

    # Sidebar vullen met file-upload knop
    # st.sidebar.markdown(f"<h3>Remote handling van een dataset</h3>", unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader(DialogEnum.sb_UPLOAD_DATASET, key="inputOneDataSet")

    # Sidebar vullen met optionele seperator
    if uploaded_file:
        with st.sidebar.expander(DialogEnum.sb_OPTIONAL_SEPERATOR.value, expanded=False):
            st.write(DialogEnum.sb_OPTIONAL_SEPERATOR_DESCRIPTION.value)
            col_sep_left, col_sep_right = st.columns([1,1])
            with col_sep_left:
                st.session_state[VarEnum.sb_LOADED_DATAFRAME_SEPERATOR.value] = st.text_input(DialogEnum.sb_SEPERATOR.value, value=',')
            with col_sep_right:
                st.write("")
                st.write("")
                flag_reload = st.button(DialogEnum.sb_RELOAD_BUTTON, key="reload_button")
                if flag_reload:
                    _reload_dataframe(uploaded_file)

    # Sidebar vullen met Remote of local functionaliteit
    # type_handler_input = st.sidebar.radio(
    # "Type Handler:",
    # ('Remote', 'Local'), horizontal=True, key=VarEnum.sb_TYPE_HANDLER.value )

    if st.session_state[VarEnum.sb_TYPE_HANDLER.value] == DialogEnum.sb_TYPE_HANDLER_option_REMOTE.value:
        # pass
        # remote_url = st.sidebar.text_input('Remote Location', '127.0.0.1')
        # remote_port = st.sidebar.text_input('Port', '5000')       
        # handler = RemoteHandler(f"http://{remote_url}:{remote_port}")
        handler = RemoteHandler(f"http://{cfg.configuration['remote_url']}:{cfg.configuration['remote_port']}")
    else:
        handler = LocalHandler()
    # handler = RemoteHandler(f"http://127.0.0.1:5000")

    if uploaded_file:
        if st.session_state[VarEnum.sb_LOADED_DATAFRAME_NAME.value] != uploaded_file.name:
            _reload_dataframe(uploaded_file)

        # LOAD IN SESSION_MAP
        st.session_state[VarEnum.gb_SESSION_MAP.value] = handler.get_session_map(dataframe_in_json=st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].to_json())

        # CALCULATE CURRENT SEQ IF NOT ALREADY PRESENT
        if VarEnum.gb_CURRENT_SEQUENCE_NUMBER.value not in st.session_state:
            st.session_state[VarEnum.gb_CURRENT_SEQUENCE_NUMBER.value] = str(max([int(x) for x in st.session_state[VarEnum.gb_SESSION_MAP.value].keys()], default=0)+1)

        # CREATE BUTTONS FROM SESSION_MAP TODO
        button_container =  st.sidebar.expander(label=DialogEnum.sb_PREVIOUS_RESULTS.value, expanded=False)

        for seq,method_dict in st.session_state[VarEnum.gb_SESSION_MAP.value].items():
            button_container.write(seq)
            for method, file_name in method_dict.items():
                button_container.write(method)
                button_container.button("⏪ " + seq + file_name.split("/")[-1],  # file_name.split("\\")[1], 
                                        on_click=StateManager.restore_state,
                                        kwargs={"handler": handler,
                                                "file_path": file_name,
                                                "chosen_seq": seq})
        
        # Toevoegen van download knop:
        # st.sidebar.button('Download huidige dataset')
        st.sidebar.download_button(
                label=DialogEnum.sb_DOWNLOAD_DATASET.value,
                data=st.session_state[VarEnum.sb_LOADED_DATAFRAME.value].to_csv(index=False).encode('utf-8'),
                file_name= f'new_{st.session_state[VarEnum.sb_LOADED_DATAFRAME_NAME.value]}',
                mime='text/csv',
            )
        
        st.sidebar.button('Panic Button', on_click=_reload_dataframe, kwargs=({"uploaded_file": uploaded_file}))

        # Aanmaken van Router object:
        router = Router(handler=handler)
        if st.session_state[VarEnum.sb_CURRENT_FUNCTIONALITY.value] == DialogEnum.sb_FUNCTIONALITY_option_DATA_PROFILING.value:
            if profiling_radio == DialogEnum.sb_DATA_PROFILING_option_pandas.value:
                router.route_pandas_data_profiling()
            if profiling_radio == DialogEnum.sb_DATA_PROFILING_option_dataprep.value:
                router.route_dataprep_data_profiling()
        if st.session_state[VarEnum.sb_CURRENT_FUNCTIONALITY.value] == DialogEnum.sb_FUNCTIONALITY_option_DATA_CLEANING.value:
            router.route_data_cleaning()
        if st.session_state[VarEnum.sb_CURRENT_FUNCTIONALITY.value] == DialogEnum.sb_FUNCTIONALITY_option_DEDUPLICATION.value:
            router.route_dedupe()
        if st.session_state[VarEnum.sb_CURRENT_FUNCTIONALITY.value] == DialogEnum.sb_FUNCTIONALITY_option_RULE_LEARNING.value:
            router.route_rule_learning()
        if st.session_state[VarEnum.sb_CURRENT_FUNCTIONALITY.value] == DialogEnum.sb_FUNCTIONALITY_option_DATA_EXTRACTION.value:
            router.route_data_extraction()

if __name__ == "__main__":
        print("Starting Streamlit")
        main()
