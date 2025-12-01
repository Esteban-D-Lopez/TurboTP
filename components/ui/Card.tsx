
import React from 'react';

interface CardProps {
    children: React.ReactNode;
    className?: string;
}

export const Card: React.FC<CardProps> = ({ children, className }) => {
    return (
        <div className={`bg-white border border-slate-200 rounded-lg shadow-sm ${className}`}>
            {children}
        </div>
    );
};
