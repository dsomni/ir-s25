"use client";

import { useCallback, useState } from "react";
import axios from "axios";
import styles from "./page.module.css";
import Dropdown from '@/components/Dropdown';

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



  const handleSearch = useCallback(async (queryInner: string) => {
    setQuery(queryInner);
    if (!queryInner) {
      setProposals([]);
      setCorrectedQuery(null);
      return;
    }

    try {
      const response = await axios.get(
        `${process.env.API_URL}/search?query=${queryInner}&indexer=${indexerType}`
      );
      setCorrectedQuery(response.data.corrected);
      setProposals(response.data.proposals);
    } catch (error) {
      console.error("Error fetching proposals:", error);
    }
  }, [indexerType]);

  return (
    <div className={styles.page}>
      <div className={styles.header}>Search</div>
      <Dropdown
        options={indexerOptions}
        initialValue="word2vec"
        onChange={setIndexerType}
      />
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
            <a href={`/${item.document}`}>{item.document}</a>, {item.score}
          </div>
        ))}
      </ul>
    </div>
  );
}
