export default function DataTable<T extends { id: string }>({
  columns, rows, emptyMessage = "No data yet.",
}: {
  columns: { header: string; render: (row: T) => React.ReactNode }[];
  rows: T[];
  emptyMessage?: string;
}) {
  if (rows.length === 0) {
    return <div className="text-sm text-slate-400 py-10 text-center">{emptyMessage}</div>;
  }
  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="text-left text-slate-500 border-b border-slate-200">
          {columns.map((c) => (
            <th key={c.header} className="py-2 px-3 font-medium">{c.header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id} className="border-b border-slate-100 hover:bg-slate-50">
            {columns.map((c) => (
              <td key={c.header} className="py-2 px-3">{c.render(row)}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
