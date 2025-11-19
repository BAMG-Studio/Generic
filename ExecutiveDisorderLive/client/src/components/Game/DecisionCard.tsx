import React, { useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Text } from "@react-three/drei";
import * as THREE from "three";

interface DecisionCardProps {
  card: any;
  onDecision: (option: any) => void;
  position: [number, number, number];
}

export default function DecisionCard({ card, onDecision, position }: DecisionCardProps) {
  const cardRef = useRef<THREE.Group>(null);
  const [hoveredOption, setHoveredOption] = useState<number | null>(null);

  // Card floating animation
  useFrame((state) => {
    if (cardRef.current) {
      cardRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime) * 0.1;
      cardRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.5) * 0.02;
    }
  });

  const handleOptionClick = (option: any, index: number) => {
    console.log(`Selected option ${index + 1}:`, option.text);
    onDecision(option);
  };

  return (
    <group ref={cardRef} position={position}>
      {/* Card Background */}
      <mesh>
        <boxGeometry args={[4, 5, 0.1]} />
        <meshStandardMaterial 
          color="#1f2937" 
          metalness={0.1} 
          roughness={0.8}
        />
      </mesh>

      {/* Card Border */}
      <mesh position={[0, 0, 0.01]}>
        <boxGeometry args={[4.1, 5.1, 0.05]} />
        <meshStandardMaterial color="#374151" />
      </mesh>

      {/* Card Title */}
      <Text
        position={[0, 2, 0.06]}
        fontSize={0.3}
        color="#ffffff"
        anchorX="center"
        anchorY="middle"
        maxWidth={3.5}
        font="/fonts/inter.json"
      >
        {card.title}
      </Text>

      {/* Card Description */}
      <Text
        position={[0, 1, 0.06]}
        fontSize={0.2}
        color="#d1d5db"
        anchorX="center"
        anchorY="middle"
        maxWidth={3.5}
        font="/fonts/inter.json"
      >
        {card.description}
      </Text>

      {/* Decision Options */}
      {card.options.map((option: any, index: number) => {
        const yPos = 0.2 - (index * 0.8);
        const isHovered = hoveredOption === index;
        
        return (
          <group key={index}>
            {/* Option Button */}
            <mesh
              position={[0, yPos, 0.06]}
              onClick={() => handleOptionClick(option, index)}
              onPointerOver={(e) => {
                setHoveredOption(index);
                document.body.style.cursor = 'pointer';
                e.stopPropagation();
              }}
              onPointerOut={() => {
                setHoveredOption(null);
                document.body.style.cursor = 'auto';
              }}
            >
              <boxGeometry args={[3.5, 0.6, 0.05]} />
              <meshStandardMaterial 
                color={isHovered ? "#374151" : "#111827"}
                emissive={isHovered ? "#1f2937" : "#000000"}
                emissiveIntensity={0.1}
              />
            </mesh>

            {/* Option Text */}
            <Text
              position={[0, yPos, 0.09]}
              fontSize={0.15}
              color={isHovered ? "#ffffff" : "#d1d5db"}
              anchorX="center"
              anchorY="middle"
              maxWidth={3.2}
              font="/fonts/inter.json"
            >
              {option.text}
            </Text>

            {/* Effects Preview */}
            <group position={[0, yPos - 0.2, 0.09]}>
              {Object.entries(option.effects).map(([resource, value], effectIndex) => {
                const effectColor = (value as number) > 0 ? "#10b981" : "#ef4444";
                const effectSign = (value as number) > 0 ? "+" : "";
                
                return (
                  <Text
                    key={resource}
                    position={[(effectIndex - 1.5) * 0.8, 0, 0]}
                    fontSize={0.1}
                    color={effectColor}
                    anchorX="center"
                    anchorY="middle"
                    font="/fonts/inter.json"
                  >
                    {`${resource.slice(0, 3)}: ${effectSign}${value}`}
                  </Text>
                );
              })}
            </group>
          </group>
        );
      })}
    </group>
  );
}
