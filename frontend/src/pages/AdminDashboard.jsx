import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Lock, Plus, Edit, Trash2, Users, Shield, Award, Activity, CheckCircle2, XCircle, RefreshCw } from 'lucide-react';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('challenges'); // 'challenges', 'users', 'submissions'
  const [stats, setStats] = useState(null);
  const [challenges, setChallenges] = useState([]);
  const [users, setUsers] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modal State for Add / Edit Challenge
  const [showModal, setShowModal] = useState(false);
  const [editingChallenge, setEditingChallenge] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'Web Security',
    difficulty: 'Easy',
    points: 50,
    flag: '',
    target_url: '',
    file_url: '',
    hint_text: '',
    hint_penalty: 10
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsRes, challengesRes, usersRes, subsRes] = await Promise.all([
        api.getAdminStats(),
        api.getAdminChallenges(),
        api.getAdminUsers(),
        api.getAdminSubmissions()
      ]);
      setStats(statsRes.stats);
      setChallenges(challengesRes.challenges || []);
      setUsers(usersRes.users || []);
      setSubmissions(subsRes.submissions || []);
    } catch (err) {
      console.error('Failed to load admin data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleOpenAddModal = () => {
    setEditingChallenge(null);
    setFormData({
      title: '',
      description: '',
      category: 'Web Security',
      difficulty: 'Easy',
      points: 50,
      flag: 'FLAG{...}',
      target_url: '',
      file_url: '',
      hint_text: '',
      hint_penalty: 10
    });
    setShowModal(true);
  };

  const handleOpenEditModal = (c) => {
    setEditingChallenge(c);
    setFormData({
      title: c.title,
      description: c.description,
      category: c.category,
      difficulty: c.difficulty,
      points: c.points,
      flag: c.flag,
      target_url: c.target_url || '',
      file_url: c.file_url || '',
      hint_text: c.hints && c.hints.length > 0 ? c.hints[0].hint_text : '',
      hint_penalty: c.hints && c.hints.length > 0 ? c.hints[0].penalty : 10
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this challenge?')) return;
    try {
      await api.deleteChallenge(id);
      loadData();
    } catch (err) {
      alert(err.message || 'Failed to delete challenge');
    }
  };

  const handleDeleteUser = async (user) => {
    if (user.role === 'admin') {
      alert('Protected admin accounts cannot be deleted.');
      return;
    }

    const confirmMessage = `Are you sure you want to delete player "${user.username}" (User ID #${user.id})?\n\nThis will permanently delete their account, solves, submissions, and leaderboard progress. This action cannot be undone.`;
    if (!window.confirm(confirmMessage)) return;

    try {
      await api.deleteUser(user.id);
      loadData();
    } catch (err) {
      alert(err.message || 'Failed to delete user.');
    }
  };

  const handleClearAllPlayers = async () => {
    const playerUsers = users.filter(u => u.role !== 'admin');
    if (playerUsers.length === 0) {
      alert('There are currently no registered player accounts to clear.');
      return;
    }

    const confirmMessage = `⚠️ CRITICAL ACTION — CLEAR ALL PLAYERS:\n\nThis will permanently delete ALL (${playerUsers.length}) registered player accounts, solves, submissions, and leaderboard scores.\n\nChallenges, hints, and Admin accounts will NOT be deleted.\n\nDo you want to continue?`;
    if (!window.confirm(confirmMessage)) return;

    try {
      const res = await api.clearAllPlayers();
      alert(res.message || 'All player accounts cleared successfully.');
      loadData();
    } catch (err) {
      alert(err.message || 'Failed to clear player accounts.');
    }
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    const hintsPayload = formData.hint_text ? [
      { hint_text: formData.hint_text, penalty: Number(formData.hint_penalty) }
    ] : [];

    const payload = {
      title: formData.title,
      description: formData.description,
      category: formData.category,
      difficulty: formData.difficulty,
      points: Number(formData.points),
      flag: formData.flag,
      target_url: formData.target_url || null,
      file_url: formData.file_url || null,
      hints: hintsPayload
    };

    try {
      if (editingChallenge) {
        await api.updateChallenge(editingChallenge.id, payload);
      } else {
        await api.createChallenge(payload);
      }
      setShowModal(false);
      loadData();
    } catch (err) {
      alert(err.message || 'Failed to save challenge');
    }
  };

  return (
    <div className="page-container animate-fade-in" style={{ padding: '30px 20px 80px' }}>
      {/* Admin Title Banner */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '30px',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: '#ffffff', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Lock size={28} color="#f59e0b" /> CyberQuest Admin Panel
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '1rem', marginTop: '4px' }}>
            Manage challenges, monitor user progress, and review live submission logs.
          </p>
        </div>

        <button onClick={loadData} className="btn btn-secondary" style={{ gap: '6px' }}>
          <RefreshCw size={16} /> Refresh Data
        </button>
      </div>

      {/* Admin Stats Overview */}
      {stats && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '20px',
          marginBottom: '32px'
        }}>
          <div className="cq-card" style={{ padding: '20px', textAlign: 'center' }}>
            <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Total Users</div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: '#ffffff', marginTop: '4px' }}>{stats.total_users}</div>
          </div>
          <div className="cq-card" style={{ padding: '20px', textAlign: 'center' }}>
            <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Total Challenges</div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: '#10b981', marginTop: '4px' }}>{stats.total_challenges}</div>
          </div>
          <div className="cq-card" style={{ padding: '20px', textAlign: 'center' }}>
            <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Total Submissions</div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: '#06b6d4', marginTop: '4px' }}>{stats.total_submissions}</div>
          </div>
          <div className="cq-card" style={{ padding: '20px', textAlign: 'center' }}>
            <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Solve Accuracy</div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f59e0b', marginTop: '4px' }}>{stats.solve_rate}%</div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div style={{ display: 'flex', gap: '12px', borderBottom: '1px solid #1e293b', marginBottom: '24px' }}>
        <button
          onClick={() => setActiveTab('challenges')}
          style={{
            padding: '12px 20px',
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'challenges' ? '3px solid #10b981' : '3px solid transparent',
            color: activeTab === 'challenges' ? '#10b981' : '#94a3b8',
            fontWeight: 700,
            fontSize: '0.95rem',
            cursor: 'pointer'
          }}
        >
          <Shield size={16} style={{ display: 'inline', marginRight: '6px' }} /> Challenges ({challenges.length})
        </button>

        <button
          onClick={() => setActiveTab('users')}
          style={{
            padding: '12px 20px',
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'users' ? '3px solid #10b981' : '3px solid transparent',
            color: activeTab === 'users' ? '#10b981' : '#94a3b8',
            fontWeight: 700,
            fontSize: '0.95rem',
            cursor: 'pointer'
          }}
        >
          <Users size={16} style={{ display: 'inline', marginRight: '6px' }} /> Registered Users ({users.length})
        </button>

        <button
          onClick={() => setActiveTab('submissions')}
          style={{
            padding: '12px 20px',
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'submissions' ? '3px solid #10b981' : '3px solid transparent',
            color: activeTab === 'submissions' ? '#10b981' : '#94a3b8',
            fontWeight: 700,
            fontSize: '0.95rem',
            cursor: 'pointer'
          }}
        >
          <Activity size={16} style={{ display: 'inline', marginRight: '6px' }} /> Flag Submissions Audit ({submissions.length})
        </button>
      </div>

      {/* TAB CONTENT 1: CHALLENGES */}
      {activeTab === 'challenges' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }}>
            <button onClick={handleOpenAddModal} className="btn btn-primary">
              <Plus size={18} /> Add New Challenge
            </button>
          </div>

          <div className="cq-card" style={{ padding: '0' }}>
            <table className="cq-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Difficulty</th>
                  <th>Points</th>
                  <th>Flag String</th>
                  <th>Solves</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {challenges.map(c => (
                  <tr key={c.id}>
                    <td>#{c.id}</td>
                    <td style={{ fontWeight: 700, color: '#ffffff' }}>{c.title}</td>
                    <td><span className="badge badge-category">{c.category}</span></td>
                    <td>
                      <span className={`badge badge-${c.difficulty.toLowerCase()}`}>{c.difficulty}</span>
                    </td>
                    <td style={{ color: '#10b981', fontWeight: 700 }}>{c.points}</td>
                    <td style={{ fontFamily: "'Fira Code', monospace", fontSize: '0.85rem', color: '#fbbf24' }}>{c.flag}</td>
                    <td>{c.solves_count}</td>
                    <td style={{ textAlign: 'right' }}>
                      <button onClick={() => handleOpenEditModal(c)} className="btn btn-secondary" style={{ padding: '6px 10px', marginRight: '6px' }}>
                        <Edit size={14} />
                      </button>
                      <button onClick={() => handleDelete(c.id)} className="btn btn-danger" style={{ padding: '6px 10px' }}>
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB CONTENT 2: USERS */}
      {activeTab === 'users' && (
        <div>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '16px',
            flexWrap: 'wrap',
            gap: '12px',
            background: '#111726',
            padding: '16px 20px',
            borderRadius: '12px',
            border: '1px solid #1e293b'
          }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', color: '#ffffff', margin: 0, fontWeight: 700 }}>
                Player Accounts & Progress Management
              </h3>
              <p style={{ color: '#94a3b8', fontSize: '0.88rem', margin: '4px 0 0 0' }}>
                View registered players, delete individual player accounts, or clear all player progress.
              </p>
            </div>

            <button
              onClick={handleClearAllPlayers}
              className="btn btn-danger"
              style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '10px 18px' }}
            >
              <Trash2 size={16} /> Clear All Players
            </button>
          </div>

          <div className="cq-card" style={{ padding: '0' }}>
            <table className="cq-table">
              <thead>
                <tr>
                  <th>User ID</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Points</th>
                  <th>Solves</th>
                  <th>Joined Date</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td>#{u.id}</td>
                    <td style={{ fontWeight: 700, color: '#ffffff' }}>{u.username}</td>
                    <td style={{ color: '#94a3b8' }}>{u.email}</td>
                    <td>
                      <span className="badge" style={{
                        background: u.role === 'admin' ? 'rgba(245, 158, 11, 0.2)' : '#1e293b',
                        color: u.role === 'admin' ? '#f59e0b' : '#94a3b8',
                        border: '1px solid #334155'
                      }}>
                        {u.role.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ color: '#10b981', fontWeight: 700 }}>{u.points} PTS</td>
                    <td>{u.solves_count}</td>
                    <td style={{ color: '#64748b', fontSize: '0.85rem' }}>{new Date(u.created_at).toLocaleDateString()}</td>
                    <td style={{ textAlign: 'right' }}>
                      {u.role === 'admin' ? (
                        <span style={{ fontSize: '0.8rem', color: '#64748b', fontStyle: 'italic' }}>Protected Admin</span>
                      ) : (
                        <button
                          onClick={() => handleDeleteUser(u)}
                          className="btn btn-danger"
                          style={{ padding: '6px 12px', fontSize: '0.82rem', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                        >
                          <Trash2 size={14} /> Delete User
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB CONTENT 3: SUBMISSIONS */}
      {activeTab === 'submissions' && (
        <div className="cq-card" style={{ padding: '0' }}>
          <table className="cq-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>User</th>
                <th>Challenge</th>
                <th>Submitted Flag</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {submissions.map(sub => (
                <tr key={sub.id}>
                  <td style={{ color: '#64748b', fontSize: '0.85rem' }}>{new Date(sub.submitted_at).toLocaleString()}</td>
                  <td style={{ fontWeight: 600 }}>{sub.username}</td>
                  <td>{sub.challenge_title}</td>
                  <td style={{ fontFamily: "'Fira Code', monospace", fontSize: '0.85rem' }}>{sub.submitted_flag}</td>
                  <td>
                    {sub.is_correct ? (
                      <span className="badge badge-easy" style={{ display: 'inline-flex', gap: '4px' }}>
                        <CheckCircle2 size={12} /> Correct
                      </span>
                    ) : (
                      <span className="badge badge-hard" style={{ display: 'inline-flex', gap: '4px' }}>
                        <XCircle size={12} /> Incorrect
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ADD / EDIT CHALLENGE MODAL */}
      {showModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.75)',
          backdropFilter: 'blur(5px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px'
        }}>
          <div className="cq-card" style={{ maxWidth: '600px', width: '100%', maxHeight: '90vh', overflowY: 'auto' }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '20px' }}>
              {editingChallenge ? 'Edit Challenge' : 'Create New Challenge'}
            </h2>

            <form onSubmit={handleFormSubmit}>
              <div className="form-group">
                <label className="form-label">Title</label>
                <input
                  type="text"
                  className="form-input"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                <div className="form-group">
                  <label className="form-label">Category</label>
                  <select
                    className="form-select"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  >
                    <option value="Web Security">Web Security</option>
                    <option value="Cryptography">Cryptography</option>
                    <option value="Forensics">Forensics</option>
                    <option value="Networking">Networking</option>
                    <option value="Linux">Linux</option>
                    <option value="OSINT">OSINT</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Difficulty</label>
                  <select
                    className="form-select"
                    value={formData.difficulty}
                    onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                  >
                    <option value="Easy">Easy</option>
                    <option value="Medium">Medium</option>
                    <option value="Hard">Hard</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Points</label>
                  <input
                    type="number"
                    className="form-input"
                    required
                    min="10"
                    max="1000"
                    value={formData.points}
                    onChange={(e) => setFormData({ ...formData, points: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea
                  className="form-textarea"
                  rows="3"
                  required
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Flag String</label>
                <input
                  type="text"
                  className="form-input"
                  required
                  placeholder="FLAG{...}"
                  value={formData.flag}
                  onChange={(e) => setFormData({ ...formData, flag: e.target.value })}
                  style={{ fontFamily: "'Fira Code', monospace" }}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Target URL (Optional)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="http://localhost:5001"
                  value={formData.target_url}
                  onChange={(e) => setFormData({ ...formData, target_url: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Challenge File URL (Optional)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="/static/challenges/file.pcap"
                  value={formData.file_url}
                  onChange={(e) => setFormData({ ...formData, file_url: e.target.value })}
                />
              </div>

              <div style={{ borderTop: '1px solid #1e293b', paddingTop: '16px', marginTop: '16px' }}>
                <h4 style={{ fontSize: '1rem', color: '#f59e0b', marginBottom: '12px' }}>Hint Setup</h4>
                <div className="form-group">
                  <label className="form-label">Hint Text</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="Enter hint description..."
                    value={formData.hint_text}
                    onChange={(e) => setFormData({ ...formData, hint_text: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Hint Penalty Points</label>
                  <input
                    type="number"
                    className="form-input"
                    value={formData.hint_penalty}
                    onChange={(e) => setFormData({ ...formData, hint_penalty: e.target.value })}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingChallenge ? 'Update Challenge' : 'Create Challenge'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
