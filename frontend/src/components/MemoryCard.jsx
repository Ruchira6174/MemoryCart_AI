import React from 'react';
import { motion } from 'framer-motion';

export const MemoryCard = ({ title, summary, timestamp, icon: Icon }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {Icon && (
            <div className="p-1.5 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-600">
              <Icon size={16} />
            </div>
          )}
          <span className="text-xs font-bold text-gray-700 uppercase tracking-wider">{title}</span>
        </div>
        {timestamp && (
          <span className="text-[10px] text-gray-400 font-medium">
            {new Date(timestamp).toLocaleDateString()}
          </span>
        )}
      </div>
      <p className="text-sm text-gray-600 leading-relaxed">{summary}</p>
    </motion.div>
  );
};

export default MemoryCard;
