'use client';

import styles from './Dropdown.module.css';

interface DropdownOption {
    value: string;
    label: string;
}

interface DropdownProps {
    options: DropdownOption[];
    value: string;
    onChange: (value: string) => void;
    className?: string;
}

export default function Dropdown({
    options,
    value,
    onChange,
    className = ''
}: DropdownProps) {
    return (
        <div className={`${styles.container} ${className}`}>
            <div className={styles.selectWrapper}>
                <select
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    className={styles.select}
                >
                    {options.map((option) => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
                <span className={styles.arrow}></span>
            </div>
        </div>
    );
}