import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import DocumentEditor from './pages/DocumentEditor'
import Settings from './pages/Settings'
import Header from './components/Header'

function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<DocumentEditor />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
