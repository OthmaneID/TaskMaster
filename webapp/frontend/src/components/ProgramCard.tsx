import { useState } from 'react';
import { Play, Square, RefreshCw } from 'lucide-react';
import { cn } from '../lib/utils';
import { startProgram, stopProgram, restartProgram, type Program } from '../lib/api';

interface ProgramCardProps {
  program: Program;
  onRefresh: () => void;
}

export function ProgramCard({ program, onRefresh }: ProgramCardProps) {
  const [loading, setLoading] = useState<string | null>(null);
  const isRunning = program.status?.toLowerCase() === 'successful';

  const handleAction = async (action: string, serviceFn: (name: string, processNum?: number) => Promise<any>) => {
    setLoading(action);
    try {
      await serviceFn(program.name, program.process_num);
      onRefresh();
    } catch (error) {
      console.error(`Failed to ${action} program:`, error);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="group relative bg-card border border-border rounded-xl p-6 hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={cn(
            "w-3 h-3 rounded-full animate-pulse",
            isRunning ? "bg-green-500" : "bg-red-500"
          )} />
          <div>
            <h3 className="text-lg font-semibold text-foreground">{program.name}</h3>
            <p className="text-xs text-muted-foreground">Process #{program.process_num}</p>
          </div>
        </div>
        <div className={cn(
          "px-3 py-1 rounded-full text-xs font-medium",
          isRunning
            ? "bg-green-500/10 text-green-600 dark:text-green-400"
            : "bg-red-500/10 text-red-600 dark:text-red-400"
        )}>
          {program.status || 'Unknown'}
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => handleAction('start', startProgram)}
          disabled={loading === 'start' || isRunning}
          className={cn(
            "flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200",
            isRunning
              ? "bg-muted text-muted-foreground cursor-not-allowed"
              : "bg-green-500 hover:bg-green-600 text-white shadow-lg shadow-green-500/20 hover:shadow-green-500/30"
          )}
        >
          <Play className="w-4 h-4" />
          Start
        </button>
        <button
          onClick={() => handleAction('stop', stopProgram)}
          disabled={loading === 'stop' || !isRunning}
          className={cn(
            "flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200",
            !isRunning
              ? "bg-muted text-muted-foreground cursor-not-allowed"
              : "bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/20 hover:shadow-red-500/30"
          )}
        >
          <Square className="w-4 h-4" />
          Stop
        </button>
        <button
          onClick={() => handleAction('restart', restartProgram)}
          disabled={loading === 'restart'}
          className={cn(
            "flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200",
            loading === 'restart'
              ? "bg-muted text-muted-foreground"
              : "bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/20 hover:shadow-primary/30"
          )}
        >
          <RefreshCw className={cn("w-4 h-4", loading === 'restart' && "animate-spin")} />
          Restart
        </button>
      </div>
    </div>
  );
}
