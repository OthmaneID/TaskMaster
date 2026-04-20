import { useState } from 'react';
import { ChevronDown, ChevronUp, Play, Square, RefreshCw, Loader2, Info } from 'lucide-react';
import { cn } from '../lib/utils';
import { startProgram, stopProgram, restartProgram, type Program } from '../lib/api';
import { ProgramCard } from './ProgramCard';
import { StatusModal } from './StatusModal';

interface ServiceGroupProps {
  serviceName: string;
  processes: Program[];
  onRefresh: () => void;
}

export function ServiceGroup({ serviceName, processes, onRefresh }: ServiceGroupProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [bulkLoading, setBulkLoading] = useState<string | null>(null);
  const [showStatusModal, setShowStatusModal] = useState(false);

  const handleBulkAction = async (action: string) => {
    setBulkLoading(action);
    try {
      const promise =
        action === 'start' ? startProgram(serviceName) :
          action === 'stop' ? stopProgram(serviceName) :
            action === 'restart' ? restartProgram(serviceName) :
              Promise.resolve();
      await promise;
      onRefresh();
    } catch (error) {
      console.error(`Failed to ${action} all processes:`, error);
    } finally {
      setBulkLoading(null);
    }
  };

  const runningCount = processes.filter(p => p.status?.toLowerCase() === 'successful').length;
  const isAllRunning = runningCount === processes.length;
  const isAllStopped = runningCount === 0;

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/5">
      <div className="p-4 bg-muted/50 border-b border-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1 hover:bg-muted rounded-md transition-colors"
            >
              {isExpanded ? (
                <ChevronUp className="w-5 h-5 text-foreground" />
              ) : (
                <ChevronDown className="w-5 h-5 text-foreground" />
              )}
            </button>
            <div>
              <h3 className="text-lg font-semibold text-foreground">{serviceName}</h3>
              <p className="text-xs text-muted-foreground">{runningCount}/{processes.length} processes running</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowStatusModal(true)}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 bg-muted hover:bg-muted/80 text-foreground"
              title="View status"
            >
              <Info className="w-4 h-4" />
              Status
            </button>
            <button
              onClick={() => handleBulkAction('start')}
              disabled={bulkLoading === 'start' || isAllRunning}
              className={cn(
                "flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200",
                isAllRunning
                  ? "bg-muted text-muted-foreground cursor-not-allowed"
                  : "bg-green-500 hover:bg-green-600 text-white shadow-lg shadow-green-500/20"
              )}
              title="Start all"
            >
              {bulkLoading === 'start' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              Start All
            </button>
            <button
              onClick={() => handleBulkAction('stop')}
              disabled={bulkLoading === 'stop' || isAllStopped}
              className={cn(
                "flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200",
                isAllStopped
                  ? "bg-muted text-muted-foreground cursor-not-allowed"
                  : "bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/20"
              )}
              title="Stop all"
            >
              {bulkLoading === 'stop' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Square className="w-4 h-4" />
              )}
              Stop All
            </button>
            <button
              onClick={() => handleBulkAction('restart')}
              disabled={bulkLoading === 'restart'}
              className={cn(
                "flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200",
                bulkLoading === 'restart'
                  ? "bg-muted text-muted-foreground"
                  : "bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/20"
              )}
              title="Restart all"
            >
              <RefreshCw className={cn("w-4 h-4", bulkLoading === 'restart' && "animate-spin")} />
              Restart All
            </button>
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {processes.map((process) => (
            <ProgramCard
              key={`${process.name}-${process.process_num}`}
              program={process}
              onRefresh={onRefresh}
            />
          ))}
        </div>
      )}

      <StatusModal
        isOpen={showStatusModal}
        onClose={() => setShowStatusModal(false)}
        serviceName={serviceName}
      />
    </div>
  );
}
