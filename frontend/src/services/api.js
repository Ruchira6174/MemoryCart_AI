/**
 * api.js — MemoryCart AI frontend API service layer.
 *
 * All backend calls go through this module so the base URL is
 * defined in one place and can be swapped via an env variable.
 */

const BASE_URL = import.meta.env?.VITE_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
async function handleResponse(res) {
  const payload = await res.json().catch(() => null);

  if (!res.ok) {
    const detail = (payload && (payload.detail || payload.message)) || res.statusText;
    throw new Error(detail || `HTTP ${res.status}`);
  }

  // Support unified backend responses: { response, data, status }
  if (payload && typeof payload === "object" && "status" in payload && "data" in payload) {
    if (payload.status === "success") return payload; // return full payload so callers can access response + data
    const msg = payload.response || "Request failed";
    throw new Error(msg);
  }

  // Fallback: return raw payload
  return payload;
}

// ---------------------------------------------------------------------------
// Chat
// ---------------------------------------------------------------------------

/**
 * Send a user message to the AI agent.
 * @param {number} userId
 * @param {string} message
 * @returns {Promise<{ response: string, data: object, status: string }>}
 */
export async function sendMessage(userId, message) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, message }),
  });
  return handleResponse(res);
}

// ---------------------------------------------------------------------------
// Memory
// ---------------------------------------------------------------------------

/**
 * Retrieve memory history for a user (returns [] for new users).
 * @param {number} userId
 * @returns {Promise<Array<{ memory_id, summary, issue_type, created_at }>>}
 */
export async function getMemory(userId) {
  const res = await fetch(`${BASE_URL}/memory/${userId}`);
  return handleResponse(res);
}

// ---------------------------------------------------------------------------
// Orders
// ---------------------------------------------------------------------------

/**
 * Retrieve order details by order ID.
 * @param {number} orderId
 * @returns {Promise<{ order_id, user_id, product_name, status, delivery_date }>}
 */
export async function getOrder(orderId) {
  const res = await fetch(`${BASE_URL}/orders/${orderId}`);
  return handleResponse(res);
}

// ---------------------------------------------------------------------------
// Refunds
// ---------------------------------------------------------------------------

/**
 * Retrieve refund details by refund ID.
 * @param {number} refundId
 * @returns {Promise<{ refund_id, order_id, status, amount }>}
 */
export async function getRefund(refundId) {
  const res = await fetch(`${BASE_URL}/refunds/${refundId}`);
  return handleResponse(res);
}
