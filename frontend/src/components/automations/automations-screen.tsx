"use client";

import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { EmptyDataState } from "@/components/ui/empty-state";

export function AutomationsScreen() {
  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Automations"
        sub="0 automations active"
        primary={
          <Button variant="primary" icon={Plus}>
            Create automation
          </Button>
        }
      />
      <EmptyDataState
        title="No automations created"
        description="Set up your first automation to streamline property management."
      />
    </>
  );
}
