import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { Trophy, CheckCircle2, Shield, Award, Clock, ArrowRight, Zap, Target } from 'lucide-react';
import ChallengeCard from '../components/ChallengeCard';

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDashboard()
      .then(res => {
        setData(res);
      })
      .catch(err => {
        console.error('Failed to fetch dashboard data', err);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="page-container" style={{ display: 'flex', justifyContent: 'center', padding: '100px 20px' }}>
        <div style={{ color: '#10b981', fontFamily: "'Fira Code', monospace" }}>[ Loading Dashboard... ]</div>
      </div>
    );
  }

  const stats = data?.stats || { points: 0, solved_count: 0, total_challenges: 5, remaining_count: 5, rank: 1 };
  const solvedCount = stats.solved_count || 0;
  const totalCount = stats.total_challenges || 1;
  const progressPercent = Math.round((solvedCount / totalCount) * 100);

  return (
    <div className="page-container animate-fade-in" style={{ padding: '30px 20px 80px' }}>
      {/* Welcome Header */}
      <div style={{
        marginBottom: '32px',
        background: 'linear-gradient(90deg, #111726 0%, #1a2336 100%)',
        border: '1px solid #1e293b',
        borderRadius: '16px',
        padding: '30px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '20px'
      }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '6px' }}>
            Welcome back, {user?.username} 👋
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '1rem' }}>
            Track your progress, unlock new challenges, and climb the leaderboard.
          </p>
        </div>

        <Link to="/challenges" className="btn btn-primary" style={{ padding: '12px 24px' }}>
          Browse Challenges <ArrowRight size={18} />
        </Link>
      </div>

      {/* Stats Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '20px',
        marginBottom: '40px'
      }}>
        <div className="cq-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ background: 'rgba(16, 185, 129, 0.15)', padding: '14px', borderRadius: '12px', color: '#10b981' }}>
            <Award size={28} />
          </div>
          <div>
            <div style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: 500 }}>Total Points</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#ffffff', fontFamily: "'Outfit', sans-serif" }}>
              {stats.points} <span style={{ fontSize: '0.9rem', color: '#10b981' }}>PTS</span>
            </div>
          </div>
        </div>

        <div className="cq-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ background: 'rgba(6, 182, 212, 0.15)', padding: '14px', borderRadius: '12px', color: '#06b6d4' }}>
            <CheckCircle2 size={28} />
          </div>
          <div>
            <div style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: 500 }}>Challenges Solved</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#ffffff', fontFamily: "'Outfit', sans-serif" }}>
              {stats.solved_count} <span style={{ fontSize: '0.9rem', color: '#64748b' }}>/ {stats.total_challenges}</span>
            </div>
          </div>
        </div>

        <div className="cq-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ background: 'rgba(139, 92, 246, 0.15)', padding: '14px', borderRadius: '12px', color: '#8b5cf6' }}>
            <Target size={28} />
          </div>
          <div>
            <div style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: 500 }}>Remaining</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#ffffff', fontFamily: "'Outfit', sans-serif" }}>
              {stats.remaining_count}
            </div>
          </div>
        </div>

        <div className="cq-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ background: 'rgba(245, 158, 11, 0.15)', padding: '14px', borderRadius: '12px', color: '#f59e0b' }}>
            <Trophy size={28} />
          </div>
          <div>
            <div style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: 500 }}>Current Rank</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#ffffff', fontFamily: "'Outfit', sans-serif" }}>
              #{stats.rank}
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar Section */}
      <div className="cq-card" style={{ marginBottom: '40px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <span style={{ fontWeight: 600, fontSize: '1rem' }}>Overall Quest Completion</span>
          <span style={{ fontFamily: "'Fira Code', monospace", fontWeight: 700, color: '#10b981' }}>
            {solvedCount} / {totalCount} challenges solved ({progressPercent}%)
          </span>
        </div>
        <div style={{
          width: '100%',
          height: '12px',
          background: '#0d1322',
          borderRadius: '6px',
          overflow: 'hidden',
          border: '1px solid #1e293b'
        }}>
          <div style={{
            width: `${progressPercent}%`,
            height: '100%',
            background: 'linear-gradient(90deg, #06b6d4 0%, #10b981 100%)',
            borderRadius: '6px',
            transition: 'width 0.5s ease-in-out'
          }} />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '30px', marginBottom: '40px' }}>
        {/* Recommended Challenges */}
        <div>
          <h2 style={{ fontSize: '1.4rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Zap size={20} color="#10b981" /> Recommended Challenges
          </h2>
          {data?.recommended_challenges?.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {data.recommended_challenges.map(ch => (
                <ChallengeCard key={ch.id} challenge={ch} />
              ))}
            </div>
          ) : (
            <div className="cq-card" style={{ textAlign: 'center', color: '#94a3b8', padding: '30px' }}>
              🎉 You have solved all available challenges! Check back soon for new additions.
            </div>
          )}
        </div>

        {/* Recent Solves Activity */}
        <div>
          <h2 style={{ fontSize: '1.4rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Clock size={20} color="#06b6d4" /> Recent Activity
          </h2>
          <div className="cq-card" style={{ padding: '0' }}>
            {data?.recent_activity?.length > 0 ? (
              <table className="cq-table">
                <thead>
                  <tr>
                    <th>Challenge</th>
                    <th>Category</th>
                    <th>Points</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_activity.map(act => (
                    <tr key={act.id}>
                      <td style={{ fontWeight: 600 }}>{act.title}</td>
                      <td>
                        <span className="badge badge-category">{act.category}</span>
                      </td>
                      <td style={{ color: '#10b981', fontWeight: 700, fontFamily: "'Fira Code', monospace" }}>
                        +{act.points_earned}
                      </td>
                      <td style={{ color: '#64748b', fontSize: '0.85rem' }}>
                        {new Date(act.solved_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div style={{ padding: '30px', textAlign: 'center', color: '#94a3b8' }}>
                No recent solve activity yet. Start a challenge to get on the board!
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
