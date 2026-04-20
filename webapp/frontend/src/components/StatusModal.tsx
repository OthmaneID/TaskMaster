import { useEffect, useState } from 'react';
import { X, Info, AlertCircle, CheckCircle, Clock, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';
import { getProgramStatus, type ProgramStatusResponse } from '../lib/api';

interface StatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  serviceName: string;
}

export function StatusModal({ isOpen, onClose, serviceName }: StatusModalProps) {
  const [statusData, setStatusData] = useState<ProgramStatusResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchStatus();
    }
  }, [isOpen, serviceName]);

  const fetchStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getProgramStatus(serviceName);
      setStatusData(data);
    } catch (err) {
      setError('Failed to fetch status');
      console.error('Error fetching status:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    const normalized = status?.toLowerCase();
    if (normalized === 'successful') return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (normalized === 'fatal' || normalized === 'down') return <AlertCircle className="w-5 h-5 text-red-500" />;
    if (normalized === 'starting' || normalized === 'backoff') return <Clock className="w-5 h-5 text-yellow-500" />;
    return <Info className="w-5 h-5 text-gray-500" />;
  };

  const getStatusColor = (status: string) => {
    const normalized = status?.toLowerCase();
    if (normalized === 'successful') return 'bg-green-500/10 text-green-600 dark:text-green-400';
    if (normalized === 'fatal' || normalized === 'down') return 'bg-red-500/10 text-red-600 dark:text-red-400';
    if (normalized === 'starting' || normalized === 'backoff') return 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400';
    return 'bg-gray-500/10 text-gray-600 dark:text-gray-400';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-card border border-border rounded-xl max-w-2xl w-full max-h-[80vh] overflow-hidden shadow-2xl">
        <div className="flex items-center justify-between p-4 border-b border-border bg-muted/50">
          <h2 className="text-lg font-semibold text-foreground">Status: {serviceName}</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-muted rounded-md transition-colors"
          >
            <X className="w-5 h-5 text-foreground" />
          </button>
        </div>

        <div className="p-4 overflow-y-auto max-h-[60vh]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : error ? (
            <div className="flex items-center justify-center py-12 text-red-500">
              <AlertCircle className="w-6 h-6 mr-2" />
              {error}
            </div>
          ) : statusData ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-muted/50 rounded-lg p-3">
                  <p className="text-xs text-muted-foreground mb-1">Stop Signal</p>
                  <p className="text-sm font-medium text-foreground">{statusData.stop_signal}</p>
                </div>
                <div className="bg-muted/50 rounded-lg p-3">
                  <p className="text-xs text-muted-foreground mb-1">Exit Codes</p>
                  <p className="text-sm font-medium text-foreground">{statusData?.exit_codes.join(', ')}</p>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-foreground mb-2">Processes ({statusData.procs.length})</h3>
                <div className="space-y-2">
                  {statusData.procs.map((proc) => (
                    <div
                      key={proc.process_num}
                      className="bg-muted/50 rounded-lg p-3 flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3">
                        {getStatusIcon(proc.status)}
                        <div>
                          <p className="text-sm font-medium text-foreground">Process #{proc.process_num}</p>
                          <p className="text-xs text-muted-foreground">{proc.status}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-xs text-muted-foreground">Retries</p>
                          <p className="text-sm font-medium text-foreground">{proc.retries}</p>
                        </div>
                        <div className={cn(
                          "px-2 py-1 rounded-full text-xs font-medium",
                          getStatusColor(proc.status)
                        )}>
                          {proc.status}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : null}
        </div>

        <div className="p-4 border-t border-border bg-muted/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
