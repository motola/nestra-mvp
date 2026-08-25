"use client";

import { useState } from "react";
import { X, Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, SectionHead } from "@/components/ui/card";

interface OAuthTokenModalProps {
  isOpen: boolean;
  vendor: string;
  onClose: () => void;
  onOAuth: () => void;
  onTokenSubmit: (token: string) => void;
}

const VENDOR_DOCS: Record<
  string,
  { name: string; url: string; tokenName: string }
> = {
  lifx: {
    name: "LIFX",
    url: "https://api.lifx.com",
    tokenName: "API Token",
  },
  govee: {
    name: "Govee",
    url: "https://govee.com/account",
    tokenName: "API Key",
  },
  meross: {
    name: "Meross",
    url: "https://meross.com/account",
    tokenName: "Access Token",
  },
  shelly: {
    name: "Shelly",
    url: "https://app.shelly.cloud",
    tokenName: "Auth Token",
  },
};

export function OAuthTokenModal({
  isOpen,
  vendor,
  onClose,
  onOAuth,
  onTokenSubmit,
}: OAuthTokenModalProps) {
  const [token, setToken] = useState("");
  const [copied, setCopied] = useState(false);
  const [useToken, setUseToken] = useState(false);

  const vendorInfo = VENDOR_DOCS[vendor.toLowerCase()] || {
    name: vendor,
    url: "#",
    tokenName: "API Token",
  };

  const handleCopyDocs = () => {
    navigator.clipboard.writeText(vendorInfo.url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSubmit = () => {
    if (token.trim()) {
      onTokenSubmit(token);
      setToken("");
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl mx-4">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <SectionHead
              title={`Connect ${vendorInfo.name}`}
              sub="CHOOSE YOUR AUTHENTICATION METHOD"
            />
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded">
              <X size={20} />
            </button>
          </div>

          {!useToken ? (
            <>
              <div className="space-y-3 mb-4">
                <button
                  onClick={onOAuth}
                  className="w-full p-4 border-2 border-blue-500 rounded-lg hover:bg-blue-50 transition text-left"
                >
                  <p className="font-semibold text-blue-700">OAuth Login</p>
                  <p className="text-sm text-gray-600 mt-1">
                    Sign in with your {vendorInfo.name} account (recommended)
                  </p>
                </button>

                <button
                  onClick={() => setUseToken(true)}
                  className="w-full p-4 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition text-left"
                >
                  <p className="font-semibold text-gray-700">
                    Enter {vendorInfo.tokenName}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    Use an existing API token from your {vendorInfo.name}{" "}
                    account
                  </p>
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
                <p className="text-sm text-blue-800">
                  Get your {vendorInfo.tokenName} from{" "}
                  <button
                    onClick={handleCopyDocs}
                    className="font-semibold underline hover:text-blue-900 inline-flex items-center gap-1"
                  >
                    {vendorInfo.url}
                    {copied ? <Check size={14} /> : <Copy size={14} />}
                  </button>
                </p>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">
                  {vendorInfo.tokenName}
                </label>
                <input
                  type="password"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder={`Paste your ${vendorInfo.name} ${vendorInfo.tokenName.toLowerCase()}`}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex gap-2 justify-end">
                <Button
                  onClick={() => {
                    setUseToken(false);
                    setToken("");
                  }}
                  variant="secondary"
                >
                  Back
                </Button>
                <Button
                  onClick={handleSubmit}
                  disabled={!token.trim()}
                  variant="primary"
                >
                  Connect with Token
                </Button>
              </div>
            </>
          )}
        </div>
      </Card>
    </div>
  );
}
