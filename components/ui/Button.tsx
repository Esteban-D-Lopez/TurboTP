
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'outline';
}

export const Button: React.FC<ButtonProps> = ({ children, className, variant = 'primary', ...props }) => {
    const baseStyles = 'inline-flex items-center justify-center px-4 py-2 border text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors';
    
    const variantStyles = {
        primary: 'border-transparent text-white bg-slate-700 hover:bg-slate-800 focus:ring-slate-500',
        outline: 'border-slate-300 text-slate-700 bg-white hover:bg-slate-50 focus:ring-slate-500',
    };

    return (
        <button
            className={`${baseStyles} ${variantStyles[variant]} ${className}`}
            {...props}
        >
            {children}
        </button>
    );
};
