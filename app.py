import streamlit as st
import PyPDF2
import asyncio
import edge_tts
import tempfile
import os
import io

st.set_page_config(
    page_title="Leitor PDF com Voz",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📖 Leitor de PDF com Voz Neural em Português do Brasil")
st.markdown("**Upload seu PDF, escolha voz masculina ou feminina, ajuste velocidade e escute com destaque de texto!**")
st.markdown("---")

# --- Sidebar com configurações ---
st.sidebar.header("🎤 Configurações de Voz")

# Vozes pt-BR disponíveis (edge-tts)
vozes = {
    "Masculina": {
        "Antônio": "pt-BR-AntonioNeural",
        "Arnaldo": "pt-BR-ArnaldoNeural"
    },
    "Feminina": {
        "Francisca": "pt-BR-FranciscaNeural",
        "Thalita": "pt-BR-ThalitaNeural",
        "Vitória": "pt-BR-VitoriaNeural"
    }
}

tipo_voz = st.sidebar.radio("Gênero da voz:", ["Feminina", "Masculina"])
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
st.sidebar.markdown("**Feito com ❤️ por IA** | **100% gratuito**")

# --- Upload PDF ---
col1, col2 = st.columns([1, 3])

with col1:
    arquivo_pdf = st.file_uploader("📁 Faça upload do PDF", type=["pdf"])

with col2:
    st.info("""
    **Como usar:**
    1. Faça upload do PDF
    2. Escolha voz e velocidade
    3. Clique em **'Gerar áudio'**
    4. Escute com destaque de texto!
    """)

# --- Processar PDF ---
texto_pdf = ""
if arquivo_pdf is not None:
    # Reset file pointer
    arquivo_pdf.seek(0)
    reader = PyPDF2.PdfReader(io.BytesIO(arquivo_pdf.read()))
    texto_pdf = ""
    for pagina in reader.pages:
        texto_pdf += pagina.extract_text() + "\n"
    
    num_palavras = len(texto_pdf.split())
    st.success(f"✅ PDF carregado! **{num_palavras:,} palavras** | **{len(reader.pages)} páginas**")

# --- Gerar áudio ---
audio_bytes = None
if st.button("🔊 Gerar áudio", type="primary", use_container_width=True) and texto_pdf.strip():
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
            os.unlink(audio_path)  # limpa arquivo temporário
            st.balloons()  # 🎈 efeito visual
        except Exception as e:
            st.error(f"❌ Erro ao gerar áudio: **{str(e)}**")
            st.info("💡 Tente com texto menor ou velocidade diferente")

# --- Player de áudio ---
if audio_bytes:
    st.markdown("### 🎧 Player de áudio")
    st.audio(audio_bytes, format="audio/mp3")

# --- Destaque de texto ---
if texto_pdf:
    st.markdown("### 📄 Texto com destaque em tempo real")
    
    # Calcula velocidade para destaque baseado na seleção
    multiplicadores = {
        "1.0x (normal)": 1.0, 
        "1.2x (rápida)": 1.2, 
        "1.5x (muito rápida)": 1.5, 
        "2.0x (super rápida)": 2.0
    }
    base_wpm = 160
    wpm = base_wpm * multiplicadores[velocidade_x]
    ms_por_palavra = int(60000 / wpm)
    
    # Limpa quebras de linha para melhor destaque
    texto_limpo = texto_pdf.replace('\n', ' ').strip()
    
    st.markdown(f"""
    <div id="texto-original" style="display:none;">{texto_limpo}</div>
    <div id="texto-destacado" style="padding: 1.5rem; border: 2px solid #4CAF50; border-radius: 12px; max-height: 400px; overflow-y: auto; font-size: 1.2rem; line-height: 1.8; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); box-shadow: 0 4px 12px rgba(0,0,0,0.1);"></div>
    
    <div style="margin-top: 1rem;">
        <button onclick="startHighlight()" style="padding: 12px 24px; background: linear-gradient(135deg, #4CAF50, #45a049); color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; box-shadow: 0 2px 8px rgba(76,175,80,0.3);">▶️ **Iniciar destaque de texto** ({velocidade_x})</button>
        <button onclick="stopHighlight()" style="margin-left: 10px; padding: 12px 24px; background: #f44336; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer;">⏹️ Parar</button>
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
        const html = `{{before}} <span style="background: linear-gradient(90deg, #FFD700, #FFA500); padding: 4px 8px; border-radius: 6px; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">{{current}}</span> {{after}}`;
        document.getElementById("texto-destacado").innerHTML = html;
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
