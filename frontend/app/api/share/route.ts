import { NextResponse } from "next/server";

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);

    // Phone ki share sheet se incoming text extract karo
    const sharedText = searchParams.get("text") || searchParams.get("title") || searchParams.get("url") || "";

    if (!sharedText) {
        return NextResponse.redirect(new URL("/", request.url));
    }

    // Ab hum redirect link ke sath text ko safe URL-encoded query parameter banakar bhejenge
    // Isse pure NextJS console page ko direct pata chal jayega ki incoming data kya hai!
    const targetUrl = new URL("/", request.url);
    targetUrl.searchParams.set("shared_text", sharedText);

    return NextResponse.redirect(targetUrl);
}