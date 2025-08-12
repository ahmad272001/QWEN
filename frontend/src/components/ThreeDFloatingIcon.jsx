import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Float, meshBounds } from '@react-three/drei';
import { useRef } from 'react';

function FloatingIcon({ onClick }) {
  const meshRef = useRef();
  useFrame((state) => {
    meshRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.5) * 0.2;
    meshRef.current.rotation.y = state.clock.elapsedTime * 0.15;
  });

  return (
    <Float speed={2} rotationIntensity={0.8} floatIntensity={0.5}>
      <mesh
        ref={meshRef}
        onClick={onClick}
        scale={1.3}
        onPointerOver={() => (document.body.style.cursor = 'pointer')}
        onPointerOut={() => (document.body.style.cursor = 'default')}
      >
        <torusKnotGeometry args={[0.5, 0.15, 128, 16]} />
        <meshStandardMaterial color="#6a3dff" metalness={1} roughness={0.2} />
      </mesh>
    </Float>
  );
}

export default function ThreeDFloatingChat({ onOpen }) {
  return (
    <div
      style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        width: '120px',
        height: '120px',
        zIndex: 1000,
        cursor: 'pointer',
      }}
    >
      <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <FloatingIcon onClick={onOpen} />
        <OrbitControls enabled={false} />
      </Canvas>
    </div>
  );
}