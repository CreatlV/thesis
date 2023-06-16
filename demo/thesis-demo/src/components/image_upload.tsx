import { Box, Button, FormControl, FormLabel, Heading, Input, VStack } from '@chakra-ui/react';
import axios from 'axios';
import { ChangeEvent, FormEvent, useEffect, useRef, useState } from 'react';

interface Response {
  scores: number[],
  labels: number[],
  boxes: number[][],
}

const categoryMap = new Map<number, string>([
  [0, "Price"],
  [1, "Product Name"],
  [2, "Image"],
]);

const ImageUpload = () => {
  const [image, setImage] = useState<File | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [boxes, setBoxes] = useState<number[][]>([]);
  const [labels, setLabels] = useState<number[]>([]);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    setResult(null);
    setBoxes([]);
    setLabels([]);

  }, [image]);

  useEffect(() => {
    if (canvasRef.current && previewImage) {
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      let img = new Image();
      img.src = previewImage;
      img.onload = function () {
        const scaleFactor = 700 / img.width; // or 500 / img.height to scale by height
        canvas.width = img.width * scaleFactor;
        canvas.height = img.height * scaleFactor;
        if (!context) {
          return;
        }
        context.drawImage(img, 0, 0, canvas.width, canvas.height);

        // Draw the bounding boxes
        context.beginPath();
        boxes.forEach((box) => {
          context.rect(box[0] * scaleFactor, box[1] * scaleFactor, (box[2] - box[0]) * scaleFactor, (box[3] - box[1]) * scaleFactor);
        });

        // Draw the labels
        context.font = `${20 * scaleFactor}px Arial`;
        context.fillStyle = 'red';
        labels.forEach((label, index) => {
          const text = categoryMap.get(label);
          context.fillText(text ?? "unknown", boxes[index][0] * scaleFactor, boxes[index][1] * scaleFactor - 5);
        });

        context.strokeStyle = 'rgba(255, 0, 0, 0.7)';
        context.lineWidth = 4 * scaleFactor;
        context.stroke();
      };
    }
  }, [previewImage, boxes]);


  const handleImageUpload = (event: ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) {
      return;
    }

    setPreviewImage(URL.createObjectURL(event.target.files[0]));
    setImage(event.target.files[0]);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (image) {
      let formData = new FormData();
      formData.append("file", image);

      try {
        const response = await axios.post(
          "http://localhost:8989/predict",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );

        const data: Response = response.data["data"][0];
        setResult(JSON.stringify(response.data, null, 2));
        setBoxes(data.boxes);  // Save the bounding boxes
        setLabels(data.labels);  // Save the labels
      } catch (error) {
        if (axios.isAxiosError(error)) {
          setResult("Error: " + error?.response?.data?.message);
        }
      }
    }
  };

  return (
    <>
      <VStack
        spacing={5}
        width="400px"
        maxW="md"
        margin="auto"
        p={5}
        border="1px"
        borderRadius="md"
        borderColor="gray.200"
        boxShadow="lg"
      >
        <Heading>Upload Image</Heading>
        <form onSubmit={handleSubmit}>
          <FormControl id="upload-image">
            <FormLabel cursor={"pointer"} background={"#e8e8e8"} p="8px 16px" borderRadius="8px">Choose an image
              <Input display={"none"} type="file" accept="image/*" onChange={handleImageUpload} />
            </FormLabel>
          </FormControl>
          <Button opacity={!image ? 0.5 : 1} colorScheme="teal" type="submit" mt="16px">
            Submit
          </Button>
        </form>
      </VStack>
      <Box mt="16px">
        {previewImage && <canvas ref={canvasRef} />}
      </Box>
    </>
  );
}

export default ImageUpload;
