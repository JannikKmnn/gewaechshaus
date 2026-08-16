import { useEffect, useState } from "react";

export default function Gallery() {
  const [scrollModeActive, setscrollModeActive] = useState(false);
  const [images, setImages] = useState([]);

  async function loadImages() {
    const galleryImages = import.meta.glob("../assets/gallery/*.{jpg,png}", {
      eager: true,
      import: "default",
    });

    const imagesObjects = Object.entries(galleryImages).map(([path, src]) => ({
      path,
      src,
    }));

    setImages(imagesObjects);
  }

  useEffect(() => {
    loadImages();
  }, []);

  return (
    <div className="gallery">
      {images.map((image) => (
        <div className="gallery-item" key={image.path}>
          <img src={image.src} alt="" loading="lazy" decoding="async" />
        </div>
      ))}
    </div>
  );
}
