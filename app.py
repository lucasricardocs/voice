import streamlit as st
import PyPDF2
import asyncio
import edge_tts
import tempfile
import os
import io

# ================================================
# CONFIGURAÇÃO INICIAL
# ================================================
st.set_page_config(
    page_title="Natural Reader - PDF to Speech",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================================================
# CSS PROFISSIONAL
# ================================================
def inject_custom_css():
    st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa !important; }
    .navbar {
        background: white;
        border-bottom: 1px solid #e0e0e0;
        padding: 1.5rem;
        margin-bottom: 2rem;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .navbar h1 { color: #1a73e8 !important; margin: 0 !important; }
    .card {
        background: white;
        border-radius: 12px;
        border: 1px solid #e8eaed;
        padding: 2rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    #texto-destacado {
        background: white;
        border: 1px solid #e8eaed;
        border-radius: 8px;
        padding: 1.5rem;
        font-size: 1.1rem;
        line-height: 1.8;
        min-height: 200px;
        max-height: 400px;
        overflow-y: auto;
    }
    .highlight {
        background-color: #ffd700;
        color: black;
        padding: 2px 4px;
        border-radius: 4px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# Navbar
st.markdown('<div class="navbar"><h1>🎙️ Natural Reader</h1><p>Vozes Neurais Premium em Português</p></div>', unsafe_allow_html=True)

# ================================================
# LAYOUT
# ================================================
col_left, col_right = st.columns([2, 1], gap="large")

with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>📝 Conteúdo</h2>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["✏️ Texto", "📄 PDF"])
    
    texto_input = ""
    if "texto_final" not in st.session_state:
        st.session_state.texto_final = ""

    with tab1:
        texto_input = st.text_area("Digite ou cole seu texto:", height=300, placeholder="Era uma vez...")
        
    with tab2:
        arquivo_pdf = st.file_uploader("Escolha um PDF", type=["pdf"])
        if arquivo_pdf:
            reader = PyPDF2.PdfReader(arquivo_pdf)
            texto_pdf = ""
            for page in reader.pages:
                texto_pdf += page.extract_text() + " "
            texto_input = texto_pdf
            st.success("PDF carregado!")

    st.session_state.texto_final = texto_input
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>🎚️ Ajustes</h2>', unsafe_allow_html=True)
    
    genero = st.radio("Gênero", ["Masculina", "Feminina"])
    
    vozes_db = {
        "Masculina": {"Antônio": "pt-BR-AntonioNeural", "Arnaldo": "pt-BR-ArnaldoNeural"},
        "Feminina": {"Francisca": "pt-BR-FranciscaNeural", "Thalita": "pt-BR-ThalitaNeural"}
    }
    
    nome_voz = st.selectbox("Escolha a voz", list(vozes_db[genero].keys()))
    VOICE = vozes_db[genero][nome_voz]
    
    velocidade = st.select_slider("Velocidade", options=["1.0x", "1.2x", "1.5x", "2.0x"])
    
    # Conversão para o formato do edge-tts (ex: +20%, +50%)
    rate_map = {"1.0x": "+0%", "1.2x": "+20%", "1.5x": "+50%", "2.0x": "+100%"}
    RATE = rate_map[velocidade]
    
    st.markdown('</div>', unsafe_allow_html=True)

# ================================================
# PROCESSAMENTO
# ================================================
if st.session_state.texto_final:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col_play, col_info = st.columns([2, 1])
    
    with col_play:
        if st.button("🎵 Gerar Áudio", use_container_width=True):
            async def generate_tts():
                communicate = edge_tts.Communicate(st.session_state.texto_final, VOICE, rate=RATE)
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                return audio_data

            with st.spinner("Sintetizando voz..."):
                try:
                    # Lógica para rodar async dentro do Streamlit
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    audio_bytes = loop.run_until_complete(generate_tts())
                    st.session_state.audio_bytes = audio_bytes
                    st.success("Pronto!")
                except Exception as e:
                    st.error(f"Erro: {e}")

        if "audio_bytes" in st.session_state:
            st.audio(st.session_state.audio_bytes)
            st.download_button("⬇️ Baixar MP3", st.session_state.audio_bytes, "audio.mp3", "audio/mpeg")

    with col_info:
        palavras = len(st.session_state.texto_final.split())
        st.info(f"Estatísticas:\n- {palavras} palavras\n- Velocidade: {velocidade}")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # ================================================
    # DESTAQUE DE TEXTO (HIGHLIGHT)
    # ================================================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>📄 Acompanhamento</h2>', unsafe_allow_html=True)
    
    # Cálculo aproximado de tempo para o JavaScript
    base_wpm = 150 # palavras por minuto média
    v_mult = float(velocidade.replace('x',''))
    ms_per_word = int(60000 / (base_wpm * v_mult))
    
    texto_limpo = st.session_state.texto_final.replace('"', '\\"').replace('\n', ' ')
    
    st.markdown(f"""
        <div id="texto-destacado">Clique em Iniciar para acompanhar...</div>
        <div style="display:flex; gap:10px; margin-top:15px;">
            <button onclick="startReading()" style="padding:10px 20px; background:#1a73e8; color:white; border:none; border-radius:5px; cursor:pointer;">▶ Iniciar Leitura</button>
            <button onclick="stopReading()" style="padding:10px 20px; background:#f1f3f4; color:#1a73e8; border:1px solid #dadce0; border-radius:5px; cursor:pointer;">⏹ Parar</button>
        </div>

        <script>
            var words = "{texto_limpo}".split(/\s+/);
            var index = 0;
            var timer = null;
            var display = document.getElementById('texto-destacado');

            window.startReading = function() {{
                if(timer) clearInterval(timer);
                index = 0;
                timer = setInterval(function() {{
                    if(index >= words.length) {{
                        clearInterval(timer);
                        return;
                    }}
                    let output = words.slice(0, index).join(" ") + 
                                 " <span class='highlight'>" + words[index] + "</span> " + 
                                 words.slice(index + 1).join(" ");
                    display.innerHTML = output;
                    
                    // Auto-scroll
                    display.scrollTop = display.scrollHeight * (index / words.length) - 50;
                    
                    index++;
                }}, {ms_per_word});
            }}

            window.stopReading = function() {{
                clearInterval(timer);
            }}
        </script>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="text-align:center; color:#5f6368; padding:20px;">Feito com Streamlit & Edge-TTS</div>', unsafe_allow_html=True)
