import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Terminal, Shield, Trophy, LayoutDashboard, LogOut, User, Lock } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header style={{
      background: 'rgba(17, 23, 38, 0.95)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid #1e293b',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0 20px',
        height: '70px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        {/* Brand Logo */}
        <Link to={user ? "/" : "/login"} style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
          <div style={{
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid #10b981',
            borderRadius: '8px',
            padding: '6px 10px',
            display: 'flex',
            alignItems: 'center',
            color: '#10b981'
          }}>
            <Terminal size={22} />
          </div>
          <div>
            <span style={{
              fontFamily: "'Outfit', sans-serif",
              fontSize: '1.35rem',
              fontWeight: 800,
              letterSpacing: '0.05em',
              color: '#ffffff'
            }}>CYBER<span style={{ color: '#10b981' }}>QUEST</span></span>
          </div>
        </Link>

        {/* Navigation Links - Only visible to authenticated users */}
        {user && (
          <nav style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <Link to="/" style={{
              color: isActive('/') ? '#10b981' : '#94a3b8',
              fontWeight: 500,
              fontSize: '0.95rem',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              Home
            </Link>

            <Link to="/dashboard" style={{
              color: isActive('/dashboard') ? '#10b981' : '#94a3b8',
              fontWeight: 500,
              fontSize: '0.95rem',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <LayoutDashboard size={16} />
              Dashboard
            </Link>

            <Link to="/challenges" style={{
              color: isActive('/challenges') ? '#10b981' : '#94a3b8',
              fontWeight: 500,
              fontSize: '0.95rem',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <Shield size={16} />
              Challenges
            </Link>

            <Link to="/leaderboard" style={{
              color: isActive('/leaderboard') ? '#10b981' : '#94a3b8',
              fontWeight: 500,
              fontSize: '0.95rem',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <Trophy size={16} />
              Leaderboard
            </Link>

            {user.role === 'admin' && (
              <Link to="/admin" style={{
                color: isActive('/admin') ? '#f59e0b' : '#fbbf24',
                fontWeight: 600,
                fontSize: '0.95rem',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                background: 'rgba(245, 158, 11, 0.1)',
                padding: '5px 12px',
                borderRadius: '6px',
                border: '1px solid rgba(245, 158, 11, 0.3)'
              }}>
                <Lock size={14} />
                Admin Panel
              </Link>
            )}
          </nav>
        )}

        {/* User Status / Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              {/* Points Badge */}
              <div style={{
                background: 'rgba(16, 185, 129, 0.12)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                color: '#34d399',
                padding: '4px 12px',
                borderRadius: '20px',
                fontFamily: "'Fira Code', monospace",
                fontSize: '0.85rem',
                fontWeight: 600
              }}>
                ⚡ {user.points ?? 0} PTS
              </div>

              {/* Username badge */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: '#1e293b',
                padding: '6px 12px',
                borderRadius: '8px',
                border: '1px solid #334155'
              }}>
                <User size={16} color="#94a3b8" />
                <span style={{ fontWeight: 600, fontSize: '0.9rem', color: '#f8fafc' }}>
                  {user.username}
                </span>
              </div>

              {/* Logout button */}
              <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '8px 12px' }} title="Logout">
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Link to="/login" className="btn btn-secondary" style={{ padding: '8px 16px' }}>
                Log In
              </Link>
              <Link to="/register" className="btn btn-primary" style={{ padding: '8px 16px' }}>
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
