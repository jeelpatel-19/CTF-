import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Trophy, Award, CheckCircle2, User, ShieldAlert, Clock } from 'lucide-react';

export default function LeaderboardPage() {
  const { user } = useAuth();
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getLeaderboard()
      .then(res => {
        setLeaderboard(res.leaderboard || []);
      })
      .catch(err => {
        console.error('Failed to load leaderboard', err);
      })
      .finally(() => setLoading(false));
  }, []);

  const getRankBadge = (rank) => {
    if (rank === 1) return <span style={{ fontSize: '1.2rem' }}>🥇</span>;
    if (rank === 2) return <span style={{ fontSize: '1.2rem' }}>🥈</span>;
    if (rank === 3) return <span style={{ fontSize: '1.2rem' }}>🥉</span>;
    return <span style={{ fontFamily: "'Fira Code', monospace", fontWeight: 700, color: '#94a3b8' }}>#{rank}</span>;
  };

  const formatSolveTime = (totalSeconds) => {
    if (totalSeconds === null || totalSeconds === undefined || totalSeconds <= 0) return '00:00';
    const hrs = Math.floor(totalSeconds / 3600);
    const mins = Math.floor((totalSeconds % 3600) / 60);
    const secs = totalSeconds % 60;

    const pad = (num) => String(num).padStart(2, '0');
    if (hrs > 0) {
      return `${pad(hrs)}:${pad(mins)}:${pad(secs)}`;
    }
    return `${pad(mins)}:${pad(secs)}`;
  };

  return (
    <div className="page-container animate-fade-in" style={{ padding: '30px 20px 80px' }}>
      {/* Title */}
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <div style={{
          display: 'inline-flex',
          background: 'rgba(245, 158, 11, 0.15)',
          border: '1px solid #f59e0b',
          padding: '10px',
          borderRadius: '50%',
          color: '#f59e0b',
          marginBottom: '16px'
        }}>
          <Trophy size={32} />
        </div>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '10px' }}>Global Leaderboard</h1>
        <p style={{ color: '#94a3b8', fontSize: '1.05rem', maxWidth: '600px', margin: '0 auto' }}>
          Top cyber hackers ranked by points and fastest solve time.
        </p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: '#10b981', fontFamily: "'Fira Code', monospace" }}>
          [ Loading Leaderboard Ranks... ]
        </div>
      ) : leaderboard.length > 0 ? (
        <div className="cq-card" style={{ padding: '10px' }}>
          <table className="cq-table">
            <thead>
              <tr>
                <th style={{ width: '90px', textAlign: 'center' }}>Rank</th>
                <th>Player</th>
                <th style={{ textAlign: 'center' }}>Challenges Solved</th>
                <th style={{ textAlign: 'center' }}>Total Time</th>
                <th style={{ textAlign: 'right', paddingRight: '24px' }}>Points</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.map(item => (
                <tr key={item.id} className={user && item.id === user.id ? 'highlight-user' : ''}>
                  <td style={{ textAlign: 'center' }}>
                    {getRankBadge(item.rank)}
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{
                        width: '34px',
                        height: '34px',
                        borderRadius: '50%',
                        background: item.is_current_user ? 'rgba(16, 185, 129, 0.2)' : '#1e293b',
                        border: item.is_current_user ? '1px solid #10b981' : '1px solid #334155',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: item.is_current_user ? '#10b981' : '#94a3b8'
                      }}>
                        <User size={18} />
                      </div>
                      <div>
                        <span style={{ fontWeight: 700, color: '#ffffff', fontSize: '1rem' }}>
                          {item.username}
                        </span>
                        {item.is_current_user && (
                          <span style={{
                            marginLeft: '8px',
                            background: '#10b981',
                            color: '#000',
                            fontSize: '0.7rem',
                            fontWeight: 700,
                            padding: '2px 6px',
                            borderRadius: '4px'
                          }}>YOU</span>
                        )}
                      </div>
                    </div>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <span className="badge badge-category" style={{ padding: '4px 10px', fontSize: '0.85rem' }}>
                      <CheckCircle2 size={13} /> {item.solves_count} Solved
                    </span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <span style={{
                      fontFamily: "'Fira Code', monospace",
                      fontSize: '0.88rem',
                      color: '#60a5fa',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '5px',
                      background: 'rgba(59, 130, 246, 0.1)',
                      border: '1px solid rgba(59, 130, 246, 0.25)',
                      padding: '3px 10px',
                      borderRadius: '12px'
                    }}>
                      <Clock size={13} />
                      {formatSolveTime(item.total_solve_time)}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right', paddingRight: '24px' }}>
                    <span style={{
                      fontFamily: "'Fira Code', monospace",
                      fontSize: '1.15rem',
                      fontWeight: 800,
                      color: '#10b981'
                    }}>
                      {item.points} <span style={{ fontSize: '0.8rem', color: '#64748b' }}>PTS</span>
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="cq-card" style={{ textAlign: 'center', padding: '60px 20px', color: '#94a3b8', fontSize: '1.1rem' }}>
          No players yet. Be the first to solve a challenge!
        </div>
      )}
    </div>
  );
}
