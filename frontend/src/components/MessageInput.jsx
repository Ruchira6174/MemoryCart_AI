import React, { useState } from 'react';
import { Send, Paperclip, Mic, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

export const MessageInput = ({ onSendMessage, isDisabled }) => {
  const [text, setText] = useState('');

  const suggestionChips = [
    { label: "What is your return policy?", query: "What is your return policy?" },
    { label: "When will my order arrive?", query: "When will my order arrive?" },
    { label: "Check refund status", query: "Check refund status of RF-881" }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || isDisabled) return;
    onSendMessage(text);
    setText('');
  };

  const handleChipClick = (query) => {
    if (isDisabled) return;
    onSendMessage(query);
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-6 pt-2">
      <div className="flex flex-wrap gap-2 mb-3 justify-center md:justify-start">
        {suggestionChips.map((chip, index) => (
          <motion.button
            key={index}
            type="button"
            onClick={() => handleChipClick(chip.query)}
            disabled={isDisabled}
            whileHover={{ y: -1, scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="text-xs px-3.5 py-1.5 rounded-full border border-gray-200 bg-white text-gray-600 hover:bg-gray-50 hover:text-black hover:border-gray-300 transition-colors shadow-sm cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {chip.label}
          </motion.button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center bg-white border border-gray-200 rounded-2xl p-2 pl-4 pr-3 transition-all duration-200 focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-100 shadow-sm">
          <button type="button" className="p-2 rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-50 transition-colors cursor-pointer" title="Attach files (UI Only)">
            <Paperclip size={18} />
          </button>
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Ask MemoryCart AI about order status, refunds, or store policies..."
            disabled={isDisabled}
            className="flex-1 bg-transparent border-0 text-black placeholder-gray-400 focus:ring-0 focus:outline-none text-sm px-3 py-2 disabled:opacity-50"
          />
          <div className="flex items-center gap-1.5">
            <button type="button" className="p-2 rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-50 transition-colors cursor-pointer" title="Voice input (UI Only)">
              <Mic size={18} />
            </button>
            <motion.button
              type="submit"
              disabled={!text.trim() || isDisabled}
              whileHover={text.trim() && !isDisabled ? { scale: 1.05 } : {}}
              whileTap={text.trim() && !isDisabled ? { scale: 0.95 } : {}}
              className={`p-2.5 rounded-xl flex items-center justify-center transition-all duration-200 cursor-pointer ${
                text.trim() && !isDisabled
                  ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm'
                  : 'bg-gray-50 text-gray-300 cursor-not-allowed border border-gray-100'
              }`}
            >
              <Send size={14} />
            </motion.button>
          </div>
        </div>
        <div className="text-[10px] text-center text-gray-400 mt-2 flex items-center justify-center gap-1.5 select-none font-medium">
          <Sparkles size={10} className="text-indigo-500" />
          <span>MemoryCart AI uses customer memory to contextualize and personalize answers.</span>
        </div>
      </form>
    </div>
  );
};

export default MessageInput;
