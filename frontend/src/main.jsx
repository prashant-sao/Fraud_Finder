import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import MainScreen from './main_screen.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <MainScreen />
  </StrictMode>,
)