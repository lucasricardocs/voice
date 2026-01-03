import streamlit as st
import PyPDF2
import asyncio
import edge_tts
import io

# ================================================
# CONFIGURAÇÃO DE TEMA E PÁGINA
# ================================================
st.set_page_config(
    page_title="Pro Reader AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_ui_theme():
    st.markdown("""
    <style>
    /* Global Dark Theme */
    .stApp {
        background-color: #0e1117 !important;
        color: #e0e0e0 !important;
    }
    
    /* Navbar Custom */
    .nav-container {
        background: #161b22;
        padding: 1.5rem;
        border-bottom: 2px solid #30363d;
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Cards Estilizados */
    .reader-card {
        background: #161b22;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* Texto de Leitura */
    #reading-area {
        background: #1c2128;
        border: 1px solid #444c56;
        border-radius: 10px;
        padding: 30px;
        font-size: 1.3rem !important;
        line-height: 1.8;
        color: #adbac7;
        min-height: 300px;
        max-height: 500px;
        overflow-y: auto;
        font-family: 'Inter', sans-serif;
    }
    
    /* Highlight Style (Amarelo Natural Reader) */
    .word-highlight {
        background-color: #f2cc60;
        color: #1c2128;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 700;
        transition: all 0.1s ease;
    }
    
    /* Botões */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #238636 !important;
        border: none !important;
        font-weight: bold !important;
    }
    
    /* Inputs */
    .stTextArea textarea {
        background-color: #0d1117 !important;
        color: #adbac7 !important;
        border: 1px solid #30363d !important;
    }
    
    h1, h2, h3 { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

inject_ui_theme()

# ================================================
# CABEÇALHO
# ================================================
st.markdown("""
<div class="nav-container">
    <h1 style='margin:0;'>🎙️ Pro Reader AI</h1>
    <p style='color: #8b949e;'>Experiência de leitura premium com vozes neurais</p>
</div>
""", unsafe_allow_html=True)

# ================================================
# BARRA LATERAL (CONFIGS)
# ================================================
with st.sidebar:
    st.header("⚙️ Configurações de Voz")
    genero = st.radio("Voz", ["Feminina", "Masculina"])
    
    vozes_db = {
        "Feminina": {"Francisca (Natural)": "pt-BR-FranciscaNeural", "Thalita (Suave)": "pt-BR-ThalitaNeural"},
        "Masculina": {"Antônio (Claro)": "pt-BR-AntonioNeural", "Arnaldo (Profundo)": "pt-BR-ArnaldoNeural"}
    }
    
    voz_selecionada = st.selectbox("Selecione a Voz", list(vozes_db[genero].keys()))
    VOICE_ID = vozes_db[genero][voz_selecionada]
    
    # Velocidade de 1.0x a 2.0x
    speed_option = st.select_slider("Velocidade da Leitura", options=["1.0x", "1.25x", "1.5x", "1.75x", "2.0x"])
    
    # Mapeamento para o motor TTS
    rate_map = {"1.0x": "+0%", "1.25x": "+25%", "1.5x": "+50%", "1.75x": "+75%", "2.0x": "+100%"}
    TTS_RATE = rate_map[speed_option]

# ================================================
# ÁREA PRINCIPAL
# ================================================
col_main, col_spacer = st.columns([1, 0.01]) # Centralizar conteúdo

with col_main:
    # Upload e Input
    with st.expander("📥 Importar Texto ou PDF", expanded=True):
        input_type = st.tabs(["📄 PDF", "✏️ Texto Livre"])
        input_text = ""
        
        with input_type[0]:
            pdf_file = st.file_uploader("Arraste seu PDF aqui", type=["pdf"])
            if pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                input_text = " ".join([p.extract_text() for p in pdf_reader.pages])
                
        with input_type[1]:
            input_text = st.text_area("Cole seu texto:", height=150, value=input_text)

    if input_text:
        # Ações de Áudio
        st.markdown("<div class='reader-card'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        
        with c1:
            btn_generate = st.button("🔊 Gerar Áudio")
        
        # Gerenciamento de Áudio
        if btn_generate:
            async def make_audio():
                comm = edge_tts.Communicate(input_text, VOICE_ID, rate=TTS_RATE)
                data = b""
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        data += chunk["data"]
                return data

            with st.spinner("Sintetizando voz neural..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    st.session_state.audio_data = loop.run_until_complete(make_audio())
                    st.success("Áudio pronto!")
                except Exception as e:
                    st.error(f"Erro no motor: {e}")

        if "audio_data" in st.session_state:
            with c2:
                st.audio(st.session_state.audio_data)
            with c3:
                st.download_button("💾 Baixar MP3", st.session_state.audio_data, "leitura.mp3")

        st.markdown("</div>", unsafe_allow_html=True)

        # ÁREA DE LEITURA COM HIGHLIGHT
        st.markdown("### 📖 Modo de Leitura")
        
        # Cálculo de tempo (WPM médio de 160)
        speed_factor = float(speed_option.replace('x',''))
        ms_word = int(60000 / (160 * speed_factor))
        
        # Limpeza para o JS
        js_text = input_text.replace('\n', ' ').replace('"', '\\"').strip()
        
        st.markdown(f"""
        <div id="reading-area">Aguardando início...</div>
        
        <div style="margin-top:20px; display:flex; gap:15px;">
            <button onclick="playReader()" style="flex:2; padding:15px; background:#238636; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">▶ Iniciar Acompanhamento Visual</button>
            <button onclick="stopReader()" style="flex:1; padding:15px; background:#da3633; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">⏹ Parar</button>
        </div>

        <script>
            var text = "{js_text}";
            var words = text.split(/\s+/);
            var i = 0;
            var timer = null;
            var area = document.getElementById('reading-area');

            window.playReader = function() {{
                if(timer) clearInterval(timer);
                i = 0;
                timer = setInterval(function() {{
                    if(i >= words.length) {{
                        clearInterval(timer);
                        return;
                    }}
                    
                    // Mostra o bloco de texto com a palavra atual destacada
                    let html = words.slice(0, i).join(" ") + 
                               " <span class='word-highlight'>" + words[i] + "</span> " + 
                               words.slice(i + 1).join(" ");
                    
                    area.innerHTML = html;
                    
                    // Scroll inteligente: mantém a palavra em destaque visível
                    let currentWord = document.querySelector('.word-highlight');
                    if(currentWord) {{
                        currentWord.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }}
                    
                    i++;
                }}, {ms_word});
            }}

            window.stopReader = function() {{
                clearInterval(timer);
                area.innerHTML = "{js_text}";
            }}
        </script>
        """, unsafe_allow_html=True)

# Footer
st.markdown("<br><p style='text-align:center; color:#444c56;'>Pro Reader v2.0 | IA Neural Speech</p>", unsafe_allow_html=True)
