import { render, screen } from "@testing-library/react"
import Home from "@/app/page"

describe("Homepage sections visibility", () => {
    it("keeps key below-the-fold sections visible on initial render", () => {
        render(<Home />)

        expect(
            screen.getByRole("heading", { name: "What You'll Find" })
        ).toBeVisible()
        expect(screen.getByRole("heading", { name: "Contribute Data" })).toBeVisible()
    })
})
