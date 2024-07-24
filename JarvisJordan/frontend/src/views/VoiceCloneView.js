import React, { useState } from 'react';
import axios from 'axios';

const VoiceCloneView = () => {
  const [text, setText] = useState('');
  const [audioPath, setAudioPath] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await axios.get(`/api/voice-clone/?text=${text}`);
    setAudioPath(result.data.audio_path);
  }

  return (
    <div>
      <h1>Voice Cloning</h1>
      <form onSubmit={handleSubmit}>
        <input type="text" value={text} onChange={(e) => setText(e.target.value)} />
        <button type="submit">Generate Voice</button>
      </form>
      {audioPath && <audio controls src={`/${audioPath}`} />}
    </div>
  );
}

export default VoiceCloneView;
