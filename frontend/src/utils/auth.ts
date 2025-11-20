import axios from 'axios'

/**
 * Initialize axios with authentication
 */
export function initAuth() {
  const token = localStorage.getItem('access_token')
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!localStorage.getItem('access_token')
}

/**
 * Logout user
 */
export function logout() {
  localStorage.removeItem('access_token')
  delete axios.defaults.headers.common['Authorization']
  window.location.href = '/login'
}

/**
 * Get current user info
 */
export async function getCurrentUser() {
  try {
    const response = await axios.get('/api/auth/me')
    return response.data
  } catch (error) {
    logout()
    return null
  }
}
