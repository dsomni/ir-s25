"use client";

import { useEffect, useState } from 'react';
import styles from './MatrixBackground.module.css';

const MatrixBackground = () => {
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    if (!isMounted) return null;

    const chars = "0123456789"; // More varied characters
    const columns = 40; // Fewer but more visible columns

    return (
        <div className={styles.matrixBackground}>
            {Array.from({ length: columns }).map((_, i) => (
                <div
                    key={i}
                    className={styles.matrixColumn}
                    style={{
                        animationDuration: `${Math.random() * 8 + 8}s`, // Slower animation
                        animationDelay: `${Math.random() * 5}s`,
                        left: `${i * 2.5}%` // Better spacing
                    }}
                >
                    {Array.from({ length: 20 }).map((_, j) => (
                        <div
                            key={j}
                            className={styles.matrixChar}
                            style={{
                                color: Math.random() > 0.5 ? 'var(--matrix-accent)' : 'var(--matrix-secondary)', // Brighter colors
                                opacity: Math.random() * 0.7 + 0.3 // More visible
                            }}
                        >
                            {chars.charAt(Math.floor(Math.random() * chars.length))}
                        </div>
                    ))}
                </div>
            ))}
        </div>
    );
};

export default MatrixBackground;