import React, { useState } from 'react';
import { AuthForm } from '../components/auth/AuthForm';

export const AuthPage: React.FC = () => {
  const [mode, setMode] = useState<'login' | 'register'>('login');

  const toggleMode = () => {
    setMode(prev => prev === 'login' ? 'register' : 'login');
  };

  return <AuthForm mode={mode} onToggleMode={toggleMode} />;
};