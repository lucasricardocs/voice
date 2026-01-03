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

# Vozes pt-BR disponíveis (baseadas em edge-tts)
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

velocidade = st.sidebar.slider("Velocidade da leitura:", -40, 40, 0, step=5)
RATE = f"{velocidade}%" if velocidade >= 0 else f"{velocidade}%"

st.sidebar.markdown("---")
st.sidebar.markdown("**Feito com ❤️ por IA**")

# --- Upload PDF ---
col1, col2 = st.columns([1, 3])

with col1:
    arquivo_pdf = st.file_uploader("📁 Faça upload do PDF", type=["pdf"])

with col2:
    st.info("**Como usar:**\n1. Faça upload do PDF\n2. Configure voz e velocidade\n3. Clique em 'Gerar áudio'\n4. Escute com destaque de texto!")

# --- Processar PDF ---
texto_pdf = ""
if arquivo_pdf is not None:
    reader = PyPDF2.PdfReader(io.BytesIO(arquivo_pdf.read()))
    for pagina in reader.pages:
        texto_pdf += pagina.extract_text() + "\n"
    
    st.success(f"✅ PDF carregado! **{len(texto_pdf.split())} palavras**")

# --- Gerar áudio ---
audio_bytes = None
if st.button("🔊 Gerar áudio", type="primary", use_container_width=True) and texto_pdf.strip():
    with st.spinner("🎵 Gerando áudio com voz neural..."):
        try:
            async def gerar_audio(texto):
                communicate = edge_tts.Communicate(texto, VOICE, rate=RATE)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    await communicate.save(fp.name)
                    return fp.name
            
            audio_path = asyncio.run(gerar_audio(texto_pdf))
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            os.remove(audio_path)
            st.success("✅ Áudio gerado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao gerar áudio: {str(e)}")

# --- Player de áudio ---
if audio_bytes:
    st.markdown("### 🎧 Player de áudio")
    st.audio(audio_bytes, format="audio/mp3")

# --- Destaque de texto ---
if texto_pdf:
    st.markdown("### 📄 Texto com destaque em tempo real")
    
    # Parâmetros para velocidade do destaque
    base_wpm = 160
    wpm = base_wpm * (1 + velocidade/100.0)
    ms_por_palavra = int(60000 / wpm)
    
    st.markdown(f"""
    <div id="texto-original" style="display:none;">{texto_pdf.replace('\n', ' ').strip()}</div>
    <div id="texto-destacado" style="padding: 1.5rem; border: 2px solid #4CAF50; border-radius: 12px; max-height: 400px; overflow-y: auto; font-size: 1.2rem; line-height: 1.8; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);"></div>
    
    <button onclick="startHighlight()" style="margin-top: 1rem; padding: 12px 24px; background: #4CAF50; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer;">▶️ Iniciar destaque de texto</button>
    
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
        const html = `{{before}} <span style="background: linear-gradient(90deg, #FFD700, #FFA500); padding: 2px 4px; border-radius: 4px; font-weight: bold;">{{current}}</span> {{after}}`;
        document.getElementById("texto-destacado").innerHTML = html;
        index += 1;
    }}
    
    function startHighlight() {{
        if (intervalId) clearInterval(intervalId);
        index = 0;
        updateHighlight();
        intervalId = setInterval(updateHighlight, msPerWord);
    }}
    </script>
    """, unsafe_allow_html=True)
