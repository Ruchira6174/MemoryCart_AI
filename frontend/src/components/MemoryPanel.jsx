import React from 'react';
import MemoryCard from './MemoryCard';

export default function MemoryPanel({ memories }) {
  return (
    <div style={styles.panel}>
      <h3 style={styles.title}>Memory Panel</h3>
      {(!memories || memories.length === 0) && (
        <div style={styles.empty}>No memories yet — recent interactions will appear here.</div>
      )}
      {memories && memories.map((m) => (
        <MemoryCard key={m.memory_id} memory={m} />
      ))}
    </div>
  );
}

const styles = {
  panel: {
    width: 320,
    padding: 16,
    borderLeft: '1px solid rgba(255,255,255,0.04)',
    background: 'linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01))',
    overflowY: 'auto',
  },
  title: { margin: 0, marginBottom: 12, color: '#c7b3ff' },
  empty: { color: '#94a3b8', fontSize: 13 },
};
