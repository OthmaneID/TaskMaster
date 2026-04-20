import { useEffect, useState } from 'react';
import { RefreshCw, Server, Zap, Shield } from 'lucide-react';
import { listPrograms, getRamUsage } from './lib/api';
import { ProgramCard } from './components/ProgramCard';
import { RamUsageDisplay } from './components/RamUsage';

export function App() {
  const [programs, setPrograms] = useState<any[]>([]);
  const [ramUsage, setRamUsage] = useState<Record<string, number> | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      const [programsData, ramData] = await Promise.all([
        listPrograms(),
        getRamUsage()
      ]);
      setPrograms(programsData);
      console.log(programsData)
      setRamUsage(ramData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const runningCount = programs.filter(p => p.status?.toLowerCase() === "successful").length;

  return (
    <div className="min-h-screen bg-linear-to-br from-background via-background to-primary/5">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-primary/10 rounded-xl">
                <Server className="w-8 h-8 text-primary" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-foreground">TaskMaster</h1>
                <p className="text-muted-foreground">Process Management Dashboard</p>
              </div>
            </div>
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center gap-2 px-4 py-2 bg-card border border-border rounded-lg hover:border-primary/50 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5"
            >
              <RefreshCw className={cn("w-4 h-4", refreshing && "animate-spin")} />
              Refresh
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-card border border-border rounded-xl p-6 hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5">
            <div className="flex items-center gap-3 mb-2">
              <Zap className="w-5 h-5 text-green-500" />
              <span className="text-sm text-muted-foreground">Running</span>
            </div>
            <div className="text-3xl font-bold text-foreground">{runningCount}</div>
          </div>

          <div className="bg-card border border-border rounded-xl p-6 hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5">
            <div className="flex items-center gap-3 mb-2">
              <Shield className="w-5 h-5 text-blue-500" />
              <span className="text-sm text-muted-foreground">Total Programs</span>
            </div>
            <div className="text-3xl font-bold text-foreground">{programs.length}</div>
          </div>

          <div className="lg:col-span-2">
            <RamUsageDisplay ramUsage={ramUsage} loading={loading} />
          </div>
        </div>

        <div className="mb-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Programs</h2>
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map(i => (
                <div key={i} className="bg-card border border-border rounded-xl p-6 animate-pulse h-48" />
              ))}
            </div>
          ) : programs.length === 0 ? (
            <div className="bg-card border border-border rounded-xl p-12 text-center">
              <Server className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">No programs found</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {programs.map((program, index) => (
                <ProgramCard
                  key={program.name + index}
                  program={program}
                  onRefresh={fetchData}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ');
}

export default App;
