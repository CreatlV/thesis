import './App.css'
import ImageUpload from './components/image_upload'
import { ChakraProvider } from "@chakra-ui/react"

function App() {

  return (
    <ChakraProvider>
      <ImageUpload />
    </ChakraProvider>
  )
}

export default App
