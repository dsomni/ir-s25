"use client";

import { useCallback, useState, useEffect, useRef } from "react";
import axios from "axios";
import styles from "./search.module.css";
import Dropdown from '@/components/Dropdown';
import BackLink from "@/components/BackLink";
import { indexerMap, Proposal } from "@/constants";

export default function Search() {
  const [query, setQuery] = useState("");
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [correctedQuery, setCorrectedQuery] = useState<string | null>(null);
  const [error, setError] = useState("");

  const [indexer, setIndexer] = useState("");
  const [indexerList, setIndexerList] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);


  useEffect(() => {
    const fetchIndexers = async () => {
      try {
        const response = await axios.get(`${process.env.API_URL}/indexers`);
        setIndexerList(response.data || []);
        if (response.data.length > 0) setIndexer(response.data[0]); // default to first
      } catch (err) {
        console.error("Failed to fetch indexers", err);
        setError("Unable to load indexer list");
      }
    };

    fetchIndexers();
  }, []);

  const performSearch = useCallback(async (searchQuery: string, searchIndexer: string) => {
    setError("");
    if (!searchQuery) {
      setProposals([]);
      // setCorrectedQuery(null);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    try {
      const response = await axios.get(
        `${process.env.API_URL}/search?query=${searchQuery}&indexer=${searchIndexer}`
      );
      const corrected = response.data.corrected;
      if (corrected && corrected !== searchQuery) {
        setCorrectedQuery(corrected);
      } else {
        setCorrectedQuery(null);
      }
      setProposals(response.data.proposals);
    } catch (error) {
      console.error("Error fetching proposals:", error);
      setError("Error fetching proposals: " + error);
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
      performSearch(newQuery, indexer);
    }, 500);
  }, [indexer, performSearch]);

  // Handle indexer type changes
  const handleIndexerChange = useCallback((newIndexer: string) => {
    setIndexer(newIndexer);
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

      <h1 className={styles.header}>Search</h1>

      <div className={styles.searchRow}>
        <Dropdown
          options={indexerList.map(value => ({ value: value, label: indexerMap.get(value)! }))}
          value={indexer}
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


      {error && <div className={styles.error}>{error}</div>}

      {correctedQuery && (
        <div className={styles.corrected}>
          Did you mean: <span>{correctedQuery}</span>?
        </div>
      )}

      <div className={styles.results}>
        {proposals.map((item, index) => (
          <div key={index} className={styles.resultItem}>
            <a
              href={`doc/${item.document}`}
              className={styles.document}
              target="_blank"

            >
              {item.document}
            </a>
            <span className={styles.score}> (score: {item.score.toFixed(2)})</span>
          </div>
        ))}
      </div>
      <BackLink href="/" />

    </div>
  );
}