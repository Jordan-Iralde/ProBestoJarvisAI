import { useState } from 'react'
import Header from './app/shared/header'
import Home from './app/pages/home/home'
import Footer from './app/shared/footer'

import './App.css'

function App() {
  const [section, setSection] = useState<"home" | "projects"| "about"| "services">("home");

  return (
    <>
      <Header setSection={setSection} />
      {section === "home" && <Home />}
      
      <Footer />
    </>
  )
}

export default App
