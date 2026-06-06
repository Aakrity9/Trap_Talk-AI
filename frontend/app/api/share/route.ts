import { NextResponse } from "next/server";

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);

    // Phone ki share sheet se incoming scam text extraction
    const sharedText = searchParams.get("text") || searchParams.get("title") || "";

    if (!sharedText) {
        return NextResponse.redirect(new URL("/", request.url));
    }

    // Yeh object tumhaare Railway backend pipeline database ke structure se match karta hai
    const payload = {
        sessionId: `session-pwa-${Date.now()}`,
        message: {
            sender: "scammer",
            text: sharedText,
            timestamp: Date.now()
        },
        conversationHistory: [],
        metadata: {
            channel: "PWA_Share_Sheet",
            language: "English",
            locale: "IN"
        }
    };

    try {
        // Railway live cloud backend pointer
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

        await fetch(`${backendUrl}/api/v1/engage`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "x-api-key": "trap_talk_secret_key_2026"
            },
            body: JSON.stringify(payload),
        });

        // Data push karne ke baad user ko live console screen par redirect kar do tracking ke liye
        return NextResponse.redirect(new URL(`/?shared_session=${payload.sessionId}`, request.url));
    } catch (error) {
        console.error("Failed to auto-forward shared scam intel:", error);
        return NextResponse.redirect(new URL("/", request.url));
    }
}