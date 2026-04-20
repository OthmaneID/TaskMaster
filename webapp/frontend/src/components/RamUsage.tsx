import { MemoryStick, TrendingUp } from 'lucide-react';

interface ProgramRamUsage {
  name: string;
  ram_usage: number;
}

interface RamUsageProps {
  ramUsage: Record<string, number> | null;
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

  const programs: ProgramRamUsage[] = Object.entries(ramUsage).map(([name, ram_usage]) => ({
    name,
    ram_usage
  }));

  const totalRam = programs.reduce((sum, p) => sum + p.ram_usage, 0);
  const maxRam = Math.max(...programs.map(p => p.ram_usage), 1);

  return (
    <div className="bg-card border border-border rounded-xl p-6 hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <MemoryStick className="w-5 h-5 text-primary" />
          <h3 className="text-lg font-semibold text-foreground">Memory Usage</h3>
        </div>
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <TrendingUp className="w-4 h-4" />
          <span>{(totalRam / 1024).toFixed(2)} GB Total</span>
        </div>
      </div>

      <div className="space-y-3">
        {programs.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">No RAM data available</p>
        ) : (
          programs.map((program) => (
            <div key={program.name} className="space-y-1">
              <div className="flex justify-between items-center text-sm">
                <span className="text-foreground font-medium">{program.name}</span>
                <span className="text-muted-foreground">
                  {
                    program.ram_usage / 1024 > 1 ?
                      program.ram_usage / 1024 + " MB"
                      :
                      program.ram_usage + " KB"
                  }
                </span>
              </div>
              <div className="relative h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="absolute top-0 left-0 h-full bg-linear-to-r from-primary to-primary/80 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${(program.ram_usage / maxRam) * 100}%` }}
                />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
