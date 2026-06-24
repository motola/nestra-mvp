import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BluetoothPairingModal } from "@/components/integrations/bluetooth-pairing-modal";

// Mock Web Bluetooth API
const mockBluetoothDevice = {
  name: "Test Light",
  id: "AA:BB:CC:DD:EE:FF",
  gatt: {
    connect: vi.fn(),
  },
};

const mockRequestDevice = vi.fn();

describe("BluetoothPairingModal", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    // Mock navigator.bluetooth
    Object.defineProperty(navigator, "bluetooth", {
      value: {
        requestDevice: mockRequestDevice,
      },
      configurable: true,
    });

    mockRequestDevice.mockClear();
  });

  function renderModal(onSuccess?: () => void, onCancel?: () => void) {
    return render(
      <QueryClientProvider client={queryClient}>
        <BluetoothPairingModal
          propertyId="550e8400-e29b-41d4-a716-446655440000"
          onSuccess={onSuccess}
          onCancel={onCancel}
        />
      </QueryClientProvider>,
    );
  }

  it("renders initial state with scan button", () => {
    renderModal();

    expect(screen.getByText("Pair Bluetooth Device")).toBeDefined();
    expect(
      screen.getByText(/scan for nearby bluetooth devices/i),
    ).toBeDefined();
    expect(screen.getByRole("button", { name: /scan devices/i })).toBeDefined();
  });

  it("shows scanning state when scan is clicked", async () => {
    mockRequestDevice.mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(() => resolve(mockBluetoothDevice), 100);
        }),
    );

    renderModal();

    const scanButton = screen.getByRole("button", { name: /scan devices/i });
    fireEvent.click(scanButton);

    expect(screen.getByText(/scanning for bluetooth devices/i)).toBeDefined();

    await waitFor(() => {
      expect(screen.getByText(/found 1 device/i)).toBeDefined();
    });
  });

  it("displays found devices in selecting state", async () => {
    mockRequestDevice.mockResolvedValue(mockBluetoothDevice);

    renderModal();

    fireEvent.click(screen.getByRole("button", { name: /scan devices/i }));

    await waitFor(() => {
      expect(screen.getByText("Test Light")).toBeDefined();
      expect(screen.getByText(/AA:BB:CC:DD:EE:FF/)).toBeDefined();
    });
  });

  it("handles scan errors gracefully", async () => {
    mockRequestDevice.mockRejectedValue(
      new DOMException("User cancelled", "NotFoundError"),
    );

    renderModal();

    fireEvent.click(screen.getByRole("button", { name: /scan devices/i }));

    await waitFor(() => {
      expect(screen.getByText(/no bluetooth devices found/i)).toBeDefined();
    });
  });

  it("calls onCancel when cancel button is clicked", () => {
    const onCancel = vi.fn();
    renderModal(undefined, onCancel);

    fireEvent.click(screen.getByRole("button", { name: /cancel/i }));

    expect(onCancel).toHaveBeenCalled();
  });
});
