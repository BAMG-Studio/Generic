import React, { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Text } from "@react-three/drei";
import * as THREE from "three";

interface ResourceDisplayProps {
  resources: {
    popularity: number;
    stability: number;
    media: number;
    economy: number;
  };
}

const resourceConfig: Array<{
  key: string;
  color: string;
  icon: string;
  position: [number, number, number];
}> = [
  { key: 'popularity', color: '#ef4444', icon: '👥', position: [-3, 2.5, 0] },
  { key: 'stability', color: '#3b82f6', icon: '🛡️', position: [-1, 2.5, 0] },
  { key: 'media', color: '#8b5cf6', icon: '📺', position: [1, 2.5, 0] },
  { key: 'economy', color: '#059669', icon: '💰', position: [3, 2.5, 0] }
];

export default function ResourceDisplay({ resources }: ResourceDisplayProps) {
  const groupRef = useRef<THREE.Group>(null);

  // Gentle pulse animation
  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.children.forEach((child, index) => {
        if (child instanceof THREE.Group) {
          const scale = 1 + Math.sin(state.clock.elapsedTime * 2 + index) * 0.05;
          child.scale.setScalar(scale);
        }
      });
    }
  });

  return (
    <group ref={groupRef}>
      {resourceConfig.map((config) => {
        const value = resources[config.key as keyof typeof resources];
        const normalizedHeight = Math.max(0.1, value / 100);
        const barColor = value < 25 ? '#dc2626' : value < 50 ? '#f59e0b' : config.color;

        return (
          <group key={config.key} position={config.position}>
            {/* Background Bar */}
            <mesh position={[0, 0.5, 0]}>
              <boxGeometry args={[0.3, 1, 0.1]} />
              <meshStandardMaterial color="#374151" />
            </mesh>

            {/* Value Bar */}
            <mesh position={[0, normalizedHeight / 2, 0.01]}>
              <boxGeometry args={[0.28, normalizedHeight, 0.08]} />
              <meshStandardMaterial 
                color={barColor} 
                emissive={barColor}
                emissiveIntensity={0.2}
              />
            </mesh>

            {/* Resource Label */}
            <Text
              position={[0, 1.2, 0]}
              fontSize={0.15}
              color="#ffffff"
              anchorX="center"
              anchorY="middle"
              font="/fonts/inter.json"
            >
              {config.key.toUpperCase()}
            </Text>

            {/* Resource Value */}
            <Text
              position={[0, -0.3, 0]}
              fontSize={0.2}
              color="#ffffff"
              anchorX="center"
              anchorY="middle"
              font="/fonts/inter.json"
            >
              {Math.round(value)}
            </Text>

            {/* Icon */}
            <Text
              position={[0, 1.5, 0]}
              fontSize={0.3}
              anchorX="center"
              anchorY="middle"
            >
              {config.icon}
            </Text>
          </group>
        );
      })}
    </group>
  );
}
