// api.ts
import axios from 'axios';

const API_URL = 'https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning';
const headers = { Authorization: `Bearer ${process.env.HUGGINGFACE_API_KEY}` };

export async function generateCaption(imageFile: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', imageFile);
  console.log('FormData:', formData.get('file')); // Log the appended file
  try {
    const response = await axios.post(API_URL, formData, { headers });
    return response.data[0].generated_text;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('API Error:', error.response?.data);
      throw new Error('Failed to generate caption. Please try again.');
    } else {
      console.error('Unknown Error:', error);
      throw new Error('An unknown error occurred. Please try again.');
    }
  }
}