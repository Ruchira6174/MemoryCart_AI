import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
  withCredentials: false,
});

export const sendMessageToBot = async (messageText, userId = 1) => {
  try {
    const response = await api.post('/chat', {
      user_id: userId,
      message: messageText
    });
    
    // Backend returns { response: string }
    const botResponse = response.data.response || 'No response received';
    
    return {
      id: Date.now(),
      sender: 'bot',
      text: botResponse,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
  } catch (error) {
    console.error('Chat API Error:', error);
    throw new Error(error.response?.data?.detail || 'Failed to communicate with AI assistant');
  }
};

export const fetchMemorySummary = async (userId = 1) => {
  try {
    const response = await api.get(`/memory/${userId}`);
    // Backend returns { user_id, memories: [...] }
    return response.data.memories || [];
  } catch (error) {
    console.error('Memory API Error:', error);
    return [];
  }
};

export const fetchOrderDetails = async (orderId) => {
  try {
    const response = await api.get(`/orders/${orderId}`);
    // Backend returns the order object directly
    return response.data;
  } catch (error) {
    console.error(`Order API Error for #${orderId}:`, error);
    return null;
  }
};

export const fetchRefundDetails = async (refundId) => {
  try {
    const response = await api.get(`/refunds/${refundId}`);
    // Backend returns the refund object directly
    return response.data;
  } catch (error) {
    console.error(`Refund API Error for #${refundId}:`, error);
    return null;
  }
};
