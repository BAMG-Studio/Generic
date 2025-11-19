import React, { useEffect, useRef } from "react";

interface AudioSystemProps {
  muted?: boolean;
  musicTrack?: string; // Optional background music track
}

export default function AudioSystem({ muted = false, musicTrack }: AudioSystemProps) {
  const musicRef = useRef<HTMLAudioElement | null>(null);
  
  // Background music player
  useEffect(() => {
    if (muted || !musicTrack) return;
    
    const playMusic = async () => {
      try {
        if (musicRef.current) {
          musicRef.current.pause();
        }
        
        const music = new Audio(musicTrack);
        music.volume = 0.3;
        music.loop = true;
        musicRef.current = music;
        
        await music.play();
      } catch (error) {
        console.log("Music playback skipped:", error);
      }
    };
    
    playMusic();
  }, [musicTrack, muted]);
  
  // Cleanup
  useEffect(() => {
    return () => {
      if (musicRef.current) {
        musicRef.current.pause();
        musicRef.current = null;
      }
    };
  }, []);
  
  return null; // This is a non-visual component
}

// Hook for playing UI sounds and effects only (NO voice/narration)
export function usePlayAudio() {
  const playEffect = async (effectName: string, volume: number = 0.5) => {
    try {
      const audio = new Audio(`/audio/sfx/${effectName}.mp3`);
      audio.volume = volume;
      await audio.play();
      return audio;
    } catch (error) {
      console.error("Failed to play effect:", error);
      return null;
    }
  };
  
  const playUISound = async (soundName: string, volume: number = 0.4) => {
    try {
      const audio = new Audio(`/audio/ui/${soundName}.mp3`);
      audio.volume = volume;
      await audio.play();
      return audio;
    } catch (error) {
      console.error("Failed to play UI sound:", error);
      return null;
    }
  };
  
  const playMusic = async (musicName: string, volume: number = 0.3, loop: boolean = true) => {
    try {
      const audio = new Audio(`/audio/music/${musicName}.mp3`);
      audio.volume = volume;
      audio.loop = loop;
      await audio.play();
      return audio;
    } catch (error) {
      console.error("Failed to play music:", error);
      return null;
    }
  };
  
  return { playEffect, playUISound, playMusic };
}