import axios from "axios";
import { notFound } from "next/navigation";

interface Document {
    name: string;
    content: string;
}

async function getDocument(documentName: string): Promise<Document | null> {
    try {
        const response = await axios.get(
            `${process.env.API_URL}/document?name=${documentName}`
        );
        return response.data;
    } catch (error) {
        console.error("Error fetching document:", error);
        return null;
    }
}

export default async function DocumentPage({
    params,
}: {
    params: { document: string };
}) {

    const { document: documentName } = await params
    const document = await getDocument(documentName);

    if (!document) {
        notFound();
    }

    return (
        <div>
            <div>{document.name}</div>
            {document.content}
        </div>
    );
}