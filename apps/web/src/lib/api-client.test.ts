import { describe, expect, it } from "vitest";
import { API_URL, ApiError } from "@/lib/api-client";

describe("api-client", () => {
  it("uses NEXT_PUBLIC_API_URL or localhost default", () => {
    expect(API_URL).toBeTruthy();
    expect(typeof API_URL).toBe("string");
  });

  it("creates ApiError with status", () => {
    const err = new ApiError("Not found", 404);
    expect(err.name).toBe("ApiError");
    expect(err.status).toBe(404);
    expect(err.message).toBe("Not found");
  });
});
