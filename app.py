import streamlit as st
import PyPDF2
import asyncio
import edge_tts
import base64
import json

# ================================================
# CONFIGURAÇÃO GERAL
# ================================================
st.set_page_config(page_title="Leitor Neural Pro", page_icon="🎧", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e6e6e6; }
    #text-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 30px;
        font-family: 'Segoe UI', sans-serif;
        font-size: 1.25rem;
        line-height: 1.8;
        height: 500px;
        overflow-y: auto;
        white-space: pre-wrap;
        color: #b0b8c4;
    }
    .word { cursor: pointer; transition: background 0.1s; padding: 2px 0; border-radius: 3px; }
    .word:hover { background-color: #21262d; }
    .active-word {
        background-color: #f2cc60;
        color: #0d1117;
        font-weight: 700;
        padding: 2px 4px;
        box-shadow: 0 0 10px rgba(242, 204, 96, 0.3);
    }
    /* Estilo da Barra de Progresso Customizada */
    .stProgress > div > div > div > div {
        background-color: #238636;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎧 Leitor Neural com Progresso Real")

# ================================================
# SIDEBAR
# ================================================
with st.sidebar:
    st.header("Configurações")
    uploaded_file = st.file_uploader("📂 Carregar PDF", type="pdf")
    
    voz = st.selectbox("🎙️ Voz", [
        "pt-BR-FranciscaNeural (Feminina)",
        "pt-BR-AntonioNeural (Masculina)",
        "pt-BR-ThalitaNeural (Jovem)",
    ])
    voice_id = voz.split()[0]
    rate_str = st.select_slider("⚡ Velocidade", options=["0%", "+25%", "+50%", "+75%", "+100%"], value="0%")

# ================================================
# LÓGICA PRINCIPAL
# ================================================
def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t: text += t + "\n\n"
    return text

if "processing_done" not in st.session_state:
    st.session_state.processing_done = False

if uploaded_file:
    full_text = extract_text(uploaded_file)
    total_chars = len(full_text)
    
    # Botão de Ação
    if st.button("🚀 Gerar Áudio"):
        progress_bar = st.progress(0, text="Iniciando conexão neural...")
        status_text = st.empty()
        
        async def generate_with_progress():
            communicate = edge_tts.Communicate(full_text, voice_id, rate=rate_str)
            audio_data = b""
            timestamps = []
            word_counter = 0
            
            # Loop assíncrono que recebe pedaços do áudio E metadados
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
                
                elif chunk["type"] == "WordBoundary":
                    # CÁLCULO DO PROGRESSO
                    # text_offset é a posição do caractere atual no texto
                    current_char_pos = chunk["offset"] + chunk["duration"] # Simplificação
                    # O edge-tts fornece 'text_offset' no objeto, vamos usar ele:
                    # Nota: em algumas versões o atributo é acessado diretamente ou via dict
                    # A estrutura segura é usar a posição relativa se disponível ou estimar
                    
                    # O 'chunk' de WordBoundary tem: offset (audio), duration, text_offset, word_length
                    t_offset = chunk.get("text_offset", 0)
                    w_len = chunk.get("word_length", 0)
                    
                    # Atualiza a barra
                    if total_chars > 0:
                        percent = min((t_offset + w_len) / total_chars, 1.0)
                        progress_bar.progress(percent, text=f"Sintetizando: {int(percent*100)}%")

                    timestamps.append({
                        "start": chunk["offset"] / 10_000_000,
                        "end": (chunk["offset"] + chunk["duration"]) / 10_000_000,
                        "word": chunk["text"],
                        "index": word_counter
                    })
                    word_counter += 1
            
            return audio_data, timestamps

        # Execução
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_bytes, time_data = loop.run_until_complete(generate_with_progress())
            
            # Finaliza a barra
            progress_bar.progress(100, text="Concluído! Carregando player...")
            
            # Salva no estado
            st.session_state.audio_b64 = base64.b64encode(audio_bytes).decode()
            st.session_state.timestamps = json.dumps(time_data)
            
            # Reconstrói HTML
            html_parts = []
            for item in time_data:
                html_parts.append(f"<span id='w-{item['index']}' class='word'>{item['word']}</span>")
            st.session_state.html_text = " ".join(html_parts)
            
            st.session_state.processing_done = True
            st.rerun() # Recarrega para mostrar o player limpo
            
        except Exception as e:
            st.error(f"Erro: {e}")

# ================================================
# PLAYER FINAL
# ================================================
if st.session_state.processing_done:
    st.markdown(f"""
    <div style="position:sticky; top:0; z-index:999; background:#0e1117; padding-bottom:10px;">
        <audio id="player" controls autoplay style="width: 100%;">
            <source src="data:audio/mp3;base64,{st.session_state.audio_b64}" type="audio/mp3">
        </audio>
    </div>
    <div id="text-container">
        {st.session_state.html_text}
    </div>

    <script>
        const timestamps = {st.session_state.timestamps};
        const player = document.getElementById('player');
        
        player.ontimeupdate = function() {{
            const time = player.currentTime;
            const activeItem = timestamps.find(item => time >= item.start && time <= item.end);
            
            if (activeItem) {{
                // Remove destaque anterior (limpeza bruta mas eficaz)
                document.querySelectorAll('.active-word').forEach(el => el.classList.remove('active-word'));
                
                const el = document.getElementById('w-' + activeItem.index);
                if (el) {{
                    el.classList.add('active-word');
                    el.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                }}
            }}
        }};
        
        // Clique na palavra para pular o audio
        const words = document.querySelectorAll('.word');
        words.forEach(w => {{
            w.onclick = function() {{
                const idx = parseInt(this.id.split('-')[1]);
                const data = timestamps.find(t => t.index === idx);
                if(data) player.currentTime = data.start;
                player.play();
            }}
        }});
    </script>
    """, unsafe_allow_html=True)

elif not uploaded_file:
    st.info("Aguardando arquivo PDF...")
