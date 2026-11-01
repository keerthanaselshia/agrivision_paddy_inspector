"""
core/speech.py  –  Speech Technology for AgriVision Paddy Inspector.

Features:
  • Web Speech API Text-to-Speech (speechSynthesis) for English (en-IN) and Tamil (ta-IN)
  • Speech-to-Text (SpeechRecognition) microphone input with auto-fill & submit
  • Speech rate toggle: Normal (1.0x) / Slow (0.8x)
  • Single tap to read aloud, tap again to stop
  • "Read all" button for disease detail pages
  • Auto-read answers toggle
  • Graceful fallback when Speech API or microphone is not supported / allowed
"""

import json
import streamlit as st
import streamlit.components.v1 as components
from core.theme import clean_html, render_html


def render_tts_button(
    text: str,
    lang: str = "en",
    speed: float = 1.0,
    button_id: str = "tts_btn",
    label: str = "🔊 Listen",
    stop_label: str = "⏹️ Stop",
    key: str | None = None,
    height: int = 42,
    tamil_script_text: str | None = None,
) -> None:
    """Render a toggleable Text-to-Speech button using browser speechSynthesis.

    For Tanglish answers, reads the paired Tamil-script version using ta-IN voice;
    if no Tamil text is available, hides the button gracefully.
    """
    if not text:
        return

    # Handle Tanglish requirement: read Tamil-script equivalent or hide button
    if lang == "tanglish":
        if tamil_script_text and tamil_script_text.strip():
            spoken_text = tamil_script_text
            voice_lang = "ta-IN"
        else:
            # Hide the button if no Tamil-script counterpart exists
            return
    elif lang == "ta" or any("\u0b80" <= c <= "\u0bff" for c in text):
        spoken_text = text
        voice_lang = "ta-IN"
    else:
        spoken_text = text
        voice_lang = "en-IN"

    clean_text = spoken_text.replace('"', '\\"').replace("\n", " ").replace("\r", " ").strip()

    html_code = f"""
    <div style="display:inline-block;margin:2px 0;">
      <button id="{button_id}" onclick="toggleTTS_{button_id}()"
        style="display:inline-flex;align-items:center;gap:6px;background:#1a3d28;color:#2ee59d;
               border:1px solid rgba(46,229,157,0.35);border-radius:20px;padding:6px 14px;
               font-family:'Poppins',sans-serif;font-size:0.82em;font-weight:600;cursor:pointer;
               transition:all 0.2s;box-shadow:0 2px 8px rgba(0,0,0,0.25);">
        <span id="{button_id}_lbl">{label}</span>
      </button>
      <span id="{button_id}_err" style="color:#ffd166;font-size:0.75em;margin-left:8px;display:none;"></span>
    </div>
    <script>
      var isSpeaking_{button_id} = false;
      function toggleTTS_{button_id}() {{
        if (!('speechSynthesis' in window)) {{
          var err = document.getElementById("{button_id}_err");
          err.innerText = "Speech not supported in this browser";
          err.style.display = "inline";
          return;
        }}
        var btnLbl = document.getElementById("{button_id}_lbl");
        if (isSpeaking_{button_id} && window.speechSynthesis.speaking) {{
          window.speechSynthesis.cancel();
          isSpeaking_{button_id} = false;
          btnLbl.innerText = "{label}";
          return;
        }}
        window.speechSynthesis.cancel();
        var utter = new SpeechSynthesisUtterance("{clean_text}");
        utter.lang = "{voice_lang}";
        utter.rate = {speed};
        
        // Try to pick suitable voice if available
        var voices = window.speechSynthesis.getVoices();
        for (var i = 0; i < voices.length; i++) {{
          if (voices[i].lang.indexOf("{voice_lang}") !== -1) {{
            utter.voice = voices[i];
            break;
          }}
        }}

        utter.onstart = function() {{
          isSpeaking_{button_id} = true;
          btnLbl.innerText = "{stop_label}";
        }};
        utter.onend = function() {{
          isSpeaking_{button_id} = false;
          btnLbl.innerText = "{label}";
        }};
        utter.onerror = function() {{
          isSpeaking_{button_id} = false;
          btnLbl.innerText = "{label}";
        }};
        window.speechSynthesis.speak(utter);
      }}
    </script>
    """
    components.html(html_code, height=height)


def render_read_all_button(
    sections: list[tuple[str, str]],
    lang: str = "en",
    speed: float = 1.0,
    button_id: str = "read_all_btn",
    height: int = 44,
) -> None:
    """Render a 'Read All' button that reads multiple sections in sequence."""
    combined_parts = []
    for title, body in sections:
        if body:
            combined_parts.append(f"{title}. {body}")
    full_text = " ".join(combined_parts).replace('"', '\\"').replace("\n", " ").strip()
    voice_lang = "ta-IN" if (lang == "ta" or any("\u0b80" <= c <= "\u0bff" for c in full_text)) else "en-IN"
    btn_label = "🔊 Read All Sections" if lang != "ta" else "🔊 முழு விபரத்தையும் கேளுங்கள்"
    stop_label = "⏹️ Stop Reading" if lang != "ta" else "⏹️ நிறுத்து"

    html_code = f"""
    <div style="margin:8px 0;">
      <button id="{button_id}" onclick="toggleReadAll_{button_id}()"
        style="display:inline-flex;align-items:center;gap:8px;background:linear-gradient(135deg,#1a3d28,#12301f);
               color:#2ee59d;border:1.5px solid #2ee59d;border-radius:22px;padding:8px 20px;
               font-family:'Poppins',sans-serif;font-size:0.9em;font-weight:700;cursor:pointer;
               box-shadow:0 4px 14px rgba(46,229,157,0.2);">
        <span id="{button_id}_lbl">{btn_label}</span>
      </button>
      <span id="{button_id}_err" style="color:#ffd166;font-size:0.78em;margin-left:8px;display:none;"></span>
    </div>
    <script>
      var isReading_{button_id} = false;
      function toggleReadAll_{button_id}() {{
        if (!('speechSynthesis' in window)) {{
          var err = document.getElementById("{button_id}_err");
          err.innerText = "Speech not supported";
          err.style.display = "inline";
          return;
        }}
        var btnLbl = document.getElementById("{button_id}_lbl");
        if (isReading_{button_id} && window.speechSynthesis.speaking) {{
          window.speechSynthesis.cancel();
          isReading_{button_id} = false;
          btnLbl.innerText = "{btn_label}";
          return;
        }}
        window.speechSynthesis.cancel();
        var utter = new SpeechSynthesisUtterance("{full_text}");
        utter.lang = "{voice_lang}";
        utter.rate = {speed};
        utter.onstart = function() {{
          isReading_{button_id} = true;
          btnLbl.innerText = "{stop_label}";
        }};
        utter.onend = function() {{
          isReading_{button_id} = false;
          btnLbl.innerText = "{btn_label}";
        }};
        utter.onerror = function() {{
          isReading_{button_id} = false;
          btnLbl.innerText = "{btn_label}";
        }};
        window.speechSynthesis.speak(utter);
      }}
    </script>
    """
    components.html(html_code, height=height)


def render_mic_button(
    target_input_label: str = "Ask a question about this disease...",
    lang: str = "en",
    height: int = 58,
) -> None:
    """Render a touch-friendly microphone button for Speech-to-Text input."""
    rec_lang = "ta-IN" if lang == "ta" else "en-IN"
    mic_title = "Click to speak in Tamil" if lang == "ta" else "Click to speak your question"
    listening_text = "🎙️ Listening... Speak now" if lang != "ta" else "🎙️ கேட்கிறது... பேசுங்கள்"

    html_code = f"""
    <div style="display:flex;align-items:center;gap:10px;margin:6px 0;">
      <button id="mic_btn" type="button" onclick="startDictation()" title="{mic_title}"
        style="display:inline-flex;align-items:center;justify-content:center;width:42px;height:42px;
               background:#1a3d28;color:#2ee59d;border:2px solid #2ee59d;border-radius:50%;
               cursor:pointer;font-size:1.2em;transition:all 0.2s;box-shadow:0 0 12px rgba(46,229,157,0.35);">
        🎤
      </button>
      <span id="mic_status" style="font-family:'Poppins',sans-serif;font-size:0.82em;color:#8ab89a;"></span>
    </div>
    <script>
      function startDictation() {{
        var SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        var status = document.getElementById("mic_status");
        var btn = document.getElementById("mic_btn");

        if (!SpeechRec) {{
          status.innerText = "Microphone input not supported in this browser. Please type below.";
          status.style.color = "#ffd166";
          return;
        }}

        var recognition = new SpeechRec();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "{rec_lang}";

        btn.style.background = "#ff5d5d";
        btn.style.borderColor = "#ff5d5d";
        btn.style.boxShadow = "0 0 16px rgba(255,93,93,0.6)";
        status.innerText = "{listening_text}";
        status.style.color = "#2ee59d";

        recognition.onresult = function(e) {{
          var transcript = e.results[0][0].transcript;
          status.innerText = "Transcribed: " + transcript;
          status.style.color = "#2ee59d";
          btn.style.background = "#1a3d28";
          btn.style.borderColor = "#2ee59d";
          btn.style.boxShadow = "0 0 12px rgba(46,229,157,0.35)";

          // Inject into parent window Streamlit text input
          try {{
            var inputs = window.parent.document.querySelectorAll('input[type="text"]');
            var target = null;
            for (var i = 0; i < inputs.length; i++) {{
              var placeholder = inputs[i].getAttribute('placeholder') || '';
              var aria = inputs[i].getAttribute('aria-label') || '';
              if (placeholder.indexOf("question") !== -1 || aria.indexOf("question") !== -1 || placeholder.indexOf("கேள்வி") !== -1) {{
                target = inputs[i];
                break;
              }}
            }}
            if (!target && inputs.length > 0) {{
              target = inputs[inputs.length - 1];
            }}
            if (target) {{
              var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
              nativeInputValueSetter.call(target, transcript);
              target.dispatchEvent(new Event('input', {{ bubbles: true }}));
              target.dispatchEvent(new Event('change', {{ bubbles: true }}));
              target.focus();
            }}
          }} catch(err) {{
            console.error("STT injection:", err);
          }}
        }};

        recognition.onerror = function(e) {{
          status.innerText = "Microphone error: " + (e.error || "unavailable");
          status.style.color = "#ffd166";
          btn.style.background = "#1a3d28";
          btn.style.borderColor = "#2ee59d";
          btn.style.boxShadow = "0 0 12px rgba(46,229,157,0.35)";
        }};

        recognition.onend = function() {{
          btn.style.background = "#1a3d28";
          btn.style.borderColor = "#2ee59d";
          btn.style.boxShadow = "0 0 12px rgba(46,229,157,0.35)";
        }};

        recognition.start();
      }}
    </script>
    """
    components.html(html_code, height=height)


def stop_all_speech() -> None:
    """Inject a small script to stop any ongoing speech synthesis."""
    components.html("<script>if ('speechSynthesis' in window) { window.speechSynthesis.cancel(); }</script>", height=0)
