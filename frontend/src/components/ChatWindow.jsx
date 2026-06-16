import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, User, MessageSquare, ArrowRight } from 'lucide-react';

export const ChatWindow = ({ messages, isTyping, onSendMessage }) => {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const emptyStateCards = [
    { title: "Policy Questions", description: "Ask about store returns, shipment rules, or FAQ.", example: "What is your return policy?" },
    { title: "Order Tracking", description: "Track shipment progress and check delivery estimates.", example: "Where is Order 1?" },
    { title: "Refund Tracking", description: "Check the status and amounts of transaction refunds.", example: "What is the status of Refund 1?" }
  ];

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 select-text bg-white">
      {messages.length === 0 ? (
        <div className="max-w-3xl mx-auto py-10 px-4 space-y-8">
          <div className="text-center space-y-3">
            <div className="inline-flex p-3 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-600 mb-2">
              <MessageSquare size={28} />
            </div>
            <h3 className="text-xl font-bold text-black tracking-tight">MemoryCart AI Assistant</h3>
            <p className="text-sm text-gray-500 max-w-lg mx-auto leading-relaxed">
              Welcome to your intelligent support terminal. I track store policies, orders, refunds, and remember details across sessions to avoid repetitive questions.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {emptyStateCards.map((card, idx) => (
              <motion.div key={idx} whileHover={{ y: -2 }} className="bg-[#FAFAFA] border border-gray-200 rounded-xl p-4 text-left transition-all duration-200 flex flex-col justify-between">
                <div>
                  <h4 className="text-xs font-bold text-indigo-700 uppercase tracking-wider mb-1">{card.title}</h4>
                  <p className="text-xs text-gray-500 leading-relaxed mb-4">{card.description}</p>
                </div>
                <button onClick={() => onSendMessage && onSendMessage(card.example)} className="w-full mt-auto text-left py-2 px-3 bg-white border border-gray-200 rounded-lg text-xs text-gray-700 hover:bg-gray-50 hover:text-black font-medium transition-colors flex items-center justify-between group cursor-pointer">
                  <span>"{card.example}"</span>
                  <ArrowRight size={12} className="text-gray-400 group-hover:text-black group-hover:translate-x-0.5 transition-all" />
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      ) : (
        <div className="max-w-3xl mx-auto space-y-6">
          <AnimatePresence initial={false}>
            {messages.map((message) => {
              const isBot = message.sender === 'bot';
              return (
                <motion.div key={message.id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className={`flex items-start gap-3.5 ${isBot ? 'justify-start' : 'justify-end'}`}>
                  {isBot && (
                    <div className="p-2 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-600 flex-shrink-0 mt-0.5">
                      <Bot size={16} />
                    </div>
                  )}
                  <div className={`max-w-[80%] space-y-1.5 ${!isBot ? 'order-1' : 'order-2'}`}>
                    <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${isBot ? 'bg-white border border-gray-200 text-black shadow-sm' : 'bg-black text-white font-normal'}`}>
                      <p className="whitespace-pre-line">{message.text}</p>
                    </div>
                    <div className={`text-[9px] font-semibold uppercase tracking-wider text-gray-400 px-1 ${isBot ? 'text-left' : 'text-right'}`}>
                      {message.timestamp}
                    </div>
                  </div>
                  {!isBot && (
                    <div className="p-2 rounded-lg bg-gray-100 border border-gray-200 text-gray-700 flex-shrink-0 mt-0.5 order-3">
                      <User size={16} />
                    </div>
                  )}
                </motion.div>
              );
            })}
          </AnimatePresence>
          {isTyping && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex items-start gap-3.5 justify-start">
              <div className="p-2 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-600 flex-shrink-0">
                <Bot size={16} />
              </div>
              <div className="bg-white border border-gray-200 text-black px-4 py-3 rounded-2xl flex items-center space-x-1 shadow-sm">
                <span className="text-xs text-gray-400 mr-2 font-medium">MemoryCart AI is typing</span>
                <motion.span animate={{ y: [0, -3, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0 }} className="w-1.5 h-1.5 bg-gray-400 rounded-full inline-block" />
                <motion.span animate={{ y: [0, -3, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.15 }} className="w-1.5 h-1.5 bg-indigo-400 rounded-full inline-block" />
                <motion.span animate={{ y: [0, -3, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.3 }} className="w-1.5 h-1.5 bg-gray-600 rounded-full inline-block" />
              </div>
            </motion.div>
          )}
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
