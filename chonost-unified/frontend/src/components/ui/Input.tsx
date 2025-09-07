import React from 'react';

interface InputProps {
  type?: 'text' | 'email' | 'password' | 'textarea';
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  label?: string;
  error?: string;
  className?: string;
  rows?: number;
}

export const Input: React.FC<InputProps> = ({
  type = 'text',
  placeholder,
  value,
  onChange,
  label,
  error,
  className = '',
  rows = 4,
}) => {
  const baseClasses = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200';
  const errorClasses = error ? 'border-red-500 focus:ring-red-500' : '';

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (onChange) {
      onChange(e.target.value);
    }
  };

  return (
    <div className={`mb-4 ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}
      {type === 'textarea' ? (
        <textarea
          className={`${baseClasses} ${errorClasses} resize-vertical`}
          placeholder={placeholder}
          value={value}
          onChange={handleChange}
          rows={rows}
        />
      ) : (
        <input
          type={type}
          className={`${baseClasses} ${errorClasses}`}
          placeholder={placeholder}
          value={value}
          onChange={handleChange}
        />
      )}
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};

