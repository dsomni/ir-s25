'use client';

import styles from './BackLink.module.css';
import Link from "next/link";


interface BackLinkProps {
    label?: string;
    href: string;
}

export default function BackLink({
    label,
    href,
}: BackLinkProps) {
    return (
        <div className={styles.backLink}>
            <Link href={href}>← {label || 'Back'}</Link>
        </div>
    );
}