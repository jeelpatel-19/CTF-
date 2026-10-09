import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, ExternalLink, Download, Lightbulb, Flag, CheckCircle2, AlertCircle, Shield, Award, HelpCircle, Clock } from 'lucide-react';

export default function ChallengeDetailPage() {
  const { id } = useParams();
  const { user, refreshUser } = useAuth();
  
  const [challenge, setChallenge] = useState(null);
  const [loading, setLoading] = useState(true);

  const [flagInput, setFlagInput] = useState('');
  const [submitResult, setSubmitResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [starting, setStarting] = useState(false);
  const [unlockingHintId, setUnlockingHintId] = useState(null);

  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const loadChallenge = async () => {
    try {
      const res = await api.getChallengeDetail(id);
      setChallenge(res.challenge);
    } catch (err) {
      console.error('Failed to load challenge details', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadChallenge();
  }, [id]);

  useEffect(() => {
    if (!challenge) return;

    if (challenge.is_solved && challenge.time_taken_seconds != null) {
      setElapsedSeconds(challenge.time_taken_seconds);
      return;
    }

    if (!challenge.started_at) return;

    const parseServerDate = (dateStr) => {
      if (!dateStr) return new Date();
      const formatted = dateStr.includes('T') ? dateStr : dateStr.replace(' ', 'T') + 'Z';
      return new Date(formatted);
    };

    const startDate = parseServerDate(challenge.started_at);

    const updateTimer = () => {
      const now = new Date();
      const diffSec = Math.max(0, Math.floor((now.getTime() - startDate.getTime()) / 1000));
      setElapsedSeconds(diffSec);
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);

    return () => clearInterval(interval);
  }, [challenge]);

  const formatDuration = (totalSeconds) => {
    if (totalSeconds === null || totalSeconds === undefined || totalSeconds < 0) return '00:00';
    const hrs = Math.floor(totalSeconds / 3600);
    const mins = Math.floor((totalSeconds % 3600) / 60);
    const secs = totalSeconds % 60;
    
    const pad = (num) => String(num).padStart(2, '0');
    if (hrs > 0) {
      return `${pad(hrs)}:${pad(mins)}:${pad(secs)}`;
    }
    return `${pad(mins)}:${pad(secs)}`;
  };

  const getBackendOrigin = () => {
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:5000/api";
    try {
      const parsed = new URL(apiUrl);
      return parsed.origin;
    } catch {
      return "http://localhost:5000";
    }
  };

  const formatTargetUrl = (url) => {
    if (!url) return '';
    const origin = getBackendOrigin();
    if (url.startsWith('http://localhost:5000')) {
      return url.replace('http://localhost:5000', origin);
    }
    if (url.startsWith('/')) {
      return `${origin}${url}`;
    }
    return url;
  };

  const formatFileUrl = (url) => {
    if (!url) return '';
    const origin = getBackendOrigin();
    if (url.startsWith('http://localhost:5000')) {
      return url.replace('http://localhost:5000', origin);
    }
    if (url.startsWith('/')) {
      return `${origin}${url}`;
    }
    return url;
  };

  const handleFlagSubmit = async (e) => {
    e.preventDefault();
    if (!flagInput.trim()) return;

    if (!user) {
      setSubmitResult({ success: false, message: 'Please log in to submit flags.' });
      return;
    }

    setSubmitting(true);
    setSubmitResult(null);

    try {
      const res = await api.submitFlag(id, flagInput.trim());
      setSubmitResult(res);
      if (res.success) {
        setFlagInput('');
        loadChallenge();
        refreshUser();
      }
    } catch (err) {
      setSubmitResult({
        success: false,
        message: err.data?.message || err.message || '✕ Incorrect flag. Keep investigating.'
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleStartChallenge = async () => {
    setStarting(true);
    try {
      await api.startChallenge(id);
      await loadChallenge();
    } catch (err) {
      alert(err.message || 'Failed to start challenge');
    } finally {
      setStarting(false);
    }
  };

  const handleUnlockHint = async (hintId) => {
    if (!user) {
      alert('Please log in to reveal hints.');
      return;
    }

    setUnlockingHintId(hintId);
    try {
      await api.unlockHint(hintId);
      await loadChallenge();
      refreshUser();
    } catch (err) {
      alert(err.message || 'Failed to reveal hint');
    } finally {
      setUnlockingHintId(null);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 20px', color: '#10b981', fontFamily: "'Fira Code', monospace" }}>
        [ Loading Challenge Data... ]
      </div>
    );
  }

  if (!challenge) {
    return (
      <div className="page-container" style={{ textAlign: 'center', padding: '60px 20px' }}>
        <h2 style={{ fontSize: '1.8rem', marginBottom: '16px' }}>Challenge Not Found</h2>
        <Link to="/challenges" className="btn btn-secondary">
          <ArrowLeft size={16} /> Back to Challenges
        </Link>
      </div>
    );
  }

  const getDifficultyBadge = (difficulty) => {
    const diff = (difficulty || '').toLowerCase();
    if (diff === 'easy') return <span className="badge badge-easy">Easy</span>;
    if (diff === 'medium') return <span className="badge badge-medium">Medium</span>;
    return <span className="badge badge-hard">Hard</span>;
  };

  return (
    <div className="page-container animate-fade-in" style={{ padding: '30px 20px 80px', maxWidth: '900px' }}>
      {/* Back Button */}
      <div style={{ marginBottom: '24px' }}>
        <Link to="/challenges" style={{ color: '#94a3b8', display: 'inline-flex', alignItems: 'center', gap: '6px', fontWeight: 500, fontSize: '0.95rem' }}>
          <ArrowLeft size={16} /> Back to Challenges
        </Link>
      </div>

      {/* Challenge Title Banner */}
      <div className="cq-card" style={{
        marginBottom: '30px',
        border: challenge.is_solved ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid #1e293b',
        background: challenge.is_solved ? 'linear-gradient(180deg, rgba(16, 185, 129, 0.08) 0%, #111726 100%)' : '#111726'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="badge badge-category">{challenge.category}</span>
            {getDifficultyBadge(challenge.difficulty)}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {/* Server-synced Timer Badge */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: challenge.is_solved ? 'rgba(16, 185, 129, 0.12)' : 'rgba(59, 130, 246, 0.12)',
              border: challenge.is_solved ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(59, 130, 246, 0.3)',
              color: challenge.is_solved ? '#34d399' : '#60a5fa',
              padding: '4px 12px',
              borderRadius: '20px',
              fontFamily: "'Fira Code', monospace",
              fontSize: '0.88rem',
              fontWeight: 600
            }}>
              <Clock size={15} />
              {challenge.is_solved ? `Solved in ${formatDuration(elapsedSeconds)}` : `Time: ${formatDuration(elapsedSeconds)}`}
            </div>

            <div style={{ fontFamily: "'Fira Code', monospace", fontSize: '1.1rem', fontWeight: 700, color: '#10b981' }}>
              ⚡ {challenge.points} POINTS
            </div>
            {challenge.is_solved && (
              <span className="badge badge-solved" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
                <CheckCircle2 size={14} /> Solved
              </span>
            )}
          </div>
        </div>

        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: '#ffffff', marginBottom: '16px' }}>
          {challenge.title}
        </h1>

        {/* Description formatted nicely */}
        <div style={{
          color: '#cbd5e1',
          fontSize: '1.05rem',
          lineHeight: '1.7',
          whiteSpace: 'pre-line',
          padding: '20px',
          background: '#0d1322',
          borderRadius: '10px',
          border: '1px solid #1e293b',
          marginBottom: '24px'
        }}>
          {challenge.description}
        </div>

        {/* Action Targets & Downloads */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px' }}>
          {!challenge.is_solved && !challenge.started_at && (
            <button
              onClick={handleStartChallenge}
              className="btn btn-primary"
              style={{ padding: '12px 20px', background: '#3b82f6', color: '#fff', border: 'none' }}
              disabled={starting}
            >
              🚀 {starting ? 'Starting...' : 'Start Challenge'}
            </button>
          )}

          {challenge.started_at && challenge.target_url && (
            <a
              href={formatTargetUrl(challenge.target_url)}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
              style={{ padding: '12px 20px' }}
            >
              <ExternalLink size={18} /> Open Target Page ({formatTargetUrl(challenge.target_url)})
            </a>
          )}

          {challenge.started_at && challenge.file_url && (
            <a
              href={formatFileUrl(challenge.file_url)}
              download
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary"
              style={{ padding: '12px 20px' }}
            >
              <Download size={18} /> Download Challenge File
            </a>
          )}
        </div>
      </div>

      {challenge.started_at && (
        <>
          {/* HINTS SECTION */}
          <div className="cq-card" style={{ marginBottom: '30px' }}>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px', color: '#f59e0b' }}>
              <Lightbulb size={20} /> Challenge Hints
            </h3>

            {challenge.hints && challenge.hints.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {challenge.hints.map((hint, idx) => (
                  <div key={hint.id} style={{
                    background: '#0d1322',
                    border: '1px solid #1e293b',
                    borderRadius: '10px',
                    padding: '18px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: hint.is_unlocked ? '10px' : '0' }}>
                      <div style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        💡 Hint {hint.index || idx + 1}
                        {hint.penalty > 0 && (
                          <span style={{ fontSize: '0.78rem', color: '#ef4444', fontFamily: "'Fira Code', monospace" }}>
                            (-{hint.penalty} pts penalty)
                          </span>
                        )}
                      </div>

                      {!hint.is_unlocked ? (
                        <button
                          onClick={() => handleUnlockHint(hint.id)}
                          className="btn btn-secondary"
                          style={{ padding: '6px 14px', fontSize: '0.85rem' }}
                          disabled={unlockingHintId === hint.id}
                        >
                          {unlockingHintId === hint.id ? 'Unlocking...' : 'Reveal Hint'}
                        </button>
                      ) : (
                        <span style={{ fontSize: '0.8rem', color: '#10b981', fontWeight: 600 }}>
                          ✓ Unlocked
                        </span>
                      )}
                    </div>

                    {hint.is_unlocked && (
                      <div style={{
                        color: '#fbbf24',
                        fontFamily: "'Fira Code', monospace",
                        fontSize: '0.92rem',
                        background: 'rgba(245, 158, 11, 0.08)',
                        padding: '12px 14px',
                        borderRadius: '6px',
                        borderLeft: '3px solid #f59e0b',
                        lineHeight: '1.5'
                      }}>
                        {hint.hint_text}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#64748b', fontSize: '0.9rem' }}>No hints available for this challenge.</p>
            )}
          </div>

          {/* FLAG SUBMISSION FORM */}
          <div className="cq-card">
            <h3 style={{ fontSize: '1.25rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Flag size={20} color="#10b981" /> Submit Flag
            </h3>

            {submitResult && (
              <div className={submitResult.success ? "alert alert-success" : "alert alert-error"}>
                {submitResult.success ? <CheckCircle2 size={20} /> : <AlertCircle size={20} />}
                <span style={{ fontWeight: 600 }}>{submitResult.message}</span>
              </div>
            )}

            <form onSubmit={handleFlagSubmit}>
              <div className="form-group">
                <label className="form-label">Enter Captured Flag</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="FLAG{...}"
                  value={flagInput}
                  onChange={(e) => setFlagInput(e.target.value)}
                  style={{ fontFamily: "'Fira Code', monospace", fontSize: '1rem', padding: '14px' }}
                  disabled={submitting || challenge.is_solved}
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%', padding: '14px', fontSize: '1rem', marginTop: '10px' }}
                disabled={submitting || !flagInput.trim() || challenge.is_solved}
              >
                {challenge.is_solved ? '✓ Challenge Solved' : submitting ? 'Validating Flag...' : 'SUBMIT FLAG'}
              </button>
            </form>
          </div>
        </>
      )}
    </div>
  );
}
