"use client";

import { useEffect, useState } from "react";
import styles from "./chat.module.css";
import axios from "axios";
import { useRef } from "react";
import Dropdown from '@/components/Dropdown';
import BackLink from "@/components/BackLink";


interface Proposal {
    document: string;
    score: number;
}

export default function ChatPage() {
    const [prompt, setPrompt] = useState("");
    const [kValue, setKValue] = useState("5");
    const [proposals, setProposals] = useState<Proposal[]>([]);
    const [showValues, setShowValues] = useState(false);
    const [model, setModel] = useState("");
    const [modelList, setModelList] = useState<string[]>([]);
    const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
    const [streamingResponse, setStreamingResponse] = useState("");
    const [error, setError] = useState("");
    const chatEndRef = useRef<HTMLDivElement | null>(null);
    const textareaRef = useRef<HTMLTextAreaElement | null>(null);

    // Resize textarea height dynamically
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
        }
    }, [prompt]);

    useEffect(() => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages, streamingResponse]);

    useEffect(() => {
        const fetchModels = async () => {
            try {
                const response = await axios.get(`${process.env.API_URL}/models`);
                setModelList(response.data || []);
                if (response.data.length > 0) setModel(response.data[0]); // default to first
            } catch (err) {
                console.error("Failed to fetch models", err);
                setError("Unable to load model list.");
            }
        };

        fetchModels();
    }, []);

    const handleSubmit = async () => {
        if (!prompt.trim()) return;
        setError("");

        // Append user message
        setMessages(prev => [...prev, { role: "user", content: prompt }]);
        setStreamingResponse("");
        setError("");
        const currentPrompt = prompt;
        setPrompt("");
        let current = "";

        try {
            const response = await fetch(
                `${process.env.API_URL}/chat?prompt=${encodeURIComponent(currentPrompt)}&k=${kValue}&model=${model}`
            );

            if (!response.ok || !response.body) {
                throw new Error("Failed to connect to backend or response body is missing.");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const messages = chunk.split('\n\n').filter(m => m.trim() !== '');
                console.log(messages)
                for (const message of messages) {
                    try {
                        const parsed = JSON.parse(message);

                        switch (parsed.type) {
                            case 'proposals':
                                setProposals(parsed.data);
                                break;
                            case 'chunk':
                                current += parsed.data;
                                setStreamingResponse(current);
                                break;
                            case 'complete':
                                setStreamingResponse("");
                                break;
                            case 'error':
                                setError(parsed.data || "Unknown error");
                                return;
                            default:
                                console.warn('Unknown message type:', parsed.type);
                        }
                    } catch (e) {
                        console.error('Error parsing message:', e);
                        return;
                    }
                }
            }

            setStreamingResponse("");
            setMessages(prev => [...prev, { role: "model", content: current }]);
        } catch (err) {
            console.error("Error during chat request:", err);
            setError("Error: " + (err instanceof Error ? err.message : "Unknown error"));
        }
    };

    return (
        <div className={styles.page}>
            <h1 className={styles.header}>Chat</h1>

            <div className={styles.controls}>
                <Dropdown
                    options={[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(i => ({ label: `k = ${i}`, value: i.toString() }))}
                    value={kValue}
                    onChange={(newValue) => setKValue(newValue)}
                />

                <Dropdown
                    options={modelList.map(m => ({ label: m, value: m }))}
                    value={model}
                    onChange={(newValue) => setModel(newValue)}
                />

            </div>

            <div className={styles.chatBox}>
                {messages.map((msg, idx) => (
                    <div key={idx} className={msg.role === "user" ? styles.userMsg : styles.modelMsg}>
                        <div className={styles.role}><strong>{msg.role === "user" ? "YOU" : model.toUpperCase()}</strong></div>
                        <div>{msg.content}</div>
                    </div>
                ))}

                {streamingResponse && (
                    <div className={styles.modelMsg}>
                        <div className={styles.role}><strong>{model.toUpperCase()}</strong></div>
                        <div>{streamingResponse}</div>
                    </div>
                )}
                <div ref={chatEndRef} />
            </div>

            <div className={styles.inputRow}>
                <textarea
                    ref={textareaRef}
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                            e.preventDefault();
                            handleSubmit();
                        }
                    }}
                    placeholder="Type your message..."
                    className={styles.textarea}

                />

                <button onClick={handleSubmit} className={styles.sendButton}>
                    Send
                </button>
            </div>

            {error && <div className={styles.error}>{error}</div>}


            {proposals.length > 0 && !!!error && (
                <div className={styles.valuesSection}>
                    <button
                        onClick={() => setShowValues((prev) => !prev)}
                        className={styles.toggleButton}
                    >
                        {showValues ? "Hide" : "Show last proposals"}
                    </button>

                    {showValues && <div className={styles.results}>
                        {proposals.map((item, index) => (
                            <div key={index} className={styles.resultItem}>
                                <a
                                    href={`doc/${item.document}`}
                                    className={styles.document}
                                >
                                    {item.document}
                                </a>
                                <span className={styles.score}> (score: {item.score.toFixed(2)})</span>
                            </div>
                        ))}
                    </div>}
                </div>
            )}

            <BackLink href="/" />

        </div>
    );
}
