import React, { useState, useEffect } from 'react';
import { Brain, X, Loader2, AlertCircle } from 'lucide-react';
import MemoryCard from './MemoryCard';
import { fetchMemorySummary } from '../services/api';

export const MemoryPanel = ({ onClose, userId = 1 }) => {
  const [memories, setMemories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadMemories = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchMemorySummary(userId);
        setMemories(data);
      } catch (err) {
        setError('Failed to load memory context.');
      } finally {
        setIsLoading(false);
      }
    };
    loadMemories();
  }, [userId]);

  return (
    <div className="flex flex-col h-full bg-[#FAFAFA]">
      <div className="h-16 flex items-center justify-between px-6 border-b border-gray-200 bg-white">
        <div className="flex items-center gap-2">
          <Brain size={18} className="text-indigo-600" />
          <h3 className="font-bold text-black tracking-tight">Customer Memory</h3>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="md:hidden p-2 rounded-lg text-gray-400 hover:text-black hover:bg-gray-100 transition-colors cursor-pointer"
          >
            <X size={18} />
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400 space-y-3">
            <Loader2 className="animate-spin text-indigo-500" size={24} />
            <p className="text-sm">Retrieving context...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 text-red-600 p-4 rounded-xl text-sm border border-red-100 flex items-start gap-2">
            <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
            <p>{error}</p>
          </div>
        ) : memories.length === 0 ? (
          <div className="text-center text-sm text-gray-500 py-10">
            No previous memory found.
          </div>
        ) : (
          memories.map((mem, idx) => (
            <MemoryCard 
              key={idx} 
              title={mem.issue_type || 'Interaction'} 
              summary={mem.summary || mem.text || JSON.stringify(mem)} 
              timestamp={mem.created_at || new Date().toISOString()} 
              icon={Brain} 
            />
          ))
        )}
      </div>
    </div>
  );
};

export default MemoryPanel;
