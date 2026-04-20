import { MemoryStick, TrendingUp } from 'lucide-react';

interface ProcessRamUsage {
  name: string;
  proces: number;
  ram_usage: string | number;
}

interface RamUsageProps {
  ramUsage: ProcessRamUsage[] | null;
  loading: boolean;
}

export function RamUsageDisplay({ ramUsage, loading }: RamUsageProps) {
  if (loading || !ramUsage) {
    return (
      <div className="bg-card border border-border rounded-xl p-6 animate-pulse">
        <div className="flex items-center gap-3 mb-4">
          <MemoryStick className="w-5 h-5 text-muted-foreground" />
          <h3 className="text-lg font-semibold text-foreground">Memory Usage</h3>
        </div>
        <div className="h-32 bg-muted rounded-lg" />
      </div>
    );
  }

  const numericRam = ramUsage
    .filter(p => typeof p.ram_usage === 'number')
    .map(p => p.ram_usage as number);

  const totalRam = numericRam.reduce((sum, val) => sum + val, 0);
  const maxRam = Math.max(...numericRam, 1);

  // Group by program name
  const groupedByProgram = ramUsage.reduce((acc, proc) => {
    if (!acc[proc.name]) {
      acc[proc.name] = [];
    }
    acc[proc.name].push(proc);
    return acc;
  }, {} as Record<string, ProcessRamUsage[]>);

  return (
    <div className="bg-card border border-border rounded-xl p-6 hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <MemoryStick className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-semibold text-foreground">Memory Usage</h3>
        </div>
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <TrendingUp className="w-4 h-4" />
          <span>{(totalRam / 1024).toFixed(2)} MB Total</span>
        </div>
      </div>

      <div className="space-y-3 max-h-64 overflow-y-auto">
        {ramUsage.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">No RAM data available</p>
        ) : (
          Object.entries(groupedByProgram).map(([programName, processes]) => (
            <div key={programName} className="space-y-2">
              <div className="text-sm font-semibold text-foreground">{programName}</div>
              <div className="pl-3 space-y-1">
                {processes.map((proc) => (
                  <div key={`${proc.name}-${proc.proces}`} className="space-y-1">
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-muted-foreground">Process #{proc.proces}</span>
                      <span className="text-muted-foreground">
                        {typeof proc.ram_usage === 'number'
                          ? proc.ram_usage > 1024
                            ? `${(proc.ram_usage / 1024).toFixed(2)} MB`
                            : `${proc.ram_usage} KB`
                          : 'N/A'
                        }
                      </span>
                    </div>
                    {typeof proc.ram_usage === 'number' && (
                      <div className="relative h-1.5 bg-muted rounded-full overflow-hidden">
                        <div
                          className="absolute top-0 left-0 h-full bg-linear-to-r from-primary to-primary/80 rounded-full transition-all duration-500 ease-out"
                          style={{ width: `${(proc.ram_usage / maxRam) * 100}%` }}
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
