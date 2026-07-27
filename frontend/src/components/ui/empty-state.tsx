import { Card } from "./card";

interface EmptyDataStateProps {
  title?: string;
  description?: string;
}

export function EmptyDataState({
  title = "No data",
  description = "Nothing to show here yet.",
}: EmptyDataStateProps) {
  return (
    <div className="px-7 pt-10 pb-8">
      <Card className="p-12 text-center">
        <p className="font-serif text-[24px] text-text-2 m-0">{title}</p>
        <p className="text-[13px] text-text-3 mt-3 max-w-[400px] mx-auto leading-[1.6]">
          {description}
        </p>
      </Card>
    </div>
  );
}
