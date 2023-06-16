import { Box, FormControl, FormLabel, Heading, Input, Spinner, VStack } from '@chakra-ui/react';
import axios from 'axios';
import { ChangeEvent, useEffect, useRef, useState } from 'react';

interface Response {
  scores: number[],
  labels: number[],
  boxes: number[][],
  processed_image: string,
}

const categoryMap = new Map<number, string>([
  [0, "Price"],
  [1, "Product Name"],
  [2, "Image"],
]);

const ImageUpload = () => {
  const [image, setImage] = useState<null | string>(null);
  const [previewImage, setPreviewImage] = useState<File | null>(null);  // Preview image
  const [boxes, setBoxes] = useState<number[][]>([]);
  const [labels, setLabels] = useState<number[]>([]);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [loading, setLoading] = useState(false)

  // First useEffect for drawing the image
  useEffect(() => {
    if (canvasRef.current && previewImage) {
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      let img = new Image();

      img.src = URL.createObjectURL(previewImage)

      img.onload = function () {
        const scale = 700 / img.width; // or 500 / img.height to scale by height
        canvas.width = img.width * scale;
        canvas.height = img.height * scale;

        if (!context) {
          return;
        }

        context.drawImage(img, 0, 0, canvas.width, canvas.height);

      };
    }
  }, [previewImage]);

  // First useEffect for drawing the image
  useEffect(() => {
    if (canvasRef.current && image) {
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      let img = new Image();

      img.src = `data:image/jpeg;base64,${image}`;

      img.onload = function () {
        const scale = 700 / img.width; // or 500 / img.height to scale by height
        canvas.width = img.width * scale;
        canvas.height = img.height * scale;

        if (!context) {
          return;
        }
        context.drawImage(img, 0, 0, canvas.width, canvas.height);

        // Draw the bounding boxes
        context.beginPath();
        boxes.forEach((box) => {
          context.rect(box[0] * scale, box[1] * scale, (box[2] - box[0]) * scale, (box[3] - box[1]) * scale);
        });

        // Draw the labels
        context.font = `${20 * scale}px Arial`;
        context.fillStyle = 'red';
        labels.forEach((label, index) => {
          const text = categoryMap.get(label);
          context.fillText(text ?? "unknown", boxes[index][0] * scale, boxes[index][1] * scale - 5);
        });

        context.strokeStyle = 'rgba(255, 0, 0, 0.7)';
        context.lineWidth = 4 * scale;
        context.stroke();

      };
    }
  }, [image]);

  const handleImageUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) {
      return;
    }

    setBoxes([]);
    setLabels([]);
    setPreviewImage(event.target.files[0]);
    setImage(null);

    let formData = new FormData();
    formData.append("file", event.target.files[0]);

    try {
      setLoading(true)
      const response = await axios.post(
        "http://localhost:8989/predict",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      const data: Response = response.data;
      console.log(data);
      setBoxes(data.boxes);  // Save the bounding boxes
      setLabels(data.labels);  // Save the labels
      setImage(data.processed_image);  // Save the processed image
    } catch (error) {
      if (axios.isAxiosError(error)) {
        // Handle error
      }
    } finally {
      setLoading(false)
    }
  }


  return (
    <>
      <VStack
        spacing={5}
        width="400px"
        height="150px"
        maxW="md"
        margin="auto"
        p={5}
        border="1px"
        borderRadius="md"
        borderColor="gray.200"
        boxShadow="lg"
      >
        <Heading>Upload Image</Heading>
        {!loading && <FormControl id="upload-image">
          <FormLabel textAlign={"center"} cursor={"pointer"} background={"#e8e8e8"} p="8px 16px" borderRadius="8px">Choose an image
            <Input display={"none"} type="file" accept="image/*" onChange={handleImageUpload} />
          </FormLabel>
        </FormControl>}
        {loading && <Spinner />}
      </VStack>
      <Box mt="16px">
        {(image || previewImage) && <canvas ref={canvasRef} />}
      </Box>
    </>
  );
}

export default ImageUpload;


