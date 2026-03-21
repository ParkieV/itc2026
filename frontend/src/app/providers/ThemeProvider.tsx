import { FC, ReactNode, useEffect, useState } from 'react'
import { ThemeContext, themes } from '../../contexts/ThemeContext'

const getTheme = () => {
  const theme = `${window?.localStorage?.getItem('theme')}`
  if (Object.values(themes).includes(theme)) return theme
  return themes.dark
}
interface ThemeProps {
  children: ReactNode
}
const ThemeProvider :FC<ThemeProps> = ({ children }) => {
  const [ theme, setTheme ] = useState(getTheme)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('theme', theme)
  }, [ theme ])

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export default ThemeProvider