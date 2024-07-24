import React from 'react';
import { Link } from 'react-router-dom';

const HomeView = () => {
  return (
    <div>
      <h1>Home</h1>
      <nav>
        <ul>
          <li><Link to="/chat">Chat</Link></li>
          <li><Link to="/voice-clone">Voice Cloning</Link></li>
          <li><Link to="/face-recognition">Face Recognition</Link></li>
        </ul>
      </nav>
    </div>
  );
}

export default HomeView;
