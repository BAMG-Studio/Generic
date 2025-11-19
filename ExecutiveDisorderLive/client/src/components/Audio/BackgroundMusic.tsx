import { useEffect, useRef } from 'react';

export default function BackgroundMusic() {
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    // Create audio element
    audioRef.current = new Audio('/sounds/background.mp3');
    audioRef.current.loop = true;
    audioRef.current.volume = 0.3;

    // Start playing on user interaction
    const startMusic = () => {
      if (audioRef.current) {
        audioRef.current.play().catch(console.error);
        // Remove listener after first interaction
        document.removeEventListener('click', startMusic);
      }
    };

    // Add listener for first user interaction
    document.addEventListener('click', startMusic);

    // Cleanup
    return () => {
      document.removeEventListener('click', startMusic);
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  return null;
}