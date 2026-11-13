/* No microphone control is exposed. Kept for integrations that supply speech errors. */
(function(){
 const messages={
  'not-allowed':'Microphone permission was denied. Please type your farming question.',
  'service-not-allowed':'The speech service is unavailable. Please type your farming question.',
  'audio-capture':'No microphone was found. Please type your farming question.',
  'no-speech':'No speech was detected. Please type your farming question.',
  'network':'The speech service network failed. Please type your farming question.',
  'aborted':'Voice input was cancelled. Please type your farming question.',
  'language-not-supported':'Speech recognition does not support this language. Please type your farming question.'
 };
 window.VoiceErrors={message:code=>messages[code]||'Voice input failed. Please type your farming question.',render(code,node){node.textContent=this.message(code);}};
})();
