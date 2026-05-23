import { act, renderHook, waitFor } from "@testing-library/react";

import { useMyPoliticians } from "@/hooks/useMyPoliticians";
import { getMyPoliticianIds } from "@/lib/myPoliticiansStorage";
import { userService } from "@/lib/api/user";
import { mockMp, mockMla } from "@/__tests__/helpers/politicianFixtures";
import type { Politician } from "@/types/politician";

jest.mock("@/lib/api/user", () => ({
  userService: {
    getUserPoliticians: jest.fn(),
  },
}));

const mockedUserService = userService as jest.Mocked<typeof userService>;

function mkPolitician(
  overrides: Partial<Politician> & Pick<Politician, "id" | "type">,
): Politician {
  return {
    political_background: { elections: [] },
    state: "DL",
    constituency: "Delhi",
    name: overrides.id,

    ...overrides,
  };
}

describe("useMyPoliticians", () => {
  beforeEach(() => {
    mockedUserService.getUserPoliticians.mockReset();
    window.localStorage.clear();
  });

  it("hydrates MP/MLA from backend user data", async () => {
    mockedUserService.getUserPoliticians.mockResolvedValueOnce([
      { politician_id: "mp-1", role: "MP" },
      { politician_id: "mla-1", role: "MLA" },
    ]);

    const allPoliticians: Politician[] = [
      mkPolitician({ id: "mp-1", type: "MP" }),
      mkPolitician({ id: "mla-1", type: "MLA" }),
    ];

    const { result } = renderHook(() =>
      useMyPoliticians(allPoliticians, "user-1"),
    );

    await waitFor(() => {
      expect(result.current.myMP?.id).toBe("mp-1");
      expect(result.current.myMLA?.id).toBe("mla-1");
    });
  });

  it("does not call backend when user is unavailable", () => {
    renderHook(() => useMyPoliticians([], undefined));
    expect(mockedUserService.getUserPoliticians).not.toHaveBeenCalled();
  });

  it("keeps local state when getUserPoliticians returns null", async () => {
    mockedUserService.getUserPoliticians.mockResolvedValueOnce(null);

    const { result } = renderHook(() =>
      useMyPoliticians([mockMp], "user-1"),
    );

    await waitFor(() => {
      expect(mockedUserService.getUserPoliticians).toHaveBeenCalled();
    });

    expect(result.current.myMP).toBeNull();
    expect(result.current.myMLA).toBeNull();
  });

  it("persists setMyMP to localStorage", async () => {
    mockedUserService.getUserPoliticians.mockResolvedValueOnce([]);

    const { result } = renderHook(() =>
      useMyPoliticians([mockMp], "user-1"),
    );

    await waitFor(() => {
      expect(mockedUserService.getUserPoliticians).toHaveBeenCalled();
    });

    act(() => {
      result.current.setMyMP(mockMp);
    });

    expect(getMyPoliticianIds()).toEqual({
      mpId: "mp-1",
      mlaId: null,
    });
    expect(result.current.myMP?.id).toBe("mp-1");
  });

  it("persists setMyMLA to localStorage", async () => {
    mockedUserService.getUserPoliticians.mockResolvedValueOnce([]);

    const { result } = renderHook(() =>
      useMyPoliticians([mockMla], "user-1"),
    );

    await waitFor(() => {
      expect(mockedUserService.getUserPoliticians).toHaveBeenCalled();
    });

    act(() => {
      result.current.setMyMLA(mockMla);
    });

    expect(getMyPoliticianIds()).toEqual({
      mpId: null,
      mlaId: "mla-1",
    });
    expect(result.current.myMLA?.id).toBe("mla-1");
  });

  it("clearSlot removes the correct politician slot", async () => {
    mockedUserService.getUserPoliticians.mockResolvedValueOnce([
      { politician_id: "mp-1", role: "MP" },
      { politician_id: "mla-1", role: "MLA" },
    ]);

    const allPoliticians = [mockMp, mockMla];
    const { result } = renderHook(() =>
      useMyPoliticians(allPoliticians, "user-1"),
    );

    await waitFor(() => {
      expect(result.current.myMP?.id).toBe("mp-1");
      expect(result.current.myMLA?.id).toBe("mla-1");
    });

    act(() => {
      result.current.clearSlot("mp");
    });

    expect(result.current.myMP).toBeNull();
    expect(result.current.myMLA?.id).toBe("mla-1");
    expect(getMyPoliticianIds()).toEqual({
      mpId: null,
      mlaId: "mla-1",
    });
  });

  it("fetches politician by id when not in allPoliticians list", async () => {
    mockedUserService.getUserPoliticians.mockResolvedValueOnce([
      { politician_id: "remote-mp", role: "MP" },
    ]);

    const remoteMp: Politician = {
      ...mockMp,
      id: "remote-mp",
      name: "Remote MP",
    };

    ;(global.fetch as jest.Mock).mockImplementation((url: string) => {
      if (String(url).includes("/politicians/remote-mp")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              success: true,
              data: remoteMp,
            }),
        });
      }
      return Promise.reject(new Error(`unexpected url: ${url}`));
    });

    const { result } = renderHook(() => useMyPoliticians([], "user-1"));

    await waitFor(() => {
      expect(result.current.myMP?.id).toBe("remote-mp");
      expect(result.current.myMP?.name).toBe("Remote MP");
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/politicians/remote-mp"),
    );
  });
});
