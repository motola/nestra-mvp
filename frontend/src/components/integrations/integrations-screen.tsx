"use client";

import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { EmptyDataState } from "@/components/ui/empty-state";

export function IntegrationsScreen() {
  return (
    <>
      <PageHeader
        eyebrow="WORKSPACE"
        title="Integrations"
        sub="0 connections"
        primary={
          <Button variant="primary" icon={Plus}>
            Connect vendor
          </Button>
        }
      />
      <EmptyDataState
        title="No integrations connected"
        description="Connect your first smart home vendor to start syncing devices."
      />
    </>
  );
}
