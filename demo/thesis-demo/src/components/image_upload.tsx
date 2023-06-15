import { Heading, Input } from "@chakra-ui/react";
import axios from "axios";
import { SetStateAction, useState } from "react";

const ImageUpload = () => {
  const [image, setImage] = useState<FileList | null>(null);
  const [result, setResult] = useState<string | null>(null);

  const handleImageUpload = (event: { target: { files: SetStateAction<FileList | null>[]; }; }) => {
    setImage(event.target.files[0]);
  };

  const handleSubmit = async (event: any) => {
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

        setResult(JSON.stringify(response.data, null, 2));
      } catch (error: any) {
        setResult("Error: " + error.message);
      }
    }
  };

  return (
    <div>
      <Heading>Upload Image</Heading>
      <form onSubmit={handleSubmit}>
        <Input type="file" accept="image/*" onChange={handleImageUpload} />
        <br />
        <Input type="submit" value="Submit" />
      </form>
      <pre>{result}</pre>
    </div>
  );
};

export default ImageUpload;
