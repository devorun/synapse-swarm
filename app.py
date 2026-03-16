import streamlit as st
from PIL import Image
import subprocess
import re
import base64
import os
import speech_recognition as sr
from audiorecorder import audiorecorder
from gtts import gTTS

# --- PAGE CONFIG ---
st.set_page_config(page_title="SYNAPSE CORE", layout="wide", initial_sidebar_state="collapsed")

# --- HELPER FUNCTIONS ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return ""

def clean_hermes_output(text):
    match = re.search(r'╭─ ⚕ Hermes ─+╮(.*?)╰─+╯', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def get_local_image(filename, fallback_url):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            ext = filename.split('.')[-1]
            return f"data:image/{ext};base64,{encoded}"
    return fallback_url

def render_agent(placeholder, name, role, color, text_html, img_src):
    placeholder.markdown(f'''
    <div class="agent-chat-box" style="border-left: 4px solid {color};">
        <img src="{img_src}" class="agent-avatar" style="border-color: {color};">
        <div class="agent-text-area">
            <h4 class="agent-name" style="color: {color};">{name} <span style="font-size: 12px; color: #555;">[{role}]</span></h4>
            <p class="agent-message">{text_html}</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# YENİ: Otomatik Ses Oynatıcı (Görünmez oynatıcı, sistem konuşuyormuş hissi verir)
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

def transcribe_audio(audio_segment):
    audio_segment.export("temp_command.wav", format="wav")
    r = sr.Recognizer()
    with sr.AudioFile("temp_command.wav") as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data, language="tr-TR")
            return text, "TR"
        except:
            try:
                text = r.recognize_google(audio_data, language="en-US")
                return text, "EN"
            except:
                return None, "fail"

# --- SIDEBAR (AGENT CORE DIRECTIVES) ---
st.sidebar.markdown("### 🎛️ AGENT PROTOCOLS")
st.sidebar.caption("Modify agent core directives here. Do not remove the {command} and {zero_scan} variables.")

sys_zero = st.sidebar.text_area("ZERO (Vision) Prompt", 
"You are ZERO, an AI vision analyst. Operator command: '{command}'. Describe 'capture.jpg' focusing on this command. List 2 key visual details. Stay tactical.", height=120)

sys_nova = st.sidebar.text_area("NOVA (Tactical) Prompt", 
"You are NOVA, a creative strategic analyst. ZERO scan: '{zero_scan}'. Goal: '{command}'. Suggest 1 engaging tactical angle based on this object. 2 sentences max.", height=120)

sys_titan = st.sidebar.text_area("TITAN (Arbiter) Prompt", 
"You are TITAN, the Arbiter. Command: '{command}'. ZERO: '{zero_scan}'. NOVA: '{nova_tactic}'. Give a 1-sentence final verdict to finalize the strategy.", height=120)

# --- CSS & ARKA PLAN ---
bg_base64 = get_base64_image("bg.png")
bg_css = f"<style>.stApp {{ background-image: url('data:image/png;base64,{bg_base64}'); background-size: cover; background-position: center; background-attachment: fixed; }}</style>" if bg_base64 else ""

ui_css = """
<style>
    .title-text { font-family: 'Courier New', monospace; font-weight: 700; text-align: center; color: #1a1a1a; margin-bottom: 0px;}
    .subtitle-text { color: #555; text-align: center; font-family: 'Courier New', monospace; margin-bottom: 30px; font-size: 14px;}
    .agent-chat-box { display: flex; align-items: center; margin-bottom: 20px; background-color: rgba(15, 15, 20, 0.8); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); }
    .agent-avatar { width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-right: 20px; border: 2px solid #444; }
    .agent-message { font-family: 'Courier New', monospace; font-size: 14px; color: #f0f0f0; margin: 0; line-height: 1.5; }
    .neon-success { background-color: rgba(0, 30, 0, 0.8) !important; border: 2px solid #39FF14 !important; color: #39FF14 !important; padding: 12px; border-radius: 8px; font-weight: bold; text-align: center; font-family: 'Courier New', monospace; box-shadow: 0 0 15px rgba(57, 255, 20, 0.3); margin-bottom: 15px; }
    .voice-box { background-color: rgba(0,0,0,0.6); padding: 15px; border-radius: 8px; border-left: 4px solid #00FFFF; margin-top:10px; margin-bottom: 10px; color: #fff; font-family: 'Courier New';}
    h4 { color: #1a1a1a !important; font-family: Courier New; font-weight: bold; }
</style>
"""

st.markdown(bg_css, unsafe_allow_html=True)
st.markdown(ui_css, unsafe_allow_html=True)

# --- AVATARS ---
img_zero = get_local_image("zero.gif", get_local_image("zero.png", "https://i.gifer.com/ZMBs.gif"))
img_nova = get_local_image("nova.gif", get_local_image("nova.png", "https://i.gifer.com/1YZ.gif"))
img_titan = get_local_image("titan.gif", get_local_image("titan.png", "https://i.gifer.com/Xqg8.gif"))

# --- HEADER ---
st.markdown("<h2 class='title-text'>SYNAPSE_SWARM // LIVE FEED</h2>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>OPERATOR: DEVORUN | COGNITIVE AGENT CHAIN</p>", unsafe_allow_html=True)

left_col, right_col = st.columns([1.5, 1])

with left_col:
    st.markdown("<h4 style='border-bottom: 2px solid #555; padding-bottom: 10px;'>[ SQUAD DISCUSSION ]</h4>", unsafe_allow_html=True)
    zero_ph, nova_ph, titan_ph = st.empty(), st.empty(), st.empty()
    render_agent(zero_ph, "ZERO", "VISION", "#00FFFF", "STANDBY. AWAITING VISUAL INPUT...", img_zero)
    render_agent(nova_ph, "NOVA", "TACTICAL", "#FF9100", "STANDBY. AWAITING ZERO'S INTEL...", img_nova)
    render_agent(titan_ph, "TITAN", "ARBITER", "#FFD700", "STANDBY. AWAITING SQUAD DATA...", img_titan)

with right_col:
    st.markdown("<h4 style='text-align: center;'>[ SENSOR INPUT ]</h4>", unsafe_allow_html=True)
    if 'cam_active' not in st.session_state: st.session_state.cam_active = False
    if st.button("👁️ TOGGLE CAMERA MODULE", use_container_width=True):
        st.session_state.cam_active = not st.session_state.cam_active

    if st.session_state.cam_active:
        camera_photo = st.camera_input("TAKE SNAPSHOT", label_visibility="collapsed")
        if camera_photo is not None:
            img = Image.open(camera_photo)
            img.save("capture.jpg")
            
            st.markdown("<div class='neon-success'>✅ VISUAL ACQUIRED. AWAITING DIRECTIVE...</div>", unsafe_allow_html=True)
            
            st.markdown("#### 🎙️ / ⌨️ OPERATOR DIRECTIVE")
            input_col1, input_col2 = st.columns([1, 2])
            
            with input_col1:
                audio = audiorecorder("START RECORDING", "STOP & EXECUTE")
            with input_col2:
                manual_text = st.text_input("Silent Protocol:", placeholder="Type command here...", label_visibility="collapsed")
                execute_text = st.button("EXECUTE TEXT", use_container_width=True)

            final_cmd = None
            cmd_type = None

            if len(audio) > 0:
                with st.spinner("Decoding audio signature..."):
                    voice_text, voice_lang = transcribe_audio(audio)
                    if voice_text:
                        final_cmd = voice_text
                        cmd_type = f"VOICE - {voice_lang}"
            elif execute_text and manual_text:
                final_cmd = manual_text
                cmd_type = "TEXT"

            if final_cmd:
                st.markdown(f"<div class='voice-box'><b>OPERATOR COMMAND ({cmd_type}):</b> {final_cmd}</div>", unsafe_allow_html=True)
                
                # --- ZERO ---
                render_agent(zero_ph, "ZERO", "VISION", "#00FFFF", "<i>Analyzing based on directive...</i>", img_zero)
                prompt_zero = sys_zero.replace("{command}", final_cmd)
                res_zero = subprocess.run(["hermes", "chat", "-q", prompt_zero], capture_output=True, text=True)
                zero_out_raw = clean_hermes_output(res_zero.stdout)
                render_agent(zero_ph, "ZERO", "VISION", "#00FFFF", zero_out_raw.replace('\n', '<br>'), img_zero)
                
                # --- NOVA ---
                render_agent(nova_ph, "NOVA", "TACTICAL", "#FF9100", "<i>Formulating strategy...</i>", img_nova)
                prompt_nova = sys_nova.replace("{command}", final_cmd).replace("{zero_scan}", zero_out_raw)
                res_nova = subprocess.run(["hermes", "chat", "-q", prompt_nova], capture_output=True, text=True)
                nova_out_raw = clean_hermes_output(res_nova.stdout)
                render_agent(nova_ph, "NOVA", "TACTICAL", "#FF9100", nova_out_raw.replace('\n', '<br>'), img_nova)
                
                # --- TITAN (WITH VOICE!) ---
                render_agent(titan_ph, "TITAN", "ARBITER", "#FFD700", "<i>Issuing verdict...</i>", img_titan)
                prompt_titan = sys_titan.replace("{command}", final_cmd).replace("{zero_scan}", zero_out_raw).replace("{nova_tactic}", nova_out_raw)
                res_titan = subprocess.run(["hermes", "chat", "-q", prompt_titan], capture_output=True, text=True)
                titan_out_raw = clean_hermes_output(res_titan.stdout)
                render_agent(titan_ph, "TITAN", "ARBITER", "#FFD700", titan_out_raw.replace('\n', '<br>'), img_titan)
                
                # TITAN'ın ses dosyasını oluştur ve arka planda görünmez olarak oynat!
                try:
                    tts = gTTS(text=titan_out_raw, lang='en', slow=False)
                    tts.save("titan_voice.mp3")
                    autoplay_audio("titan_voice.mp3")
                except Exception as e:
                    st.warning(f"Audio module offline: {e}")

                st.markdown("<p class='neon-success' style='color: #39FF14;'>✅ SWARM ANALYSIS COMPLETE.</p>", unsafe_allow_html=True)
                
                export_data = f"OPERATOR COMMAND: {final_cmd}\n\n[ZERO - VISION]\n{zero_out_raw}\n\n[NOVA - TACTICAL]\n{nova_out_raw}\n\n[TITAN - ARBITER]\n{titan_out_raw}"
                st.download_button(label="💾 DOWNLOAD EXPORT REPORT (.txt)", data=export_data, file_name="swarm_operation_report.txt", mime="text/plain", use_container_width=True)

            elif execute_text and not manual_text:
                st.warning("⚠️ Please enter a text command before executing.")
            elif len(audio) > 0 and not final_cmd:
                st.error("❌ Audio unclear. Try again or use text input.")
    else:
        st.info("SYSTEM ON STANDBY.")
