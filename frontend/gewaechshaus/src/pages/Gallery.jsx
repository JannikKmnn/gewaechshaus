import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

export default function Gallery() {
  const [fullScreenImage, setFullScreenImage] = useState(null);
  const [images, setImages] = useState([]);

  function loadImages() {
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

  function moveFullScreen(direction) {
    var curr_idx = images.indexOf(fullScreenImage);
    if (direction == "next") {
      setFullScreenImage(images[curr_idx + 1]);
    } else {
      setFullScreenImage(images[curr_idx - 1]);
    }
  }

  useEffect(() => {
    loadImages();
  }, []);

  return (
    <div>
      <div className="gallery">
        {images.map((image) => (
          <div
            className="gallery-item"
            key={image.path}
            onClick={() => setFullScreenImage(image)}
          >
            <img src={image.src} alt="" loading="lazy" decoding="async" />
          </div>
        ))}
      </div>

      {fullScreenImage && (
        <div
          onClick={() => setFullScreenImage(null)}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 1000,
            backgroundColor: "rgba(0, 0, 0, 0.8)",

            display: "flex",
            alignItems: "center",
            justifyContent: "center",

            padding: "10px",
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "10% 1fr 10%",
              gap: "20px",
            }}
          >
            {images.indexOf(fullScreenImage) !== 0 ? (
              <button
                className="gallery-chevron"
                style={{
                  fontSize: "50px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: 0,
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  moveFullScreen("prev");
                }}
              >
                <ChevronLeft />
              </button>
            ) : (
              <div></div>
            )}

            <img
              src={fullScreenImage.src}
              alt=""
              onClick={(e) => e.stopPropagation()}
              style={{
                maxWidth: "95vw",
                maxHeight: "95vh",
                width: "auto",
                height: "auto",
                objectFit: "contain",

                borderRadius: "10px",
                boxShadow: "0 8px 40px rgba(0, 0, 0, 0.5)",
              }}
            />
            {images.indexOf(fullScreenImage) !== images.length - 1 ? (
              <button
                className="gallery-chevron"
                style={{
                  fontSize: "50px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: 0,
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  moveFullScreen("next");
                }}
              >
                <ChevronRight />
              </button>
            ) : (
              <div></div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
