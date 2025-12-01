
import React from 'react';

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
    options: { value: string; label: string }[];
}

export const Select: React.FC<SelectProps> = ({ className, options, ...props }) => {
    return (
        <select
            className={`block w-full pl-3 pr-10 py-2 text-base border-slate-300 focus:outline-none focus:ring-slate-500 focus:border-slate-500 sm:text-sm rounded-md shadow-sm ${className}`}
            {...props}
        >
            {options.map(option => (
                <option key={option.value} value={option.value}>
                    {option.label}
                </option>
            ))}
        </select>
    );
};
