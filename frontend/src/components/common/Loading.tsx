// src/components/common/Loading.tsx
import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  fullHeight?: boolean;
}

export const Loading: React.FC<LoadingProps> = ({
  message = 'Loading...',
  size = 'md',
  fullHeight = false,
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div
      className={`flex flex-col items-center justify-center text-slate-500 py-8 ${
        fullHeight ? 'min-h-[60vh]' : ''
      }`}
    >
      <Loader2 className={`${sizeClasses[size]} animate-spin text-blue-600 mb-3`} />
      <span className="text-sm font-medium tracking-wide text-slate-600">{message}</span>
    </div>
  );
};
export default Loading;
