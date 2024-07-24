import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import HomeView from './views/HomeView';
import ChatView from './views/ChatView';
import VoiceCloneView from './views/VoiceCloneView';
import FaceRecognitionView from './views/FaceRecognitionView';

function App() {
  return (
    <Router>
      <Switch>
        <Route exact path="/" component={HomeView} />
        <Route path="/chat" component={ChatView} />
        <Route path="/voice-clone" component={VoiceCloneView} />
        <Route path="/face-recognition" component={FaceRecognitionView} />
      </Switch>
    </Router>
  );
}

export default App;
