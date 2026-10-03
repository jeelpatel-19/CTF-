import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../services/api';
import ChallengeCard from '../components/ChallengeCard';
import { Search, Filter, Shield } from 'lucide-react';

export default function ChallengesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters state
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || 'All');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    api.getChallenges()
      .then(res => {
        setChallenges(res.challenges || []);
      })
      .catch(err => {
        console.error('Failed to load challenges', err);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const cat = searchParams.get('category');
    if (cat) {
      setSelectedCategory(cat);
    }
  }, [searchParams]);

  const categories = ['All', 'Web Security', 'Cryptography', 'Forensics', 'Networking', 'Linux', 'OSINT'];
  const difficulties = ['All', 'Easy', 'Medium', 'Hard'];
  const statuses = ['All', 'Solved', 'Unsolved'];

  const filteredChallenges = challenges.filter(c => {
    // Category Filter
    if (selectedCategory !== 'All' && c.category.toLowerCase() !== selectedCategory.toLowerCase()) {
      return false;
    }
    // Difficulty Filter
    if (selectedDifficulty !== 'All' && c.difficulty.toLowerCase() !== selectedDifficulty.toLowerCase()) {
      return false;
    }
    // Status Filter
    if (selectedStatus === 'Solved' && !c.is_solved) return false;
    if (selectedStatus === 'Unsolved' && c.is_solved) return false;

    // Search Query Filter
    if (searchQuery.trim() !== '') {
      const q = searchQuery.toLowerCase();
      const titleMatch = c.title.toLowerCase().includes(q);
      const descMatch = c.description.toLowerCase().includes(q);
      const catMatch = c.category.toLowerCase().includes(q);
      if (!titleMatch && !descMatch && !catMatch) return false;
    }

    return true;
  });

  return (
    <div className="page-container animate-fade-in" style={{ padding: '30px 20px 80px' }}>
      {/* Page Title */}
      <div style={{ marginBottom: '30px' }}>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Shield color="#10b981" size={32} /> CyberQuest Challenges
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '1.05rem' }}>
          Test your skills across multiple domains. Select a challenge to view details, use hints, and submit flags.
        </p>
      </div>

      {/* FILTER BAR */}
      <div className="cq-card" style={{ marginBottom: '30px', padding: '20px' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* Search Box */}
          <div style={{ position: 'relative', flex: '1 1 250px' }}>
            <input
              type="text"
              className="form-input"
              placeholder="Search challenges by title or keyword..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ paddingLeft: '40px' }}
            />
            <Search size={18} color="#64748b" style={{ position: 'absolute', left: '12px', top: '12px' }} />
          </div>

          {/* Category Dropdown/Pills */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>
              Category:
            </span>
            <select
              className="form-select"
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                setSearchParams(e.target.value === 'All' ? {} : { category: e.target.value });
              }}
              style={{ width: 'auto', minWidth: '150px' }}
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          {/* Difficulty Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>
              Difficulty:
            </span>
            <select
              className="form-select"
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              style={{ width: 'auto', minWidth: '120px' }}
            >
              {difficulties.map(diff => (
                <option key={diff} value={diff}>{diff}</option>
              ))}
            </select>
          </div>

          {/* Status Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>
              Status:
            </span>
            <select
              className="form-select"
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              style={{ width: 'auto', minWidth: '120px' }}
            >
              {statuses.map(st => (
                <option key={st} value={st}>{st}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* CHALLENGES GRID */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: '#10b981', fontFamily: "'Fira Code', monospace" }}>
          [ Loading Challenge Catalog... ]
        </div>
      ) : filteredChallenges.length > 0 ? (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: '24px'
        }}>
          {filteredChallenges.map(c => (
            <ChallengeCard key={c.id} challenge={c} />
          ))}
        </div>
      ) : (
        <div className="cq-card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div style={{ color: '#64748b', marginBottom: '12px' }}>
            <Filter size={40} />
          </div>
          <h3 style={{ fontSize: '1.2rem', marginBottom: '8px' }}>No challenges found</h3>
          <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>
            Try adjusting your search query or filter parameters.
          </p>
          <button
            onClick={() => {
              setSelectedCategory('All');
              setSelectedDifficulty('All');
              setSelectedStatus('All');
              setSearchQuery('');
              setSearchParams({});
            }}
            className="btn btn-secondary"
            style={{ marginTop: '20px' }}
          >
            Reset All Filters
          </button>
        </div>
      )}
    </div>
  );
}
