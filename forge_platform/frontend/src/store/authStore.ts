import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  tenant_id: string;
  is_verified: boolean;
}

type AuthType = 'jwt' | 'token';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  authType: AuthType | null;
  isAuthenticated: boolean;
  
  setAuth: (user: User, accessToken: string, refreshToken: string) => void;
  loginWithToken: (apiToken: string) => Promise<void>;
  loginWithCredentials: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      authType: null,
      isAuthenticated: false,
      
      setAuth: (user, accessToken, refreshToken) => {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        set({ user, accessToken, refreshToken, authType: 'jwt', isAuthenticated: true });
      },
      
      loginWithToken: async (apiToken: string) => {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auth/verify-token`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiToken}`,
          },
        });
        
        if (!response.ok) {
          throw new Error('Invalid token');
        }
        
        const data = await response.json();
        localStorage.setItem('access_token', apiToken);
        set({ 
          user: data.user, 
          accessToken: apiToken, 
          refreshToken: null,
          authType: 'token',
          isAuthenticated: true 
        });
      },
      
      loginWithCredentials: async (email: string, password: string) => {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });
        
        if (!response.ok) {
          throw new Error('Invalid credentials');
        }
        
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        set({ 
          user: data.user, 
          accessToken: data.access_token, 
          refreshToken: data.refresh_token,
          authType: 'jwt',
          isAuthenticated: true 
        });
      },
      
      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ 
          user: null, 
          accessToken: null, 
          refreshToken: null, 
          authType: null,
          isAuthenticated: false 
        });
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
