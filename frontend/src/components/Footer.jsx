import React from 'react';
import { Terminal, Shield, Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer style={{
      background: '#070a12',
      borderTop: '1px solid #1e293b',
      padding: '40px 20px 30px',
      color: '#64748b',
      fontSize: '0.9rem'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ color: '#10b981', display: 'flex', alignItems: 'center' }}>
            <Terminal size={20} />
          </div>
          <span style={{ color: '#ffffff', fontWeight: 700, fontFamily: "'Outfit', sans-serif" }}>
            CYBER<span style={{ color: '#10b981' }}>QUEST</span>
          </span>
          <span style={{ margin: '0 8px' }}>|</span>
          <span>Beginner-Friendly Cybersecurity & CTF Platform</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <span>Designed for Cybersecurity Learning & Hands-On Practice</span>
        </div>

        <div style={{ width: '100%', borderTop: '1px solid #1e293b', marginTop: '20px', paddingTop: '20px', textAlign: 'center', fontSize: '0.85rem' }}>
          &copy; {new Date().getFullYear()} CyberQuest Platform. All security challenges hosted in safe isolated environments.
        </div>
      </div>
    </footer>
  );
}
