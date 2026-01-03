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
# CSS CLEAN E PROFISSIONAL - Estilo Natural Reader
# ================================================
def inject_custom_css():
    st.markdown("""
    <style>
    /* ===== RESET E FUNDO ===== */
    * {
        margin: 0;
        padding: 0;
    }
    
    .stApp {
        background-color: #f8f9fa !important;
    }
    
    .main {
        background-color: #f8f9fa !important;
    }
    
    /* ===== NAVBAR FIXA ===== */
    .navbar {
        position: sticky;
        top: 0;
        background: white;
        border-bottom: 1px solid #e0e0e0;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        z-index: 100;
    }
    
    .navbar h1 {
        color: #1a73e8 !important;
        font-size: 2rem !important;
        margin: 0 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }
    
    .navbar p {
        color: #5f6368 !important;
        font-size: 0.95rem !important;
        margin: 0.5rem 0 0 0 !important;
    }
    
    /* ===== CONTAINERS ===== */
    .card {
        background: white;
        border-radius: 12px;
        border: 1px solid #e8eaed;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        border-color: #dadce0;
    }
    
    /* ===== TÍTULOS ===== */
    h1, h2, h3, h4, h5, h6 {
        color: #202124 !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        letter-spacing: -0.3px !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 0.75rem !important;
    }
    
    h3 {
        font-size: 1.2rem !important;
        color: #202124 !important;
    }
    
    /* ===== TEXTOS ===== */
    p, span, label, li {
        color: #5f6368 !important;
        line-height: 1.6;
    }
    
    b, strong {
        color: #202124 !important;
        font-weight: 600;
    }
    
    /* ===== TEXTAREA ESTILIZADA ===== */
    .stTextArea > div > div > textarea {
        background: white !important;
        border: 1px solid #dadce0 !important;
        border-radius: 8px !important;
        color: #202124 !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        padding: 1rem !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #1a73e8 !important;
        box-shadow: 0 1px 6px rgba(26, 115, 232, 0.3) !important;
    }
    
    /* ===== SELECTBOX E RADIO ===== */
    .stSelectbox > div > div > div,
    .stRadio > div > div,
    .stRadio > div > label {
        background: white !important;
        border-radius: 8px !important;
        color: #202124 !important;
    }
    
    .stSelectbox > div > div > div {
        border: 1px solid #dadce0 !important;
        padding: 0.75rem !important;
    }
    
    .stSelectbox > div > div > div:focus-within {
        border-color: #1a73e8 !important;
        box-shadow: 0 1px 6px rgba(26, 115, 232, 0.2) !important;
    }
    
    /* ===== FILE UPLOADER ===== */
    .stFileUploader {
        border-radius: 12px !important;
    }
    
    .stFileUploader > div > div > div > button {
        background: linear-gradient(135deg, #1a73e8 0%, #1967d2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        box-shadow: 0 2px 4px rgba(26, 115, 232, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    
    .stFileUploader > div > div > div > button:hover {
        background: linear-gradient(135deg, #1967d2 0%, #1557c0 100%) !important;
        box-shadow: 0 4px 8px rgba(26, 115, 232, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    /* ===== BOTÕES PRIMÁRIOS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #1a73e8 0%, #1967d2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.85rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        cursor: pointer !important;
        box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1967d2 0%, #1557c0 100%) !important;
        box-shadow: 0 4px 12px rgba(26, 115, 232, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* ===== BOTÕES SECUNDÁRIOS ===== */
    .btn-secondary {
        background: white !important;
        color: #1a73e8 !important;
        border: 1px solid #dadce0 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    
    .btn-secondary:hover {
        background: #f8f9fa !important;
        border-color: #1a73e8 !important;
        box-shadow: 0 2px 6px rgba(26, 115, 232, 0.2) !important;
    }
    
    /* ===== AUDIO PLAYER ===== */
    .stAudio {
        background: white !important;
        border-radius: 12px !important;
        border: 1px solid #e8eaed !important;
        padding: 1.5rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    }
    
    /* ===== ALERTS ===== */
    .stSuccess {
        background: #e6f4ea !important;
        border-left: 4px solid #34a853 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    .stError {
        background: #fce8e6 !important;
        border-left: 4px solid #d33b27 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    .stInfo {
        background: #e8f0fe !important;
        border-left: 4px solid #1a73e8 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    .stWarning {
        background: #fef7e0 !important;
        border-left: 4px solid #f9ab00 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    /* ===== SPINNER ===== */
    .stSpinner {
        text-align: center;
    }
    
    .stSpinner > div {
        border-color: rgba(26, 115, 232, 0.2) !important;
        border-top-color: #1a73e8 !important;
    }
    
    /* ===== TABS ===== */
    .stTabs > div > div > button {
        border-bottom: 3px solid transparent !important;
        color: #5f6368 !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    
    .stTabs > div > div > button[aria-selected="true"] {
        border-bottom-color: #1a73e8 !important;
        color: #1a73e8 !important;
    }
    
    /* ===== DIVIDER ===== */
    hr {
        border: none !important;
        height: 1px !important;
        background: #e8eaed !important;
        margin: 2rem 0 !important;
    }
    
    /* ===== GRID LAYOUT ===== */
    [data-testid="column"] {
        padding: 0 1rem;
    }
    
    [data-testid="column"]:first-child {
        padding-left: 0;
    }
    
    [data-testid="column"]:last-child {
        padding-right: 0;
    }
    
    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 3rem 2rem;
        border-top: 1px solid #e8eaed;
        color: #5f6368 !important;
        font-size: 0.9rem;
        margin-top: 3rem;
    }
    
    .footer a {
        color: #1a73e8 !important;
        text-decoration: none;
    }
    
    .footer a:hover {
        text-decoration: underline;
    }
    
    /* ===== DESTAQUE DE TEXTO ===== */
    #texto-destacado {
        background: white;
        border: 1px solid #e8eaed;
        border-radius: 8px;
        padding: 1.5rem;
        font-size: 1.05rem;
        line-height: 1.8;
        color: #202124;
        min-height: 250px;
        max-height: 400px;
        overflow-y: auto;
    }
    
    #texto-destacado span {
        background: linear-gradient(120deg, #ffd700, #ffed4e);
        color: #333 !important;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* ===== INFO BOX ===== */
    .info-box {
        background: #f1f3f4;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #1a73e8;
    }
    
    .info-box p {
        margin: 0.25rem 0 !important;
        color: #202124 !important;
    }
    
    /* ===== RESPONSIVIDADE ===== */
    @media (max-width: 768px) {
        .navbar {
            padding: 1rem;
        }
        
        .navbar h1 {
            font-size: 1.5rem !important;
        }
        
        .card {
            padding: 1rem;
        }
        
        h2 {
            font-size: 1.3rem !important;
        }
        
        .stButton > button {
            padding: 0.75rem 1.5rem !important;
            font-size: 0.9rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ================================================
# NAVBAR
# ================================================
st.markdown("""
<div class="navbar">
    <h1>🎙️ Natural Reader</h1>
    <p>Converta PDF e Texto em Áudio com Vozes Neurais em Português do Brasil</p>
</div>
""", unsafe_allow_html=True)

# ================================================
# LAYOUT PRINCIPAL
# ================================================
col_left, col_right = st.columns([2, 1], gap="large")

# ===== COLUNA ESQUERDA =====
with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    st.markdown('<h2>📝 Seu Texto ou PDF</h2>', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2 = st.tabs(["✏️ Digitar Texto", "📄 Upload PDF"])
    
    texto_pdf = ""
    num_paginas = 0
    
    with tab1:
        st.markdown('<p style="color: #5f6368; margin-bottom: 0.5rem;"><b>Cole ou digite seu texto:</b></p>', unsafe_allow_html=True)
        texto_pdf = st.text_area(
            "Texto",
            height=350,
            placeholder="Digite seu texto aqui ou cole conteúdo de um artigo, documento, etc...",
            label_visibility="collapsed"
        )
    
    with tab2:
        st.markdown('<p style="color: #5f6368; margin-bottom: 0.5rem;"><b>Selecione um arquivo PDF:</b></p>', unsafe_allow_html=True)
        arquivo_pdf = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
        
        if arquivo_pdf is not None:
            arquivo_pdf.seek(0)
            reader = PyPDF2.PdfReader(io.BytesIO(arquivo_pdf.read()))
            texto_pdf = ""
            for pagina in reader.pages:
                texto_pdf += pagina.extract_text() + "\n"
            
            num_paginas = len(reader.pages)
            num_palavras = len(texto_pdf.split())
            
            st.success(f"✅ PDF carregado com sucesso! **{num_palavras:,}** palavras | **{num_paginas}** páginas")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===== COLUNA DIREITA =====
with col_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    st.markdown('<h2 style="border: none; padding: 0; margin-bottom: 1.5rem;">🎚️ Configurações</h2>', unsafe_allow_html=True)
    
    # Gênero da voz
    st.markdown('<p style="color: #202124; font-weight: 600; margin-bottom: 0.75rem;">👥 Gênero da Voz</p>', unsafe_allow_html=True)
    tipo_voz = st.radio("", ["👨 Masculina", "👩 Feminina"], label_visibility="collapsed")
    
    # Vozes disponíveis
    vozes = {
        "👨 Masculina": {
            "🎤 Antônio": "pt-BR-AntonioNeural",
            "🎤 Arnaldo": "pt-BR-ArnaldoNeural"
        },
        "👩 Feminina": {
            "🎤 Francisca": "pt-BR-FranciscaNeural",
            "🎤 Thalita": "pt-BR-ThalitaNeural",
            "🎤 Vitória": "pt-BR-VitoriaNeural"
        }
    }
    
    # Selectbox de voz
    st.markdown('<p style="color: #202124; font-weight: 600; margin: 1.5rem 0 0.75rem;">🎙️ Voz</p>', unsafe_allow_html=True)
    vozes_disponiveis = vozes[tipo_voz]
    voz_label = st.selectbox("Voz", list(vozes_disponiveis.keys()), label_visibility="collapsed")
    VOICE = vozes_disponiveis[voz_label]
    
    # Velocidade
    st.markdown('<p style="color: #202124; font-weight: 600; margin: 1.5rem 0 0.75rem;">⚡ Velocidade</p>', unsafe_allow_html=True)
    velocidade_x = st.selectbox(
        "Velocidade",
        ["1.0x (normal)", "1.2x (rápida)", "1.5x (muito rápida)", "2.0x (super rápida)"],
        label_visibility="collapsed"
    )
    
    velocidades = {
        "1.0x (normal)": "0%",
        "1.2x (rápida)": "20%",
        "1.5x (muito rápida)": "50%",
        "2.0x (super rápida)": "100%"
    }
    RATE = velocidades[velocidade_x]
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ================================================
# SEÇÃO DE GERAÇÃO E PLAYER
# ================================================
if texto_pdf.strip():
    col_audio1, col_audio2 = st.columns([2, 1], gap="large")
    
    with col_audio1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.markdown('<h2>🔊 Seu Áudio</h2>', unsafe_allow_html=True)
        
        # Session state
        if "audio_bytes" not in st.session_state:
            st.session_state.audio_bytes = None
        
        # Botão para gerar
        col_btn1, col_btn2 = st.columns([3, 1])
        
        with col_btn1:
            btn_generate = st.button(
                "🎵 Gerar Áudio",
                use_container_width=True,
                key="btn_generate"
            )
        
        if btn_generate:
            with st.spinner("🎵 Processando áudio com IA..."):
                try:
                    async def gerar_audio(texto):
                        communicate = edge_tts.Communicate(texto, VOICE, rate=RATE)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                            await communicate.save(fp.name)
                            return fp.name
                    
                    audio_path = asyncio.run(gerar_audio(texto_pdf))
                    with open(audio_path, "rb") as f:
                        st.session_state.audio_bytes = f.read()
                    os.unlink(audio_path)
                    st.success("✅ Áudio gerado com sucesso!")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
                    st.info("💡 Tente com um texto menor ou velocidade diferente")
        
        # Player de áudio
        if st.session_state.audio_bytes:
            st.markdown('<p style="margin-top: 1.5rem; margin-bottom: 0.5rem; color: #202124; font-weight: 600;">Player:</p>', unsafe_allow_html=True)
            st.audio(st.session_state.audio_bytes, format="audio/mp3")
            
            # Download
            st.download_button(
                label="⬇️ Baixar MP3",
                data=st.session_state.audio_bytes,
                file_name="audio_naturalreader.mp3",
                mime="audio/mpeg",
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_audio2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.markdown('<h3 style="border: none; margin-bottom: 1rem;">📊 Resumo</h3>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-box">
            <p><b>Voz:</b> {voz_label.replace('🎤 ', '')}</p>
            <p><b>Velocidade:</b> {velocidade_x}</p>
            <p><b>Palavras:</b> {len(texto_pdf.split()):,}</p>
            <p><b>Caracteres:</b> {len(texto_pdf):,}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ================================================
# SEÇÃO DE DESTAQUE
# ================================================
if texto_pdf.strip():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    st.markdown('<h2>📄 Acompanhe a Leitura com Destaque</h2>', unsafe_allow_html=True)
    
    multiplicadores = {
        "1.0x (normal)": 1.0,
        "1.2x (rápida)": 1.2,
        "1.5x (muito rápida)": 1.5,
        "2.0x (super rápida)": 2.0
    }
    base_wpm = 160
    wpm = base_wpm * multiplicadores[velocidade_x]
    ms_por_palavra = int(60000 / wpm)
    
    texto_limpo = texto_pdf.replace('\n', ' ').strip()
    
    st.markdown(f"""
    <div id="texto-original" style="display:none;">{texto_limpo}</div>
    <div id="texto-destacado">
        <p style="text-align: center; color: #9aa0a6;">Clique em 'Iniciar Destaque' para acompanhar o texto</p>
    </div>
    
    <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 1.5rem;">
        <button class="stButton" onclick="startHighlight()" style="background: linear-gradient(135deg, #1a73e8 0%, #1967d2 100%); color: white; border: none; border-radius: 8px; padding: 0.85rem 2rem; font-weight: 600; cursor: pointer; box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3);">▶️ Iniciar Destaque ({velocidade_x})</button>
        <button class="btn-secondary" onclick="stopHighlight()" style="background: white; color: #1a73e8; border: 1px solid #dadce0; border-radius: 8px; padding: 0.75rem 1.5rem; font-weight: 600; cursor: pointer;">⏹️ Parar</button>
    </div>
    
    <script>
    const rawText = document.getElementById("texto-original").innerText;
    const words = rawText.split(/\\s+/).filter(w => w.length > 0);
    let index = 0;
    let intervalId = null;
    
    const msPerWord = {ms_por_palavra};
    
    function updateHighlight() {{
        if (index >= words.length) {{
            clearInterval(intervalId);
            return;
        }}
        const before = words.slice(0, index).join(" ");
        const current = words[index];
        const after = words.slice(index + 1).join(" ");
        const html = `${{before}} <span>${{current}}</span> ${{after}}`;
        document.getElementById("texto-destacado").innerHTML = html;
        document.getElementById("texto-destacado").scrollTop = document.getElementById("texto-destacado").scrollHeight * 0.3;
        index += 1;
    }}
    
    function startHighlight() {{
        if (intervalId) clearInterval(intervalId);
        index = 0;
        updateHighlight();
        intervalId = setInterval(updateHighlight, msPerWord);
    }}
    
    function stopHighlight() {{
        if (intervalId) {{
            clearInterval(intervalId);
            intervalId = null;
        }}
    }}
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ================================================
# FOOTER
# ================================================
st.markdown("""
<div class="footer">
    <p><b>🎙️ Natural Reader - PDF to Speech</b></p>
    <p>Desenvolvido com Streamlit + Edge-TTS + Python</p>
    <p><b>100% Gratuito • Open Source • Hospedado no Streamlit Cloud</b></p>
    <p style="margin-top: 1rem; font-size: 0.85rem;">Vozes neurais em português do Brasil com qualidade premium</p>
</div>
""", unsafe_allow_html=True)
