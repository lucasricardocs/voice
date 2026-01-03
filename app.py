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
    page_title="Leitor PDF com Voz",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================
# CSS PREMIUM - 200+ LINHAS DE ESTILO ANIMADO
# ================================================
def inject_custom_css():
    st.markdown("""
    <style>
    /* ===== 1. ANIMAÇÕES GLOBAIS ===== */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes gradientText {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    @keyframes float {
        0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255,107,107,0.7); }
        70% { box-shadow: 0 0 0 20px rgba(255,107,107,0); }
        100% { box-shadow: 0 0 0 0 rgba(255,107,107,0); }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 10px rgba(76,175,80,0.5); }
        50% { text-shadow: 0 0 30px rgba(76,175,80,1); }
    }
    
    /* ===== 2. FUNDO ANIMADO E PARTÍCULAS ===== */
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab, #ee7752);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        min-height: 100vh;
    }
    
    .stApp {
        background: transparent !important;
    }
    
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        pointer-events: none;
    }
    
    .particle {
        position: absolute;
        background: rgba(255,255,255,0.1);
        border-radius: 50%;
        animation: float 20s infinite linear;
    }
    
    /* ===== 3. GLASSMORPHISM - CARDS TRANSPARENTES ===== */
    .glass-card {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 25px 45px rgba(0,0,0,0.1) !important;
        padding: 2rem !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        animation: slideInLeft 0.6s ease-out;
    }
    
    .glass-card:hover {
        transform: translateY(-10px) !important;
        box-shadow: 0 35px 60px rgba(0,0,0,0.2) !important;
        background: rgba(255, 255, 255, 0.15) !important;
    }
    
    /* ===== 4. SIDEBAR GLASS ===== */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1) !important;
    }
    
    /* ===== 5. TITULO PRINCIPAL ANIMADO ===== */
    .title-main {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 300% 300%;
        animation: gradientText 3s ease infinite;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: 2px;
        text-shadow: 0 0 30px rgba(255,255,255,0.5);
    }
    
    .subtitle-main {
        text-align: center;
        font-size: 1.3rem;
        color: rgba(255,255,255,0.9);
        margin-bottom: 2rem;
        animation: slideInRight 0.8s ease-out;
    }
    
    /* ===== 6. BOTÕES NEON ANIMADOS ===== */
    .btn-neon {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        background-size: 300% 300%;
        border: 2px solid rgba(255,255,255,0.3);
        border-radius: 50px;
        padding: 1rem 2.5rem;
        font-size: 1.2rem;
        font-weight: bold;
        color: white;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .btn-neon:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        animation: pulse 1.5s infinite;
    }
    
    .btn-neon:active {
        transform: translateY(-1px);
    }
    
    /* ===== 7. INPUTS E SELECTS ===== */
    .stSelectbox > div > div > div,
    .stRadio > div > div {
        background: rgba(255,255,255,0.1) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        color: white !important;
    }
    
    .stFileUploader > div > div > div > button {
        background: linear-gradient(135deg, #4CAF50, #45a049) !important;
        color: white !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader > div > div > div > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 25px rgba(76,175,80,0.4) !important;
    }
    
    /* ===== 8. COLUNAS E LAYOUT ===== */
    [data-testid="column"] {
        animation: slideInLeft 0.6s ease-out;
    }
    
    [data-testid="column"]:nth-child(2) {
        animation: slideInRight 0.6s ease-out;
    }
    
    /* ===== 9. SUCCESS/ERROR/INFO BOXES ===== */
    .stSuccess {
        background: rgba(76,175,80,0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 15px !important;
        border-left: 4px solid #4CAF50 !important;
    }
    
    .stError {
        background: rgba(244,67,54,0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 15px !important;
        border-left: 4px solid #f44336 !important;
    }
    
    .stInfo {
        background: rgba(33,150,243,0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 15px !important;
        border-left: 4px solid #2196F3 !important;
    }
    
    /* ===== 10. PLAYER DE ÁUDIO ===== */
    .stAudio {
        background: rgba(255,255,255,0.1) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    
    /* ===== 11. SEÇÃO DE DESTAQUE ===== */
    .highlight-section {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 2px solid rgba(76,175,80,0.3);
        padding: 2rem;
        margin: 2rem 0;
    }
    
    /* ===== 12. SPINNER CUSTOMIZADO ===== */
    .stSpinner > div {
        border-color: rgba(76,175,80,0.3) !important;
        border-top-color: #4CAF50 !important;
    }
    
    /* ===== 13. DIVIDER ===== */
    hr {
        border: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        margin: 2rem 0;
    }
    
    /* ===== 14. TEXTOS ===== */
    h1, h2, h3, h4, h5, h6 {
        color: rgba(255,255,255,0.95) !important;
    }
    
    p, span, label, li {
        color: rgba(255,255,255,0.85) !important;
    }
    
    /* ===== 15. RESPONSIVIDADE ===== */
    @media (max-width: 768px) {
        .title-main {
            font-size: 2.5rem;
        }
        
        .glass-card {
            padding: 1.5rem !important;
        }
        
        .btn-neon {
            font-size: 1rem;
            padding: 0.75rem 1.5rem;
        }
    }
    </style>
    
    <!-- Partículas flutuantes -->
    <div class="particles" id="particles"></div>
    
    <script>
    // Gera partículas flutuantes
    function createParticles() {
        const particlesContainer = document.getElementById('particles');
        if (!particlesContainer) return;
        
        for(let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.width = particle.style.height = (Math.random() * 4 + 1) + 'px';
            particle.style.animationDelay = Math.random() * 20 + 's';
            particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
            particlesContainer.appendChild(particle);
        }
    }
    createParticles();
    </script>
    """, unsafe_allow_html=True)

# Injeta CSS no início
inject_custom_css()

# ================================================
# CONTEÚDO PRINCIPAL
# ================================================

# Título animado
st.markdown('<h1 class="title-main">🎙️ Leitor PDF Premium</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-main">Transforme seu PDF em áudio com vozes neurais incríveis ✨</p>', unsafe_allow_html=True)
st.markdown("---")

# --- Sidebar com configurações ---
st.sidebar.header("🎤 Configurações de Voz")

# Vozes pt-BR disponíveis (edge-tts)
vozes = {
    "👨 Masculina": {
        "Antônio": "pt-BR-AntonioNeural",
        "Arnaldo": "pt-BR-ArnaldoNeural"
    },
    "👩 Feminina": {
        "Francisca": "pt-BR-FranciscaNeural",
        "Thalita": "pt-BR-ThalitaNeural",
        "Vitória": "pt-BR-VitoriaNeural"
    }
}

tipo_voz = st.sidebar.radio("Gênero da voz:", list(vozes.keys()))
vozes_disponiveis = vozes[tipo_voz]
voz_label = st.sidebar.selectbox("Voz:", list(vozes_disponiveis.keys()))
VOICE = vozes_disponiveis[voz_label]

# Velocidade como multiplicador 1.0x até 2.0x
velocidade_x = st.sidebar.selectbox(
    "Velocidade da leitura:",
    ["1.0x (normal)", "1.2x (rápida)", "1.5x (muito rápida)", "2.0x (super rápida)"],
    index=0
)

# Mapeia para formato edge-tts válido
velocidades = {
    "1.0x (normal)": "0%",
    "1.2x (rápida)": "20%",
    "1.5x (muito rápida)": "50%",
    "2.0x (super rápida)": "100%"
}
RATE = velocidades[velocidade_x]

st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1);">
        <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">
            <b>Feito com ❤️ por IA</b><br>
            <b>100% Gratuito</b><br>
            <b>Código aberto</b>
        </p>
    </div>
""", unsafe_allow_html=True)

# --- Upload PDF e Info ---
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: white; text-align: center;">📁 Upload PDF</h3>', unsafe_allow_html=True)
    arquivo_pdf = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h3 style="color: white;">✨ Como usar</h3>', unsafe_allow_html=True)
    st.markdown("""
    <ol style="color: rgba(255,255,255,0.9);">
        <li><b>Upload do PDF</b> - Selecione seu arquivo</li>
        <li><b>Escolha voz</b> - Masculina ou feminina</li>
        <li><b>Ajuste velocidade</b> - De 1.0x até 2.0x</li>
        <li><b>Clique em Gerar</b> - Aguarde a magia acontecer ✨</li>
        <li><b>Escute e acompanhe</b> - Com destaque de texto</li>
    </ol>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# --- Processar PDF ---
texto_pdf = ""
num_paginas = 0

if arquivo_pdf is not None:
    arquivo_pdf.seek(0)
    reader = PyPDF2.PdfReader(io.BytesIO(arquivo_pdf.read()))
    texto_pdf = ""
    for pagina in reader.pages:
        texto_pdf += pagina.extract_text() + "\n"
    
    num_palavras = len(texto_pdf.split())
    num_paginas = len(reader.pages)
    
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color: white;">✅ PDF Carregado com Sucesso!</h3>
        <p style="color: #4ecdc4; font-size: 1.2rem; margin: 0;">
            📊 <b>{num_palavras:,}</b> palavras | 
            📄 <b>{num_paginas}</b> páginas | 
            📝 Pronto para conversão
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- Botão NEON para gerar áudio ---
if texto_pdf.strip():
    col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 2])
    
    with col_btn2:
        btn_click = st.button(
            "🔮 Gerar Áudio Mágico",
            key="btn_generate",
            use_container_width=True,
            help="Clique para converter o PDF em áudio com IA"
        )
    
    # --- Gerar áudio ---
    audio_bytes = None
    if btn_click:
        with st.spinner(f"🎵 Gerando áudio com {voz_label} ({velocidade_x})..."):
            try:
                async def gerar_audio(texto):
                    communicate = edge_tts.Communicate(texto, VOICE, rate=RATE)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        await communicate.save(fp.name)
                        return fp.name
                
                audio_path = asyncio.run(gerar_audio(texto_pdf))
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()
                os.unlink(audio_path)
                st.balloons()
            except Exception as e:
                st.error(f"❌ Erro ao gerar áudio: **{str(e)}**")
                st.info("💡 Dica: Tente com um PDF menor ou uma velocidade diferente")
    
    # --- Player de áudio (armazenado em session_state) ---
    if "audio_bytes" not in st.session_state:
        st.session_state.audio_bytes = None
    
    if audio_bytes:
        st.session_state.audio_bytes = audio_bytes
    
    if st.session_state.audio_bytes:
        st.markdown("<h3 style='text-align: center; color: white;'>🎧 Seu Áudio</h3>", unsafe_allow_html=True)
        st.audio(st.session_state.audio_bytes, format="audio/mp3")

st.markdown("---")

# --- Destaque de texto ---
if texto_pdf:
    st.markdown("<h3 style='color: white;'>📄 Acompanhe o Texto com Destaque em Tempo Real</h3>", unsafe_allow_html=True)
    
    # Calcula velocidade para destaque
    multiplicadores = {
        "1.0x (normal)": 1.0, 
        "1.2x (rápida)": 1.2, 
        "1.5x (muito rápida)": 1.5, 
        "2.0x (super rápida)": 2.0
    }
    base_wpm = 160
    wpm = base_wpm * multiplicadores[velocidade_x]
    ms_por_palavra = int(60000 / wpm)
    
    # Limpa quebras de linha
    texto_limpo = texto_pdf.replace('\n', ' ').strip()
    
    st.markdown(f"""
    <div id="texto-original" style="display:none;">{texto_limpo}</div>
    <div id="texto-destacado" style="padding: 2rem; border: 2px solid rgba(76,175,80,0.5); border-radius: 20px; max-height: 500px; overflow-y: auto; font-size: 1.3rem; line-height: 1.9; background: linear-gradient(135deg, rgba(245,247,250,0.1), rgba(195,207,226,0.1)); box-shadow: 0 8px 24px rgba(0,0,0,0.2); backdrop-filter: blur(10px);"></div>
    
    <div style="margin-top: 1.5rem; display: flex; gap: 1rem; justify-content: center;">
        <button onclick="startHighlight()" class="btn-neon" style="width: auto;">▶️ Iniciar Destaque ({velocidade_x})</button>
        <button onclick="stopHighlight()" style="width: auto; padding: 1rem 2.5rem; background: linear-gradient(135deg, #f44336, #d32f2f); color: white; border: 2px solid rgba(255,255,255,0.3); border-radius: 50px; font-size: 1.2rem; font-weight: bold; cursor: pointer; box-shadow: 0 10px 30px rgba(0,0,0,0.3); transition: all 0.3s ease;">⏹️ Parar</button>
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
        const html = `{{before}} <span style="background: linear-gradient(90deg, #FFD700, #FFA500); padding: 6px 10px; border-radius: 8px; font-weight: bold; box-shadow: 0 4px 12px rgba(255,165,0,0.4);">{{current}}</span> {{after}}`;
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

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: rgba(255,255,255,0.05); border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); margin-top: 3rem;">
    <p style="color: rgba(255,255,255,0.7); margin: 0; font-size: 0.95rem;">
        🌟 <b>Leitor PDF com Voz Neural</b> 🌟<br>
        Desenvolvido com Streamlit + Edge-TTS + Python<br>
        <b>100% Gratuito • Open Source • Hospedado no Streamlit Cloud</b>
    </p>
</div>
""", unsafe_allow_html=True)
