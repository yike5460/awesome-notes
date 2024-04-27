// pages/index.tsx
import { useState } from 'react';
import ImageUploader from '../components/ImageUploader';
import ImageCaption from '../components/ImageCaption';
import { HTMLSketleton } from '../components/HTML';
import { generateCaption } from '../api';

export default function Home() {
  const [caption, setCaption] = useState('');

  const handleImageUpload = async (file: File) => {
    const generatedCaption = await generateCaption(file);
    setCaption(generatedCaption);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Image Caption Generator</h1>
      <ImageUploader onImageUpload={handleImageUpload} />
      {caption && <ImageCaption caption={caption} />}

      <HTMLSketleton />
    </div>
  );
}