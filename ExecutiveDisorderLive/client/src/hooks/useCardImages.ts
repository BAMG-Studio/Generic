import { useState, useEffect } from "react";

// Map of card themes to available backgrounds/images
const CARD_IMAGE_THEMES = {
  economic: {
    gradient: "from-green-600 to-green-900",
    icon: "💰",
    images: [
      "/images/backgrounds/economic-1.jpg",
      "/images/backgrounds/market.jpg",
      "/images/backgrounds/wall-street.jpg"
    ]
  },
  foreign: {
    gradient: "from-blue-600 to-blue-900",
    icon: "🌍",
    images: [
      "/images/backgrounds/diplomacy.jpg",
      "/images/backgrounds/world-map.jpg",
      "/images/backgrounds/un-assembly.jpg"
    ]
  },
  domestic: {
    gradient: "from-purple-600 to-purple-900",
    icon: "🏛️",
    images: [
      "/images/backgrounds/capitol.jpg",
      "/images/backgrounds/white-house.jpg",
      "/images/backgrounds/congress.jpg"
    ]
  },
  social: {
    gradient: "from-pink-600 to-pink-900",
    icon: "👥",
    images: [
      "/images/backgrounds/crowd.jpg",
      "/images/backgrounds/protest.jpg",
      "/images/backgrounds/social-media.jpg"
    ]
  },
  crisis: {
    gradient: "from-red-600 to-red-900",
    icon: "🚨",
    images: [
      "/images/backgrounds/crisis.jpg",
      "/images/backgrounds/emergency.jpg",
      "/images/backgrounds/breaking-news.jpg"
    ]
  },
  scandal: {
    gradient: "from-orange-600 to-orange-900",
    icon: "📰",
    images: [
      "/images/backgrounds/scandal.jpg",
      "/images/backgrounds/newspaper.jpg",
      "/images/backgrounds/media-frenzy.jpg"
    ]
  }
};

// Fallback gradient generators based on card ID/title
function generateCardGradient(cardId: string, category: string): string {
  const theme = CARD_IMAGE_THEMES[category as keyof typeof CARD_IMAGE_THEMES];
  if (theme) {
    return theme.gradient;
  }
  
  // Generate a consistent gradient based on card ID
  const hash = cardId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const hue1 = (hash * 137) % 360;
  const hue2 = (hue1 + 60) % 360;
  
  return `from-[hsl(${hue1},70%,50%)] to-[hsl(${hue2},70%,30%)]`;
}

interface CardImageData {
  imageUrl?: string;
  gradient: string;
  icon: string;
  isLoading: boolean;
  error?: string;
}

export function useCardImages(cardId: string, category: string, imageUrl?: string): CardImageData {
  const [imageData, setImageData] = useState<CardImageData>({
    gradient: generateCardGradient(cardId, category),
    icon: CARD_IMAGE_THEMES[category as keyof typeof CARD_IMAGE_THEMES]?.icon || "🎭",
    isLoading: false
  });
  
  useEffect(() => {
    // If we have a direct image URL, try to load it
    if (imageUrl) {
      setImageData(prev => ({ ...prev, isLoading: true }));
      
      const img = new Image();
      img.onload = () => {
        setImageData(prev => ({
          ...prev,
          imageUrl,
          isLoading: false
        }));
      };
      img.onerror = () => {
        setImageData(prev => ({
          ...prev,
          isLoading: false,
          error: "Failed to load image"
        }));
      };
      img.src = imageUrl;
    }
  }, [imageUrl]);
  
  return imageData;
}

// Hook to preload and manage all card images
export function usePreloadCardImages(cards: Array<{ id: string; category: string; imageUrl?: string }>) {
  const [loadedImages, setLoadedImages] = useState<Map<string, string>>(new Map());
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const loadImages = async () => {
      const imageMap = new Map<string, string>();
      const promises: Promise<void>[] = [];
      
      for (const card of cards) {
        if (card.imageUrl) {
          const promise = new Promise<void>((resolve) => {
            const img = new Image();
            img.onload = () => {
              imageMap.set(card.id, card.imageUrl as string);
              resolve();
            };
            img.onerror = () => {
              // If image fails to load, we'll use gradient fallback
              resolve();
            };
            img.src = card.imageUrl || "";
          });
          promises.push(promise);
        }
      }
      
      await Promise.all(promises);
      setLoadedImages(imageMap);
      setIsLoading(false);
    };
    
    loadImages();
  }, [cards]);
  
  return { loadedImages, isLoading };
}