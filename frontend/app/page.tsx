"use client";

import { useCallback, useState, useEffect, useRef } from "react";
import axios from "axios";
import styles from "./page.module.css";
import Dropdown from '@/components/Dropdown';
import dynamic from 'next/dynamic';

const MatrixBackground = dynamic(
  () => import('@/components/MatrixBackground'),
  { ssr: false }
);

interface Proposal {
  document: string;
  score: number;
}

const indexerOptions = [
  { value: 'word2vec', label: 'Word2Vec' },
  { value: 'inverted_idx', label: 'Inverted Index' },
];

export default function Home() {
  const [query, setQuery] = useState("");
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [correctedQuery, setCorrectedQuery] = useState<string | null>(null);
  const [indexerType, setIndexerType] = useState<string>('word2vec');
  const [isSearching, setIsSearching] = useState(false);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const performSearch = useCallback(async (searchQuery: string, searchIndexer: string) => {
    if (!searchQuery) {
      setProposals([]);
      setCorrectedQuery(null);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    try {
      const response = await axios.get(
        `${process.env.API_URL}/search?query=${searchQuery}&indexer=${searchIndexer}`
      );
      setCorrectedQuery(response.data.corrected);
      setProposals(response.data.proposals);
    } catch (error) {
      console.error("Error fetching proposals:", error);
    } finally {
      setIsSearching(false);
    }
  }, []);

  // Debounced search handler for input changes
  const handleSearchInput = useCallback((newQuery: string) => {
    setQuery(newQuery);

    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // Set new timeout
    searchTimeoutRef.current = setTimeout(() => {
      performSearch(newQuery, indexerType);
    }, 500);
  }, [indexerType, performSearch]);

  // Handle indexer type changes
  const handleIndexerChange = useCallback((newIndexer: string) => {
    setIndexerType(newIndexer);
    // Perform search immediately when indexer changes
    if (query) {
      // Clear any pending debounced search
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
      performSearch(query, newIndexer);
    }
  }, [query, performSearch]);

  // Clean up timeout on unmount
  useEffect(() => {
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div className={styles.page}>
      <MatrixBackground />

      <h1 className={styles.header}>Search</h1>

      <div className={styles.searchRow}>
        <Dropdown
          options={indexerOptions}
          value={indexerType}
          onChange={handleIndexerChange}
        />
        <input
          className={styles.input}
          type="text"
          value={query}
          onChange={(e) => handleSearchInput(e.target.value)}
          placeholder="Type to search..."
        />
        {isSearching && <span className={styles.searchIndicator}>...</span>}
      </div>

      {correctedQuery && correctedQuery != query && (
        <div className={styles.corrected}>
          Did you mean: <span>{correctedQuery}</span>?
        </div>
      )}

      <div className={styles.results}>
        {proposals.map((item, index) => (
          <div key={index} className={styles.resultItem}>
            <a
              href={`/${item.document}`}
              className={styles.document}
            >
              {item.document}
            </a>
            <span className={styles.score}> (score: {item.score.toFixed(2)})</span>
          </div>
        ))}
      </div>
    </div>
  );
}