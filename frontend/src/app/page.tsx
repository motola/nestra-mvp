import { redirect } from "next/navigation";

// Intelligence is the product home — redirect the root immediately
export default function RootPage() {
  redirect("/intelligence");
}
