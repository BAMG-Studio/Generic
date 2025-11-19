import React, { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

export default function ParticleEffects() {
  const meshRef = useRef<THREE.Points>(null);
  
  // Create particles
  const particles = useMemo(() => {
    const particleCount = 100;
    const positions = new Float32Array(particleCount * 3);
    const velocities = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      
      // Random positions around origin
      positions[i3] = (Math.random() - 0.5) * 10;
      positions[i3 + 1] = (Math.random() - 0.5) * 10;
      positions[i3 + 2] = (Math.random() - 0.5) * 5;

      // Random velocities
      velocities[i3] = (Math.random() - 0.5) * 0.02;
      velocities[i3 + 1] = Math.random() * 0.02;
      velocities[i3 + 2] = (Math.random() - 0.5) * 0.02;

      // Random colors (gold/yellow theme)
      colors[i3] = 1; // R
      colors[i3 + 1] = 0.8 + Math.random() * 0.2; // G
      colors[i3 + 2] = 0.2; // B
    }

    return { positions, velocities, colors, count: particleCount };
  }, []);

  // Animate particles
  useFrame(() => {
    if (meshRef.current && meshRef.current.geometry) {
      const positions = meshRef.current.geometry.attributes.position.array as Float32Array;
      
      for (let i = 0; i < particles.count; i++) {
        const i3 = i * 3;
        
        // Update positions
        positions[i3] += particles.velocities[i3];
        positions[i3 + 1] += particles.velocities[i3 + 1];
        positions[i3 + 2] += particles.velocities[i3 + 2];

        // Reset particles that go too far
        if (positions[i3 + 1] > 5) {
          positions[i3] = (Math.random() - 0.5) * 10;
          positions[i3 + 1] = -5;
          positions[i3 + 2] = (Math.random() - 0.5) * 5;
        }
      }
      
      meshRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particles.count}
          array={particles.positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={particles.count}
          array={particles.colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.1}
        vertexColors
        transparent
        opacity={0.8}
        sizeAttenuation
      />
    </points>
  );
}
