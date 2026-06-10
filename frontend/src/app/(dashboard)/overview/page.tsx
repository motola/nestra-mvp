import { redirect } from "next/navigation";

// Overview is retired — Intelligence is now the home pane
export default function OverviewPage() {
  redirect("/intelligence");
}
