import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Sparkles, RefreshCw, ShoppingCart } from 'lucide-react';
import ChatWindow from '../components/ChatWindow';
import MessageInput from '../components/MessageInput';
import MemoryPanel from '../components/MemoryPanel';
import { sendMessageToBot } from '../services/api';

export const ChatPage = () => {
  const [messages, setMessages] = useState([{
    id: Date.now(),
    sender: 'bot',
    text: "Hello! I am MemoryCart AI, your e-commerce personal support assistant. I remember our past conversations to help you faster. How can I assist you with your orders, refunds, or policies today?",
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  }]);
  const [isTyping, setIsTyping] = useState(false);
  const [isMemoryOpen, setIsMemoryOpen] = useState(true);
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);

  const handleSendMessage = async (text) => {
    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const botResponse = await sendMessageToBot(text);
      setMessages((prev) => [...prev, botResponse]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [...prev, {
        id: Date.now(),
        sender: 'bot',
        text: "I'm having trouble connecting right now. Please try again later.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleResetChat = () => {
    setMessages([{
      id: Date.now(),
      sender: 'bot',
      text: "Hello! I am MemoryCart AI. How can I assist you with your orders, refunds, or policies today?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }]);
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-white text-black overflow-hidden font-sans relative">
      <header className="h-16 border-b border-gray-200 bg-white flex items-center justify-between px-6 z-20 flex-shrink-0">
        <div className="flex items-center gap-3 select-none">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-600">
              <ShoppingCart size={18} />
            </div>
            <span className="font-bold tracking-tight text-base text-black">
              MemoryCart <span className="text-indigo-600 font-semibold">AI</span>
            </span>
          </div>
          <div className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-indigo-50 border border-indigo-100 text-[10px] font-semibold text-indigo-600">
            <Sparkles size={10} />
            <span>AI ASSISTANT</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-100 text-emerald-700 text-[10px] font-semibold select-none">
            <span className="relative flex h-1.5 w-1.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
            </span>
            <span>Memory Active</span>
          </div>
          <button onClick={handleResetChat} className="p-2 rounded-lg text-gray-400 hover:text-black hover:bg-gray-100 transition-colors cursor-pointer" title="Reset Chat">
            <RefreshCw size={15} />
          </button>
          <button onClick={() => setIsMemoryOpen(!isMemoryOpen)} className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-200 text-gray-700 hover:bg-gray-50 hover:text-black transition-colors text-xs font-semibold cursor-pointer">
            <Brain size={14} className="text-indigo-600" />
            <span>{isMemoryOpen ? 'Hide Memory' : 'Show Memory'}</span>
          </button>
          <button onClick={() => setIsMobileDrawerOpen(true)} className="flex md:hidden items-center gap-2 p-2 rounded-lg border border-gray-200 text-gray-700 hover:bg-gray-50 hover:text-black transition-colors cursor-pointer" title="Open Memory">
            <Brain size={16} className="text-indigo-600" />
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative bg-white">
        <main className={`flex flex-col h-full bg-white transition-all duration-300 ease-in-out ${isMemoryOpen ? 'w-full md:w-[70%]' : 'w-full'}`}>
          <ChatWindow messages={messages} isTyping={isTyping} onSendMessage={handleSendMessage} />
          <MessageInput onSendMessage={handleSendMessage} isDisabled={isTyping} />
        </main>
        
        <aside className={`hidden md:block h-full transition-all duration-300 ease-in-out flex-shrink-0 ${isMemoryOpen ? 'w-[30%] opacity-100 border-l border-gray-200' : 'w-0 opacity-0 overflow-hidden pointer-events-none'}`}>
          <MemoryPanel />
        </aside>

        <AnimatePresence>
          {isMobileDrawerOpen && (
            <>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 0.4 }} exit={{ opacity: 0 }} onClick={() => setIsMobileDrawerOpen(false)} className="absolute inset-0 bg-black z-30 md:hidden cursor-pointer" />
              <motion.div initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }} transition={{ type: 'spring', damping: 26, stiffness: 220 }} className="absolute right-0 top-0 bottom-0 w-[80%] max-w-xs z-40 md:hidden shadow-lg bg-white">
                <MemoryPanel onClose={() => setIsMobileDrawerOpen(false)} />
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ChatPage;
