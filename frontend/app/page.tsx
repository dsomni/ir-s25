"use client";

import styles from "./page.module.css";
import Link from "next/link";
import "./globals.css"; // Ensure matrix variables are loaded


export default function Home() {
  return (
    <div className={styles.page}>

      <header className={styles.header}>PyFinder</header>

      <div className={styles.links}>
        <Link href="/search" className={styles.bigLink}>
          Go to search
        </Link>
        <Link href="/chat" className={styles.bigLink}>
          Start chatting
        </Link>

        <p className={styles.authors}>Created by dsomni, adbedlam and kiaver</p>
      </div>

      <Link href="https://github.com/dsomni/ir-s25" target="_blank" className={styles.githubLink}>
        Check our GitHub!
      </Link>
    </div>
  );
}
