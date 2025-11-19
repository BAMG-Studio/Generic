import React, { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { Text } from "@react-three/drei";
import * as THREE from "three";

import CharacterCard3D from "./CharacterCard3D";
import { useCharacters } from "../../lib/stores/useCharacters";
import { useGameState } from "../../lib/stores/useGameState";
import { characters } from "../../data/characters";

export default function CharacterSelection() {
  const groupRef = useRef<THREE.Group>(null);
  const { selectedCharacter, setSelectedCharacter } = useCharacters();
  const { setGamePhase } = useGameState();

  // Calculate positions for character cards in a grid
  const cardPositions = useMemo(() => {
    const positions = [];
    const cols = 5;
    const rows = 2;
    const spacing = 3;
    
    for (let i = 0; i < characters.length; i++) {
      const col = i % cols;
      const row = Math.floor(i / cols);
      const x = (col - (cols - 1) / 2) * spacing;
      const z = (row - (rows - 1) / 2) * spacing;
      positions.push([x, 0, z]);
    }
    return positions;
  }, []);

  // Gentle rotation animation
  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.1) * 0.05;
    }
  });

  const handleCharacterSelect = (character: any) => {
    setSelectedCharacter(character);
    console.log('Selected character:', character.name);
  };

  const handleStartGame = () => {
    if (selectedCharacter) {
      console.log('Starting game with:', selectedCharacter.name);
      setGamePhase('playing');
    }
  };

  return (
    <group ref={groupRef}>
      {/* Title */}
      <Text
        position={[0, 4, 0]}
        fontSize={1}
        color="#ffffff"
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter.json"
      >
        Choose Your Leader
      </Text>

      {/* Character Cards */}
      {characters.map((character, index) => (
        <CharacterCard3D
          key={character.id}
          character={character}
          position={cardPositions[index] as [number, number, number]}
          isSelected={selectedCharacter?.id === character.id}
          onSelect={handleCharacterSelect}
        />
      ))}

      {/* Selected Character Details */}
      {selectedCharacter && (
        <group position={[0, -2, 0]}>
          <Text
            position={[0, 0.5, 0]}
            fontSize={0.6}
            color="#ffffff"
            anchorX="center"
            anchorY="middle"
            font="/fonts/inter.json"
          >
            {selectedCharacter.name}
          </Text>
          
          <Text
            position={[0, 0, 0]}
            fontSize={0.3}
            color="#cccccc"
            anchorX="center"
            anchorY="middle"
            maxWidth={10}
            font="/fonts/inter.json"
          >
            {selectedCharacter.shortBio}
          </Text>

          {/* Start Button */}
          <mesh
            position={[0, -1, 0]}
            onClick={handleStartGame}
            onPointerOver={(e) => {
              e.object.scale.setScalar(1.1);
              document.body.style.cursor = 'pointer';
            }}
            onPointerOut={(e) => {
              e.object.scale.setScalar(1);
              document.body.style.cursor = 'auto';
            }}
          >
            <boxGeometry args={[2, 0.5, 0.1]} />
            <meshStandardMaterial color="#059669" />
          </mesh>
          
          <Text
            position={[0, -1, 0.06]}
            fontSize={0.3}
            color="#ffffff"
            anchorX="center"
            anchorY="middle"
            font="/fonts/inter.json"
          >
            Start Campaign
          </Text>
        </group>
      )}
    </group>
  );
}
