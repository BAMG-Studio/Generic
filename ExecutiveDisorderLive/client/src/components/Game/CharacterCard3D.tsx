import React, { useRef, useState } from "react";
import { useFrame, useLoader } from "@react-three/fiber";
import { Text, Plane } from "@react-three/drei";
import * as THREE from "three";

interface CharacterCard3DProps {
  character: any;
  position: [number, number, number];
  isSelected: boolean;
  onSelect: (character: any) => void;
}

export default function CharacterCard3D({
  character,
  position,
  isSelected,
  onSelect
}: CharacterCard3DProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const [textureError, setTextureError] = useState(false);
  
  // Load character portrait texture with error handling
  let texture: THREE.Texture | null = null;
  try {
    texture = useLoader(THREE.TextureLoader, character.portraitUrl, undefined, () => {
      setTextureError(true);
    }) as THREE.Texture;
  } catch (error) {
    setTextureError(true);
  }

  // Animation
  useFrame((state) => {
    if (meshRef.current) {
      // Hover animation
      if (hovered) {
        meshRef.current.position.y = Math.sin(state.clock.elapsedTime * 4) * 0.1 + 0.2;
        meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 2) * 0.05;
      } else {
        meshRef.current.position.y = THREE.MathUtils.lerp(meshRef.current.position.y, 0, 0.1);
        meshRef.current.rotation.y = THREE.MathUtils.lerp(meshRef.current.rotation.y, 0, 0.1);
      }

      // Selected animation
      if (isSelected) {
        meshRef.current.scale.setScalar(1.2 + Math.sin(state.clock.elapsedTime * 3) * 0.05);
      } else {
        const targetScale = hovered ? 1.1 : 1;
        meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.1);
      }
    }
  });

  return (
    <group position={position}>
      {/* Card Base */}
      <mesh
        ref={meshRef}
        onClick={() => onSelect(character)}
        onPointerOver={(e) => {
          setHovered(true);
          document.body.style.cursor = 'pointer';
          e.stopPropagation();
        }}
        onPointerOut={() => {
          setHovered(false);
          document.body.style.cursor = 'auto';
        }}
      >
        <boxGeometry args={[1.5, 2, 0.1]} />
        <meshStandardMaterial 
          color={isSelected ? character.themeColor : '#ffffff'} 
          metalness={0.1}
          roughness={0.2}
        />
      </mesh>

      {/* Character Portrait */}
      <Plane
        args={[1.2, 1.2]}
        position={[0, 0.2, 0.051]}
      >
        {!textureError && texture ? (
          <meshStandardMaterial map={texture} />
        ) : (
          <meshStandardMaterial color={character.themeColor} />
        )}
      </Plane>

      {/* Character Name */}
      <Text
        position={[0, -0.6, 0.051]}
        fontSize={0.15}
        color={isSelected ? '#ffffff' : '#000000'}
        anchorX="center"
        anchorY="middle"
        font="/fonts/inter.json"
        maxWidth={1.4}
      >
        {character.name}
      </Text>

      {/* Stats Display */}
      <group position={[0, -0.9, 0.051]}>
        {Object.entries(character.startingStats).map(([stat, value], index) => (
          <group key={stat} position={[(index - 1.5) * 0.3, 0, 0]}>
            <Text
              position={[0, 0.1, 0]}
              fontSize={0.08}
              color={isSelected ? '#ffffff' : '#333333'}
              anchorX="center"
              anchorY="middle"
              font="/fonts/inter.json"
            >
              {stat.slice(0, 3).toUpperCase()}
            </Text>
            <Text
              position={[0, -0.05, 0]}
              fontSize={0.1}
              color={isSelected ? '#ffffff' : '#000000'}
              anchorX="center"
              anchorY="middle"
              font="/fonts/inter.json"
            >
              {String(value)}
            </Text>
          </group>
        ))}
      </group>

      {/* Selection Indicator */}
      {isSelected && (
        <mesh position={[0, 0, -0.06]}>
          <boxGeometry args={[1.6, 2.1, 0.05]} />
          <meshStandardMaterial color="#fbbf24" emissive="#fbbf24" emissiveIntensity={0.3} />
        </mesh>
      )}
    </group>
  );
}
