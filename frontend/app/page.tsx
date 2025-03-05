"use client";

import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [query, setQuery] = useState("");
  const [proposals, setProposals] = useState([]);

  const handleSearch = async (query: string) => {
    setQuery(query);
    if (!query) {
      setProposals([]);
      return;
    }

    try {
      const response = await axios.get(
        // `http://127.0.0.1:${process.env.BACKEND_PORT}/search?query=${query}`
        `${process.env.API_URL}/search?query=${query}`
      );
      console.log(response);
      setProposals(response.data.proposals);
    } catch (error) {
      console.error("Error fetching proposals:", error);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Search</h1>

      <input
        type="text"
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="Type to search..."
      />

      <ul>
        {proposals.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
