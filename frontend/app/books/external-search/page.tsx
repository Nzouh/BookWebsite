"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

function RedirectContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const query = searchParams.get("query") || "";

    useEffect(() => {
        if (query) {
            router.replace(`/books/search?q=${encodeURIComponent(query)}`);
        } else {
            router.replace("/books/search");
        }
    }, [query, router]);

    return (
        <div style={{ padding: "2rem", textAlign: "center" }}>
            <p>Redirecting to the new search page...</p>
        </div>
    );
}

export default function ExternalSearchPage() {
    return (
        <Suspense fallback={<div>Redirecting...</div>}>
            <RedirectContent />
        </Suspense>
    );
}
