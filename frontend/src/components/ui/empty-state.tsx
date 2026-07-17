import { Card } from "./card";

export function EmptyDataState() {
  return (
    <div className="px-7 pt-10 pb-8">
      <Card className="p-12 text-center">
        <p className="font-serif text-[24px] text-text-2 m-0">No data</p>
        <p className="text-[13px] text-text-3 mt-3 max-w-[400px] mx-auto leading-[1.6]">
          This view is empty. Enable Demo Mode in the Intelligence tab to see
          sample data.
        </p>
      </Card>
    </div>
  );
}
