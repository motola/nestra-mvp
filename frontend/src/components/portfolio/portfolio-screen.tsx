"use client";

import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { EmptyDataState } from "@/components/ui/empty-state";

export function PortfolioScreen() {
  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Portfolios"
        sub="0 portfolios · 0 properties"
        primary={
          <Button variant="primary" icon={Plus}>
            Add property
          </Button>
        }
      />
      <EmptyDataState
        title="No portfolios yet"
        description="Create your first portfolio to get started managing your properties."
      />
    </>
  );
}
