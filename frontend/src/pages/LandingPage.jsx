import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Terminal, Shield, Award, Users, ArrowRight, Flag, Cpu } from 'lucide-react';
import { api } from '../services/api';

export default function LandingPage() {
  const [stats, setStats] = useState({
    challenges: 5,
    categories: 6,
    totalPoints: 1000,
    players: 0
  });

  useEffect(() => {
    // Fetch live challenge stats
    api.getChallenges()
      .then(res => {
        if (res.challenges) {
          const totalPts = res.challenges.reduce((acc, c) => acc + c.points, 0);
          const uniqueCats = new Set(res.challenges.map(c => c.category)).size;
          setStats(prev => ({
            ...prev,
            challenges: res.challenges.length,
            categories: Math.max(2, uniqueCats),
            totalPoints: totalPts
          }));
        }
      })
      .catch(() => {});
      
    api.getLeaderboard()
      .then(res => {
        if (res.leaderboard) {
          setStats(prev => ({ ...prev, players: res.leaderboard.length }));
        }
      })
      .catch(() => {});
  }, []);

  const workflowSteps = [
    { num: '1', title: 'Choose a Challenge', desc: 'Select a task by category or difficulty level based on your cybersecurity skill set.' },
    { num: '2', title: 'Investigate the Target', desc: 'Inspect web pages, decode ciphers, analyze packet captures, or test isolated lab containers.' },
    { num: '3', title: 'Find the Flag', desc: 'Discover hidden flag strings formatted as CTF{secret_key_here}.' },
    { num: '4', title: 'Submit the Flag', desc: 'Enter the captured flag into CyberQuest to validate your solution.' },
    { num: '5', title: 'Earn Points', desc: 'Gain points, climb the live global leaderboard, and track your learning progress.' }
  ];

  return (
    <div className="page-container animate-fade-in" style={{ padding: '40px 20px 80px' }}>
      {/* HERO SECTION */}
      <section style={{ textAlign: 'center', margin: '40px 0 80px' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: '#10b981',
          padding: '6px 16px',
          borderRadius: '20px',
          fontSize: '0.85rem',
          fontWeight: 600,
          marginBottom: '24px'
        }}>
          <Terminal size={16} /> Beginner-Friendly Cybersecurity Training Platform
        </div>

        <h1 style={{
          fontSize: '3.8rem',
          fontWeight: 800,
          lineHeight: 1.1,
          marginBottom: '16px',
          fontFamily: "'Outfit', sans-serif"
        }}>
          CYBER<span style={{ color: '#10b981' }}>QUEST</span>
        </h1>

        <h2 style={{
          fontSize: '1.6rem',
          color: '#34d399',
          fontWeight: 600,
          marginBottom: '20px',
          fontFamily: "'Outfit', sans-serif"
        }}>
          Learn. Hack. Capture the Flag.
        </h2>

        <p style={{
          maxWidth: '650px',
          margin: '0 auto 36px',
          fontSize: '1.15rem',
          color: '#94a3b8',
          lineHeight: '1.6'
        }}>
          Practice cybersecurity through hands-on challenges, discover real-world vulnerabilities, and capture hidden flags in a safe interactive platform.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <Link to="/challenges" className="btn btn-primary" style={{ padding: '14px 32px', fontSize: '1.05rem' }}>
            <Flag size={20} /> Start Hacking
          </Link>
          <Link to="/challenges" className="btn btn-secondary" style={{ padding: '14px 28px', fontSize: '1.05rem' }}>
            Explore Challenges <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      {/* STATISTICS SECTION */}
      <section style={{ marginBottom: '90px' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '20px'
        }}>
          <div className="cq-card" style={{ textAlign: 'center', padding: '30px 20px' }}>
            <div style={{ color: '#10b981', marginBottom: '10px', display: 'flex', justifyContent: 'center' }}>
              <Shield size={32} />
            </div>
            <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#ffffff', fontFamily: "'Outfit', sans-serif" }}>
              {stats.challenges}
            </div>
            <div style={{ color: '#94a3b8', fontSize: '0.95rem', marginTop: '4px' }}>Active Challenges</div>
          </div>

          <div className="cq-card" style={{ textAlign: 'center', padding: '30px 20px' }}>
            <div style={{ color: '#06b6d4', marginBottom: '10px', display: 'flex', justifyContent: 'center' }}>
              <Cpu size={32} />
            </div>
            <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#ffffff', fontFamily: "'Outfit', sans-serif" }}>
              {stats.categories}
            </div>
            <div style={{ color: '#94a3b8', fontSize: '0.95rem', marginTop: '4px' }}>Categories</div>
          </div>

          <div className="cq-card" style={{ textAlign: 'center', padding: '30px 20px' }}>
            <div style={{ color: '#f59e0b', marginBottom: '10px', display: 'flex', justifyContent: 'center' }}>
              <Award size={32} />
            </div>
            <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#ffffff', fontFamily: "'Outfit', sans-serif" }}>
              {stats.totalPoints}
            </div>
            <div style={{ color: '#94a3b8', fontSize: '0.95rem', marginTop: '4px' }}>Total Points</div>
          </div>

          <div className="cq-card" style={{ textAlign: 'center', padding: '30px 20px' }}>
            <div style={{ color: '#8b5cf6', marginBottom: '10px', display: 'flex', justifyContent: 'center' }}>
              <Users size={32} />
            </div>
            <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#ffffff', fontFamily: "'Outfit', sans-serif" }}>
              {stats.players}
            </div>
            <div style={{ color: '#94a3b8', fontSize: '0.95rem', marginTop: '4px' }}>Registered Players</div>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS SECTION */}
      <section>
        <div style={{ textAlign: 'center', marginBottom: '50px' }}>
          <h2 style={{ fontSize: '2.2rem', fontWeight: 700, marginBottom: '12px' }}>How It Works</h2>
          <p style={{ color: '#94a3b8', fontSize: '1.05rem', maxWidth: '600px', margin: '0 auto' }}>
            Follow five straightforward steps to capture your first flag and gain hands-on security experience.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '20px',
          position: 'relative'
        }}>
          {workflowSteps.map((step, idx) => (
            <div key={idx} className="cq-card" style={{ textAlign: 'center', padding: '24px 16px', position: 'relative' }}>
              <div style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                background: 'rgba(16, 185, 129, 0.15)',
                border: '2px solid #10b981',
                color: '#10b981',
                fontWeight: 800,
                fontSize: '1.2rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px',
                fontFamily: "'Fira Code', monospace"
              }}>
                {step.num}
              </div>
              <h4 style={{ fontSize: '1.05rem', marginBottom: '8px', color: '#ffffff' }}>{step.title}</h4>
              <p style={{ color: '#94a3b8', fontSize: '0.88rem', lineHeight: '1.5' }}>{step.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
