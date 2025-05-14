'use client';

import axios from "axios";
import { notFound } from "next/navigation";
import styles from './DocumentPage.module.css';
import dynamic from 'next/dynamic';
import Link from "next/link";
import { useEffect, useState } from "react";
import { use } from "react";

async function fetchDocument(documentName: string) {
    try {
        const response = await axios.get(
            `${process.env.API_URL}/document?name=${documentName}`
        );
        console.log("Document response:", response.data);
        return response.data;
    } catch (err) {
        console.error("Error fetching document:", err);
        return null;
    }
}

export default function DocumentPage({
    params,
}: {
    params: Promise<{ document: string }>;
}) {
    // Unwrap the params Promise
    const { document: documentName } = use(params);
    const [document, setDocument] = useState<{
        name: string;
        element_type: string;
        full_name: string;
        module_name: string;
        parameters: string;
        description: string;
    } | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function loadDocument() {
            try {
                setLoading(true);
                const doc = await fetchDocument(documentName);
                if (!doc) {
                    notFound();
                }
                setDocument(doc);
            } catch (err) {
                console.error("Error loading document:", err);
                setError("Failed to load document");
            } finally {
                setLoading(false);
            }
        }

        loadDocument();
    }, [documentName]);

    if (loading) {
        return (
            <div className={styles.container}>
                <MatrixBackground />
                <div className={styles.loading}>Loading document...</div>
            </div>
        );
    }

    if (error || !document) {
        return (
            <div className={styles.container}>
                <MatrixBackground />
                <div className={styles.error}>
                    {error || "Document not found"}
                    <div className={styles.backLink}>
                        <Link href="/">← Back to Search</Link>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>

            <div className={styles.documentCard}>
                <div className={styles.header}>
                    <span className={styles.elementType}>{document.element_type}</span>
                    <h1 className={styles.title}>
                        {document.full_name} <span className={styles.from}>from</span> {document.module_name}
                    </h1>
                </div>

                {document.parameters && (
                    <div className={styles.section}>
                        <h2 className={styles.sectionTitle}>PARAMETERS</h2>
                        <pre className={styles.parameters}>
                            {document.parameters}
                        </pre>
                    </div>
                )}

                {document.description && <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>DESCRIPTION</h2>
                    <div className={styles.description}>
                        {document.description.split('\n').map((para, i) => (
                            <p key={i}>{para}</p>
                        ))}
                    </div>
                </div>}

                <div className={styles.backLink}>
                    <Link href="/search">← Back to Search</Link>
                </div>
            </div>
        </div>
    );
}

const MatrixBackground = dynamic(
    () => import('@/components/MatrixBackground'),
    { ssr: false }
);