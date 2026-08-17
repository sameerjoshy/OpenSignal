import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { TierBadge, StatusBadge } from "./Badges";

describe("Badges", () => {
  it("renders tier 1 badge", () => {
    render(<TierBadge tier={1} />);
    expect(screen.getByText("Tier 1")).toBeTruthy();
  });

  it("renders unscored for missing tier", () => {
    render(<TierBadge tier={null} />);
    expect(screen.getByText("Unscored")).toBeTruthy();
  });

  it("renders a status badge", () => {
    render(<StatusBadge status="active" />);
    expect(screen.getByText("active")).toBeTruthy();
  });
});