import axios from "axios";

const API_BASE = "https://product-sentiment-analyzer-1-8q4m.onrender.com";

/**
 * Searches for a product and returns its sentiment analysis.
 * Always returns a well-defined shape, even on failure, so components
 * never crash trying to read properties of `undefined`.
 */
export async function searchProduct(query, site = "flipkart") {
  try {
    const res = await axios.get(`${API_BASE}/api/search`, {
      params: { q: query, site },
      timeout: 30000,
    });
    return { data: res.data, error: null };
  } catch (err) {
    const message =
      err.response?.data?.error ||
      err.message ||
      "Something went wrong while searching. Please try again.";
    return { data: null, error: message };
  }
}
