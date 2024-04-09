// components/ImageCaption.tsx
interface ImageCaptionProps {
    caption: string;
  }
  
  export default function ImageCaption({ caption }: ImageCaptionProps) {
    return (
      <div className="mt-4">
        <h3 className="text-lg font-bold">Generated Caption:</h3>
        <p>{caption}</p>
      </div>
    );
  }