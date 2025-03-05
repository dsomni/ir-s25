"use client";

import { useCallback, useEffect, useState } from "react";
import axios from "axios";
import styles from "./page.module.css";

interface Proposal {
  document: string;
  score: number;
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [correctedQuery, setCorrectedQuery] = useState<string | null>(null);

  useEffect(() => {}, [query]);

  const handleSearch = useCallback(async (queryInner: string) => {
    setQuery(queryInner);
    if (!queryInner) {
      setProposals([]);
      setCorrectedQuery(null);
      return;
    }

    try {
      const response = await axios.get(
        `${process.env.API_URL}/search?query=${queryInner}`
      );
      setCorrectedQuery(response.data.corrected);
      setProposals(response.data.proposals);
    } catch (error) {
      console.error("Error fetching proposals:", error);
    }
  }, []);

  return (
    <div className={styles.page}>
      <div className={styles.header}>Search</div>
      <div className={styles.inputWrapper}>
        <input
          className={styles.input}
          type="text"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Type to search..."
        />
      </div>
      {!!correctedQuery && <div>Corrected: {correctedQuery}</div>}

      <ul>
        {proposals.map((item, index) => (
          <div key={index}>
            {item.document}, {item.score}
          </div>
        ))}
      </ul>
    </div>
  );
}
