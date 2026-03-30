const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const micButton = document.getElementById("micButton");
const voiceStatus = document.getElementById("voiceStatus");

let recognition = null;
let isListening = false;
let inputPrefix = "";
let finalTranscript = "";
const speechSupported = "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
let activeUtterance = null;
let activeSpeakButton = null;

const speakerIcon = `
  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
    <path d="M4 9v6h4l5 4V5L8 9H4Zm11.5 3a4.5 4.5 0 0 0-2.5-4.04v8.08A4.5 4.5 0 0 0 15.5 12Zm2.5 0a7 7 0 0 1-4 6.32v-1.74a5.5 5.5 0 0 0 0-9.16V5.68A7 7 0 0 1 18 12Z"></path>
  </svg>
`;

function addMessage(text, type, sources) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${type}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  wrapper.appendChild(bubble);

  if (sources && sources.length) {
    const sourceLine = document.createElement("div");
    sourceLine.className = "sources";
    sourceLine.textContent = formatSources(sources);
    wrapper.appendChild(sourceLine);
  }

  if (type === "bot") {
    const speakButton = createSpeakButton(bubble);
    wrapper.appendChild(speakButton);
  }

  chatWindow.appendChild(wrapper);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return wrapper;
}

function formatSources(sources) {
  return `Sources: ${sources
    .map((source) => `${source.id} - ${source.title}`)
    .join(" | ")}`;
}

function setSources(wrapper, sources) {
  if (!sources || !sources.length) {
    return;
  }
  const sourceLine = document.createElement("div");
  sourceLine.className = "sources";
  sourceLine.textContent = formatSources(sources);
  const speakButton = wrapper.querySelector(".speak-button");
  if (speakButton) {
    wrapper.insertBefore(sourceLine, speakButton);
  } else {
    wrapper.appendChild(sourceLine);
  }
}

function stopSpeaking() {
  if (!speechSupported) {
    return;
  }
  window.speechSynthesis.cancel();
  if (activeSpeakButton) {
    activeSpeakButton.classList.remove("is-speaking");
  }
  activeSpeakButton = null;
  activeUtterance = null;
}

function toggleSpeech(text, button) {
  if (!speechSupported) {
    return;
  }
  const trimmed = text.trim();
  if (!trimmed) {
    return;
  }
  if (activeSpeakButton === button) {
    stopSpeaking();
    return;
  }

  stopSpeaking();
  const utterance = new SpeechSynthesisUtterance(trimmed);
  activeUtterance = utterance;
  activeSpeakButton = button;
  button.classList.add("is-speaking");

  utterance.onend = () => {
    if (activeSpeakButton === button) {
      button.classList.remove("is-speaking");
      activeSpeakButton = null;
      activeUtterance = null;
    }
  };

  utterance.onerror = () => {
    if (activeSpeakButton === button) {
      button.classList.remove("is-speaking");
      activeSpeakButton = null;
      activeUtterance = null;
    }
  };

  window.speechSynthesis.speak(utterance);
}

function createSpeakButton(bubble) {
  const speakButton = document.createElement("button");
  speakButton.type = "button";
  speakButton.className = "speak-button";
  speakButton.setAttribute("aria-label", "Speak answer");
  speakButton.innerHTML = speakerIcon;

  if (!speechSupported) {
    speakButton.disabled = true;
    speakButton.title = "Text-to-speech is not supported in this browser.";
    return speakButton;
  }

  speakButton.addEventListener("click", () => {
    toggleSpeech(bubble.textContent, speakButton);
  });

  return speakButton;
}

function setVoiceStatus(message, isError = false) {
  if (!voiceStatus) {
    return;
  }
  voiceStatus.textContent = message;
  voiceStatus.classList.toggle("error", Boolean(isError));
}

function setListeningState(listening) {
  isListening = listening;
  if (!micButton) {
    return;
  }
  micButton.classList.toggle("is-listening", listening);
  micButton.setAttribute("aria-pressed", listening ? "true" : "false");
  micButton.setAttribute("aria-label", listening ? "Stop voice input" : "Start voice input");
}

function initVoiceInput() {
  if (!micButton) {
    return;
  }
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    micButton.disabled = true;
    micButton.title = "Voice input is not supported in this browser.";
    setVoiceStatus("Voice input is not supported in this browser.", true);
    return;
  }

  recognition = new SpeechRecognition();
  recognition.interimResults = true;
  recognition.continuous = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    inputPrefix = messageInput.value.trim();
    finalTranscript = "";
    setListeningState(true);
    setVoiceStatus("Listening... Speak now.");
  };

  recognition.onresult = (event) => {
    let interimTranscript = "";
    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      const result = event.results[i];
      const transcript = result[0].transcript;
      if (result.isFinal) {
        finalTranscript = `${finalTranscript} ${transcript}`.trim();
      } else {
        interimTranscript = `${interimTranscript} ${transcript}`.trim();
      }
    }
    const captured = [finalTranscript, interimTranscript].filter(Boolean).join(" ");
    const combined = [inputPrefix, captured].filter(Boolean).join(" ");
    if (combined) {
      messageInput.value = combined;
    }
  };

  recognition.onerror = (event) => {
    setVoiceStatus(`Voice input error: ${event.error}.`, true);
  };

  recognition.onend = () => {
    setListeningState(false);
    if (messageInput.value.trim()) {
      setVoiceStatus("Voice input captured. Review and send.");
    } else {
      setVoiceStatus("Voice input stopped.");
    }
  };

  micButton.addEventListener("click", () => {
    if (!recognition) {
      return;
    }
    if (isListening) {
      recognition.stop();
      return;
    }
    try {
      recognition.start();
    } catch (error) {
      setVoiceStatus("Voice input is already running.", true);
    }
  });
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) {
    return;
  }

  if (isListening && recognition) {
    recognition.stop();
  }

  addMessage(message, "user");
  messageInput.value = "";

  const pending = addMessage("Searching policies...", "bot");

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    const bubble = pending.querySelector(".bubble");
    bubble.textContent = data.answer || "No response received.";
    setSources(pending, data.sources);
  } catch (error) {
    const bubble = pending.querySelector(".bubble");
    bubble.textContent = "Something went wrong. Please try again.";
  }
});

initVoiceInput();
