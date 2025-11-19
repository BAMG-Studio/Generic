import React, { useEffect } from "react";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";

import CharacterSelection from "./CharacterSelection";
import GameplayScene from "./GameplayScene";
import { useGameState } from "../../lib/stores/useGameState";

export default function GameCanvas() {
  const { scene } = useThree();
  const { gamePhase, timeOfDay } = useGameState();

  // Setup lighting
  useEffect(() => {
    // Clear existing lights
    const lights = scene.children.filter(child => child instanceof THREE.Light);
    lights.forEach(light => scene.remove(light));

    // Ambient light
    const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);

    // Directional light (main light)
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 5);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);

    // Additional fill light
    const fillLight = new THREE.DirectionalLight(0x87ceeb, 0.3);
    fillLight.position.set(-5, 5, -5);
    scene.add(fillLight);

    return () => {
      scene.remove(ambientLight);
      scene.remove(directionalLight);
      scene.remove(fillLight);
    };
  }, [scene, timeOfDay]);

  // Background color based on time of day
  useEffect(() => {
    let bgColor;
    switch (timeOfDay) {
      case 'morning':
        bgColor = '#87ceeb';
        break;
      case 'afternoon':
        bgColor = '#4682b4';
        break;
      case 'night':
        bgColor = '#191970';
        break;
      default:
        bgColor = '#111827';
    }
    scene.background = new THREE.Color(bgColor);
  }, [scene, timeOfDay]);

  return (
    <>
      {gamePhase === 'character_selection' && <CharacterSelection />}
      {gamePhase === 'playing' && <GameplayScene />}
    </>
  );
}
