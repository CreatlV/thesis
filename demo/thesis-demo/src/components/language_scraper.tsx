import { Box, Button, HStack, Heading, Input, Spinner, Text, VStack, useToast } from "@chakra-ui/react"
import axios from "axios"
import { useState } from "react"

interface ResponseLMScrape {
  gpt: ResponseGPT,
  text: string
}

interface ResponseGPT {
  productName: string,
  originalPrice: string | null,
  currentPrice: string,
  currency: string,
  description: string,
  specifications: string[],
}

interface ResponseAdapt {
  xpaths: Record<string, string>,
  domains: Record<string, object>
}

interface ResponseExtract {
  [key: string]: string
}

const LanguageScraper = () => {
  const [url, setUrl] = useState("")
  const [loading, setLoading] = useState(false)
  const [responseLM, setResponseLM] = useState<ResponseGPT | null>(null)
  const [text, setText] = useState("")

  const [responseAdapt, setResponseAdapt] = useState<ResponseAdapt | null>(null)
  const [responseExtract, setResponseExtract] = useState<ResponseExtract | null>(null)


  const toast = useToast()

  async function scrapeHandler() {
    if (url === "") {
      return
    }
    try {
      setLoading(true)
      const response = await axios.post('http://localhost:8989/lm/predict', {
        "url": url
      })
      const data = response.data as ResponseLMScrape
      setResponseLM(data.gpt)
      setText(data.text)
    } catch (error) {
      if (axios.isAxiosError(error)) {
        toast({
          title: "Error",
          description: error.response?.data.message,
          status: "error",
          isClosable: true,
        })
      }
    } finally {
      setLoading(false)
    }
  }

  async function adaptHandler() {
    if (url === "") {
      return
    }
    try {
      setLoading(true)
      const response = await axios.post('http://localhost:8989/lm/adapt', {
        "url": url
      })
      const data = response.data as ResponseAdapt
      setResponseAdapt(data)
      toast({
        title: "Success",
        description: "Adapted successfully",
        status: "success",
        duration: 5000,
        isClosable: true,
      })
    } catch (error) {
      if (axios.isAxiosError(error)) {
        toast({
          title: "Error",
          description: error.response?.data.message,
          status: "error",
          isClosable: true,
        })
      }
    } finally {
      setLoading(false)
    }
  }

  async function scrapeAdaptedHandler() {
    if (url === "") {
      return
    }
    try {
      setLoading(true)
      const response = await axios.post('http://localhost:8989/lm/extract', {
        "url": url
      })
      const data = response.data.data as ResponseExtract
      setResponseExtract(data)
    } catch (error) {
      if (axios.isAxiosError(error)) {
        toast({
          title: "Error",
          description: error.response?.data.detail,
          status: "error",
          isClosable: true,
        })
      }
    } finally {
      setLoading(false)
    }
  }




  return (
    <VStack w="100vw">
      <Heading m="32px">Open AI - Scraper</Heading>
      <Input w="500px" value={url} onChange={e => setUrl(e.target.value)} placeholder="URL" />
      {!loading && <HStack>
        <Button onClick={scrapeHandler} m="16px 0" w="140px">LM Scrape</Button>
        <Box borderLeft={"1px solid black"} p="4px 8px">
          <Button marginRight={"8px"} onClick={adaptHandler} >Adapt</Button>
          <Button onClick={scrapeAdaptedHandler}>Scrape adapted</Button>
        </Box>
      </HStack>}
      {loading && <Spinner />}

      <HStack mt="32px" spacing="32px">
        {responseLM && <VStack mt="32px" alignItems={"start"} maxW="600px" alignSelf={"start"} textAlign={"start"}>
          <Text><strong>Name: </strong>{responseLM.productName}</Text>
          <Text><strong>Original price: </strong>{responseLM.originalPrice}</Text>
          <Text><strong>Current price: </strong>{responseLM.currentPrice}</Text>
          <Text><strong>Currency: </strong>{responseLM.currency}</Text>
          <Text><strong>Description: </strong>{responseLM.description}</Text>
          <Box><strong>Specifications: </strong>{responseLM.specifications.map(spec => {
            return <Text>- {spec}</Text>
          })}</Box>
        </VStack>}
        {responseExtract && <VStack mt="32px" alignItems={"start"} maxW="600px" alignSelf={"start"} textAlign={"start"}>
          {Object.keys(responseExtract).map(key => {
            return <Text><strong>{key}: </strong>{responseExtract[key]}</Text>
          })}
        </VStack>}
      </HStack>
    </VStack>
  )
}

export default LanguageScraper