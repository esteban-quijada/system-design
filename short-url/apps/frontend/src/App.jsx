import { useEffect, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import ParticleScene from "./components/ParticleScene";
import ShortenForm from "./components/ShortenForm";
import StatsPanel from "./components/StatsPanel";

export default function App() {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      {/* Fixed Three.js canvas behind all content */}
      <div style={{ position: "fixed", inset: 0, zIndex: 0 }}>
        <Canvas camera={{ position: [0, 0, 8], fov: 75 }}>
          <ParticleScene scrollY={scrollY} />
        </Canvas>
      </div>

      {/* Scrollable content on top */}
      <div style={{ position: "relative", zIndex: 1 }}>
        {/* Hero section */}
        <section id="hero" style={{ position: "relative" }}>
          <div style={{ textAlign: "center" }}>
            <h1>URL Shortener</h1>
            <p className="subtitle">
              Shorten links. Track clicks. Built on Kubernetes.
            </p>
            <a href="#shorten">
              <button style={{ width: "auto", padding: "0.85rem 2rem" }}>
                Get Started
              </button>
            </a>
          </div>
          <p className="scroll-hint">↓ scroll</p>
        </section>

        <ShortenForm />
        <StatsPanel />
      </div>
    </>
  );
}
