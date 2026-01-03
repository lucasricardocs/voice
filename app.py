import streamlit as st
import PyPDF2
import asyncio
import edge_tts
import base64
import json
import re

# ================================================
# CONFIGURAÇÃO DE ALTA PERFORMANCE
# ================================================
st.set_page_config(
    page_title="Leitor Dinâmico AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS CLEAN & DARK MODE
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #f0f2f6; }
    
    /* Container de Texto Otimizado para Leitura */
    #reader-view {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 40px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 1.4rem; /* Fonte grande para leitura fácil */
        line-height: 1.8;
        color: #8b949e;
        height: 600px;
        overflow-y: auto;
        scroll-behavior: smooth;
    }
    
    /* Estilo da Frase (Sentença) */
    .sentence {
        transition: all 0.2s ease;
        padding: 4px 6px;
        border-radius: 6px;
        cursor: pointer;
    }
    
    .sentence:hover {
        background-color: #21262d;
        color: #c9d1d9;
    }
    
    /* O Destaque da Frase Ativa */
    .active-sentence {
        background-color: #1f6feb !important; /* Azul Profissional */
        color: #ffffff !important;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(31, 111, 235, 0.3);
        border-left: 4px solid #58a6ff;
    }
    
    /* Player Fixo */
    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 100;
        background: #0e1117;
        padding-bottom: 1rem;
        border-bottom: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

# ================================================
# LÓGICA DE PROCESSAMENTO INTELIGENTE
# ================================================

def extract_text(pdf_file):
    """Extração rápida de texto"""
    reader = PyPDF2.PdfReader(pdf_file)
    text = []
    for page in reader.pages:
        t = page.extract_text()
        if t: text.append(t)
    # Junta e limpa quebras de linha excessivas para fluidez
    return " ".join(text).replace('\n', ' ')

def map_speed(value_x):
    """Mapeia 1.0x-2.0x para a sintaxe do edge-tts"""
    # 1.0 = +0%, 1.5 = +50%, 2.0 = +100%
    percentage = int((value_x - 1.0) * 100)
    return f"+{percentage}%"

async def generate_audio_stream(text, voice, rate_str):
    """Gera áudio e calcula timestamps de frases em uma única passada"""
    communicate = edge_tts.Communicate(text, voice, rate=rate_str)
    
    audio_data = b""
    sentence_timestamps = []
    
    current_sentence_words = []
    sentence_start = 0.0
    idx = 0
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
            
        elif chunk["type"] == "WordBoundary":
            # Dados da palavra atual
            start = chunk["offset"] / 10_000_000
            end = (chunk["offset"] + chunk["duration"]) / 10_000_000
            word = chunk["text"]
            
            # Se for a primeira palavra da frase, marca o início
            if not current_sentence_words:
                sentence_start = start
            
            current_sentence_words.append(word)
            
            # Verifica se a palavra tem pontuação final de frase
            if re.search(r'[.!?։::]+$', word):
                sentence_timestamps.append({
                    "index": idx,
                    "start": sentence_start,
                    "end": end, # O fim da frase é o fim desta palavra
                    "text": " ".join(current_sentence_words)
                })
                current_sentence_words = [] # Reseta para próxima frase
                idx += 1
    
    # Adiciona o que sobrou (caso o texto não termine em ponto)
    if current_sentence_words:
        sentence_timestamps.append({
            "index": idx,
            "start": sentence_start,
            "end": end,
            "text": " ".join(current_sentence_words)
        })
        
    return audio_data, sentence_timestamps

# ================================================
# INTERFACE
# ================================================

# Sidebar Compacta
with st.sidebar:
    st.title("⚡ Configuração")
    uploaded_file = st.file_uploader("Arquivo PDF", type="pdf")
    
    # Seleção de Voz
    voz_nome = st.selectbox("Voz", ["Feminina (Francisca)", "Masculina (Antônio)"])
    voice_id = "pt-BR-FranciscaNeural" if "Feminina" in voz_nome else "pt-BR-AntonioNeural"
    
    # Slider de 1.0x a 2.0x (Numérico para precisão)
    speed_val = st.slider("Velocidade", min_value=1.0, max_value=2.0, value=1.0, step=0.1, format="%0.1fx")
    rate_str = map_speed(speed_val)

# Corpo Principal
if not uploaded_file:
    st.info("👋 Para começar, arraste seu PDF para a barra lateral.")
else:
    # Estado da Aplicação
    if "app_state" not in st.session_state:
        st.session_state.app_state = {"ready": False}

    # Botão de Ação
    if st.button("🚀 Processar Leitura Rápida", type="primary", use_container_width=True):
        full_text = extract_text(uploaded_file)
        
        if len(full_text.strip()) == 0:
            st.error("O PDF parece estar vazio ou é uma imagem.")
        else:
            with st.spinner("⚡ Sintetizando áudio em alta velocidade..."):
                try:
                    # Execução do Loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    audio_bytes, sentences = loop.run_until_complete(
                        generate_audio_stream(full_text, voice_id, rate_str)
                    )
                    
                    # Salva no Estado
                    st.session_state.app_state = {
                        "ready": True,
                        "audio_b64": base64.b64encode(audio_bytes).decode(),
                        "data": json.dumps(sentences),
                        # Constrói o HTML das frases pré-processadas
                        "html": " ".join([f"<span id='s-{s['index']}' class='sentence'>{s['text']}</span>" for s in sentences])
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ================================================
    # PLAYER JAVASCRIPT OTIMIZADO (Highlight por Frase)
    # ================================================
    if st.session_state.app_state["ready"]:
        data = st.session_state.app_state
        
        # HTML do Player
        html_content = f"""
        <div class="sticky-header">
            <audio id="player" controls autoplay style="width: 100%; height: 45px;">
                <source src="data:audio/mp3;base64,{data['audio_b64']}" type="audio/mp3">
            </audio>
        </div>
        
        <div id="reader-view">
            {data['html']}
        </div>

        <script>
            const sentences = {data['data']};
            const player = document.getElementById('player');
            const container = document.getElementById('reader-view');
            
            // Variável para evitar buscas desnecessárias
            let lastIndex = -1;

            player.ontimeupdate = function() {{
                const t = player.currentTime;
                
                // Otimização: Só busca se o tempo saiu da frase anterior
                if (lastIndex !== -1 && t >= sentences[lastIndex].start && t <= sentences[lastIndex].end) {{
                    return; // Ainda estamos na mesma frase
                }}
                
                // Busca a nova frase ativa
                const active = sentences.find(s => t >= s.start && t <= s.end);
                
                if (active && active.index !== lastIndex) {{
                    // Remove destaque anterior
                    const prev = document.querySelector('.active-sentence');
                    if (prev) prev.classList.remove('active-sentence');
                    
                    // Adiciona novo destaque
                    const el = document.getElementById('s-' + active.index);
                    if (el) {{
                        el.classList.add('active-sentence');
                        
                        // Scroll suave para manter a frase no centro
                        el.scrollIntoView({{
                            behavior: 'smooth',
                            block: 'center'
                        }});
                    }}
                    lastIndex = active.index;
                }}
            }};
            
            // Clique na frase para pular o áudio
            container.addEventListener('click', (e) => {{
                if (e.target.classList.contains('sentence')) {{
                    const id = parseInt(e.target.id.split('-')[1]);
                    const target = sentences.find(s => s.index === id);
                    if (target) {{
                        player.currentTime = target.start;
                        player.play();
                    }}
                }}
            }});
        </script>
        """
        
        st.components.v1.html(html_content, height=700, scrolling=False)
