import { PROPERTIES } from "@/lib/fixtures";
import { PropertyScreen } from "@/components/property/property-screen";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const property = PROPERTIES.find((p) => p.id === id);
  return { title: `${property?.name ?? "Property"} · Alphacon` };
}

export default async function PropertyPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const property = PROPERTIES.find((p) => p.id === id) ?? PROPERTIES[0];
  return <PropertyScreen property={property} />;
}
