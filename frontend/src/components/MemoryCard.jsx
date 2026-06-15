import React from 'react';

export default function MemoryCard({ memory }) {
  return (
    <div style={styles.card}>
      <div style={styles.type}>{memory.issue_type}</div>
      <div style={styles.summary}>{memory.summary}</div>
      <div style={styles.ts}>{memory.created_at ? new Date(memory.created_at).toLocaleString() : 'unknown'}</div>
    </div>
  );
}

const styles = {
  card: {
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(255,255,255,0.06)',
    padding: '10px',
    borderRadius: 8,
    marginBottom: 8,
  },
  type: { fontSize: 12, color: '#a78bfa', fontWeight: 700, marginBottom: 6 },
  summary: { fontSize: 13, color: '#e2e8f0', whiteSpace: 'pre-wrap' },
  ts: { fontSize: 11, color: '#94a3b8', marginTop: 8 },
};
