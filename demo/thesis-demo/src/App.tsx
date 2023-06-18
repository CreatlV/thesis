import { Route } from 'wouter'
import './App.css'
import ImageUpload from './components/image_upload'
import { ChakraProvider } from "@chakra-ui/react"
import LanguageScraper from './components/language_scraper'

function App() {

  return (
    <ChakraProvider>
      <Route>
        <ImageUpload />
      </Route>
      <Route path='/lm'>
        <LanguageScraper />
      </Route>
    </ChakraProvider>
  )
}

export default App
