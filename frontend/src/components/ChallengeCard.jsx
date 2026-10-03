import React from 'react';
import { Link } from 'react-router-dom';
import { Globe, Key, Search, FileText, Network, Terminal, CheckCircle2, ArrowRight } from 'lucide-react';

export default function ChallengeCard({ challenge }) {
  const getCategoryIcon = (category) => {
    const catLower = (category || '').toLowerCase();
    if (catLower.includes('web')) return <Globe size={20} color="#06b6d4" />;
    if (catLower.includes('crypto')) return <Key size={20} color="#8b5cf6" />;
    if (catLower.includes('forensics')) return <FileText size={20} color="#f59e0b" />;
    if (catLower.includes('network')) return <Network size={20} color="#10b981" />;
    if (catLower.includes('linux')) return <Terminal size={20} color="#ec4899" />;
    return <Search size={20} color="#3b82f6" />;
  };

  const getDifficultyBadge = (difficulty) => {
    const diff = (difficulty || '').toLowerCase();
    if (diff === 'easy') return <span className="badge badge-easy">Easy</span>;
    if (diff === 'medium') return <span className="badge badge-medium">Medium</span>;
    return <span className="badge badge-hard">Hard</span>;
  };

  return (
    <div className="cq-card" style={{
      display: 'flex',
      flexDirection: 'column',
      justify: 'space-between',
      position: 'relative',
      height: '100%',
      border: challenge.is_solved ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid #1e293b',
      background: challenge.is_solved ? 'linear-gradient(180deg, rgba(16, 185, 129, 0.05) 0%, #111726 100%)' : '#111726'
    }}>
      <div>
        {/* Card Header: Category Icon + Badges */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              background: '#1b2438',
              padding: '8px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center'
            }}>
              {getCategoryIcon(challenge.category)}
            </div>
            <span className="badge badge-category">{challenge.category}</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {getDifficultyBadge(challenge.difficulty)}
            {challenge.is_solved && (
              <span className="badge badge-solved" title="Solved">
                <CheckCircle2 size={12} /> Solved
              </span>
            )}
          </div>
        </div>

        {/* Challenge Title */}
        <h3 style={{ fontSize: '1.2rem', marginBottom: '10px', color: '#ffffff' }}>
          {challenge.title}
        </h3>

        {/* Description */}
        <p style={{
          color: '#94a3b8',
          fontSize: '0.9rem',
          lineHeight: '1.5',
          marginBottom: '20px',
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden'
        }}>
          {challenge.description}
        </p>
      </div>

      {/* Card Footer: Points & Open Button */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justify: 'space-between',
        paddingTop: '16px',
        borderTop: '1px solid #1e293b'
      }}>
        <div style={{
          fontFamily: "'Fira Code', monospace",
          fontSize: '1rem',
          fontWeight: 700,
          color: '#10b981'
        }}>
          {challenge.points} <span style={{ fontSize: '0.8rem', color: '#64748b' }}>PTS</span>
        </div>

        <Link to={`/challenges/${challenge.id}`} className={challenge.is_solved ? "btn btn-outline" : "btn btn-primary"} style={{ padding: '8px 14px', fontSize: '0.85rem' }}>
          {challenge.is_solved ? 'REVIEW' : 'OPEN CHALLENGE'}
          <ArrowRight size={14} />
        </Link>
      </div>
    </div>
  );
}
