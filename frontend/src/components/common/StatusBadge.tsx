// src/components/common/StatusBadge.tsx
import React from 'react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'sm' }) => {
  const norm = status?.toUpperCase() || '';

  const getStyle = (s: string) => {
    switch (s) {
      // Experience & Document statuses
      case 'APPROVED':
      case 'READY':
      case 'RESOLVED':
      case 'REVIEWED':
      case 'POSITIVE':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200/80';

      case 'PENDING':
      case 'PROCESSING':
      case 'OPEN':
        return 'bg-amber-50 text-amber-700 border-amber-200/80';

      case 'IN_PROGRESS':
        return 'bg-blue-50 text-blue-700 border-blue-200/80';

      case 'REJECTED':
      case 'FAILED':
      case 'NEGATIVE':
      case 'ESCALATED':
        return 'bg-rose-50 text-rose-700 border-rose-200/80';

      case 'DISMISSED':
      case 'CLOSED':
        return 'bg-slate-100 text-slate-600 border-slate-200';

      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs font-semibold';

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border ${getStyle(
        norm
      )} ${sizeClasses} whitespace-nowrap tracking-wide`}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-80" />
      {norm}
    </span>
  );
};
export default StatusBadge;
