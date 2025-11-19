import React, { useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Text } from "@react-three/drei";
import * as THREE from "three";

import ResourceDisplay from "./ResourceDisplay";
import DecisionCard from "./DecisionCard";
import ParticleEffects from "./ParticleEffects";
import { useGameState } from "../../lib/stores/useGameState";
import { useCharacters } from "../../lib/stores/useCharacters";
import { useResources } from "../../lib/stores/useResources";
import { decisionCards } from "../../data/cards.ts";

export default function GameplayScene() {
  const sceneRef = useRef<THREE.Group>(null);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showParticles, setShowParticles] = useState(false);
  
  const { gamePhase, turn, endGame } = useGameState();
  const { selectedCharacter } = useCharacters();
  const { resources, updateResources } = useResources();

  const currentCard = decisionCards[currentCardIndex] || null;

  // Scene rotation animation
  useFrame((state) => {
    if (sceneRef.current) {
      sceneRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.05) * 0.02;
    }
  });

  const handleDecision = (option: any) => {
    console.log('Decision made:', option.text);
    
    // Apply resource changes
    updateResources(option.effects);
    
    // Show particle effects
    setShowParticles(true);
    setTimeout(() => setShowParticles(false), 2000);

    // Move to next card
    const nextIndex = (currentCardIndex + 1) % decisionCards.length;
    setCurrentCardIndex(nextIndex);

    // Check for game end conditions
    const totalResources = Object.values(resources).reduce((sum: number, val: number) => sum + val, 0);
    if (totalResources <= 100 || turn >= 50) {
      setTimeout(() => endGame(), 1000);
    }
  };

  if (!selectedCharacter || !currentCard) {
    return null;
  }

  return (
    <group ref={sceneRef}>
      {/* Background Elements */}
      <mesh position={[0, 0, -10]} scale={[20, 20, 1]}>
        <planeGeometry />
        <meshStandardMaterial color="#1f2937" />
      </mesh>

      {/* Character Display */}
      <group position={[-4, 1, 0]}>
        <mesh>
          <boxGeometry args={[1, 1, 0.1]} />
          <meshStandardMaterial color={selectedCharacter.themeColor} />
        </mesh>
        
        <Text
          position={[0, -0.8, 0]}
          fontSize={0.3}
          color="#ffffff"
          anchorX="center"
          anchorY="middle"
          font="/fonts/inter.json"
        >
          {selectedCharacter.name}
        </Text>
      </group>

      {/* Resource Displays */}
      <ResourceDisplay resources={resources} />

      {/* Current Decision Card */}
      <DecisionCard 
        card={currentCard}
        onDecision={handleDecision}
        position={[0, 0, 0]}
      />

      {/* Turn Counter */}
      <Text
        position={[4, 3, 0]}
        fontSize={0.4}
        color="#ffffff"
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter.json"
      >
        Turn {turn}
      </Text>

      {/* Particle Effects */}
      {showParticles && <ParticleEffects />}
    </group>
  );
}
