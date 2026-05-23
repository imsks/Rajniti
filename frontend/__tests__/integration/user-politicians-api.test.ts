/**
 * Integration-style tests for user politician API client roundtrips.
 */
const API_BASE = "http://localhost:8000/api/v1";

type SavedPolitician = { politician_id: string; role: string };

let userService: (typeof import("@/lib/api/user"))["userService"];

function okResponse(data: unknown, status = 200) {
  return { ok: true, status, json: () => Promise.resolve(data) };
}

export {};

function createPoliticiansFetchRouter(initialSaved: SavedPolitician[] = []) {
  const saved = [...initialSaved];

  return (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const method = init?.method ?? "GET";

    if (url.includes("/users/user-1/politicians") && method === "GET") {
      return Promise.resolve(okResponse({ success: true, data: saved }));
    }

    if (url.includes("/users/user-1/politicians") && method === "POST") {
      const body = JSON.parse(String(init?.body)) as SavedPolitician;
      const withoutRole = saved.filter((row) => row.role !== body.role);
      saved.length = 0;
      saved.push(...withoutRole, body);
      return Promise.resolve(okResponse({ success: true }));
    }

    if (url.includes("/users/user-1/politicians/") && method === "DELETE") {
      const politicianId = url.split("/").pop();
      const index = saved.findIndex(
        (row) => row.politician_id === politicianId,
      );
      if (index >= 0) saved.splice(index, 1);
      return Promise.resolve(okResponse({ success: true }));
    }

    return Promise.reject(new Error(`unexpected url: ${url}`));
  };
}

beforeAll(() => {
  process.env.NEXT_PUBLIC_API_URL = API_BASE;
  jest.resetModules();
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  userService = require("@/lib/api/user").userService;
});

beforeEach(() => {
  (global.fetch as jest.Mock).mockReset();
});

describe("user politicians API integration", () => {
  it("add then get returns saved MP", async () => {
    (global.fetch as jest.Mock).mockImplementation(
      createPoliticiansFetchRouter(),
    );

    const addResult = await userService.addUserPolitician(
      "user-1",
      "pol-1",
      "MP",
    );
    expect(addResult).toEqual({ success: true });

    const politicians = await userService.getUserPoliticians("user-1");
    expect(politicians).toEqual([{ politician_id: "pol-1", role: "MP" }]);
  });

  it("upsert replaces MP and keeps MLA", async () => {
    (global.fetch as jest.Mock).mockImplementation(
      createPoliticiansFetchRouter([
        { politician_id: "mp-1", role: "MP" },
        { politician_id: "mla-1", role: "MLA" },
      ]),
    );

    await userService.addUserPolitician("user-1", "mp-2", "MP");

    const politicians = await userService.getUserPoliticians("user-1");
    const byRole = Object.fromEntries(
      (politicians ?? []).map((row) => [row.role, row.politician_id]),
    );

    expect(byRole).toEqual({ MP: "mp-2", MLA: "mla-1" });
  });

  it("remove clears politician from subsequent get", async () => {
    (global.fetch as jest.Mock).mockImplementation(
      createPoliticiansFetchRouter([{ politician_id: "pol-1", role: "MP" }]),
    );

    const removeResult = await userService.removeUserPolitician(
      "user-1",
      "pol-1",
    );
    expect(removeResult).toEqual({ success: true });

    const politicians = await userService.getUserPoliticians("user-1");
    expect(politicians).toEqual([]);
  });

  it("get returns null when backend responds with 500", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: () =>
        Promise.resolve({
          success: false,
          error: "Failed to fetch politicians",
        }),
    });

    const politicians = await userService.getUserPoliticians("user-1");
    expect(politicians).toBeNull();
  });

  it("add returns failure when backend responds with 500", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: () =>
        Promise.resolve({ success: false, error: "Failed to add politician" }),
    });

    const result = await userService.addUserPolitician("user-1", "pol-1", "MP");
    expect(result).toEqual({ success: false });
  });
});
