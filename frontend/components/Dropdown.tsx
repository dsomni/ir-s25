'use client'; // Mark as Client Component

import { useState } from 'react';
import styles from './Dropdown.module.css'; // Optional CSS module

interface DropdownOption {
    value: string;
    label: string;
}

interface DropdownProps {
    options: DropdownOption[];
    initialValue?: string;
    label?: string;
    onChange: (value: string) => void;
    className?: string;
}

export default function Dropdown({
    options,
    initialValue = '',
    label,
    onChange,
    className = ''
}: DropdownProps) {
    const [selectedValue, setSelectedValue] = useState(initialValue);

    const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const value = e.target.value;
        setSelectedValue(value);
        onChange(value);
    };

    return (
        <div className={`${styles.container} ${className}`}>
            {label && <label className={styles.label}>{label}</label>}
            <select
                value={selectedValue}
                onChange={handleChange}
                className={styles.select}
            >
                {options.map((option) => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
        </div>
    );
}