import axiosInstance from './axios';

export interface Program {
  name: string;
  process_num: number;
  status: string;
}

export interface ProcessStatus {
  status: string;
  process_num: number;
  retries: number;
}

export interface ProgramStatusResponse {
  name: string;
  procs: ProcessStatus[];
  stop_signal: string;
  exit_codes: number[];
}

export async function listPrograms(): Promise<Program[]> {
  const response = await axiosInstance.get('/programs/list');
  return response.data.data;
}

export async function getProgramStatus(serviceName: string): Promise<ProgramStatusResponse> {
  const response = await axiosInstance.get(`/programs/status/${serviceName}`);
  if (response.data.get("error")) {
    throw new Error(response.data.get("error"));
  }
  return response.data.data;
}

export async function startProgram(serviceName: string, processNum: number = 0): Promise<{ success: boolean; message: string }> {
  const url = processNum > 0
    ? `/programs/start/${serviceName}/${processNum}`
    : `/programs/start/${serviceName}`;
  const response = await axiosInstance.post(url);
  if (response.data.get("error")) {
    throw new Error(response.data.get("error"));
  }
  return response.data;
}

export async function stopProgram(serviceName: string, processNum: number = 0): Promise<{ success: boolean; message: string }> {
  const url = processNum > 0
    ? `/programs/stop/${serviceName}/${processNum}`
    : `/programs/stop/${serviceName}`;
  const response = await axiosInstance.post(url);
  if (response.data.get("error")) {
    throw new Error(response.data.get("error"));
  }
  return response.data;
}

export async function restartProgram(serviceName: string, processNum: number = 0): Promise<{ success: boolean; message: string }> {
  const url = processNum > 0
    ? `/programs/restart/${serviceName}/${processNum}`
    : `/programs/restart/${serviceName}`;
  const response = await axiosInstance.post(url);
  if (response.data.get("error")) {
    throw new Error(response.data.get("error"));
  }
  return response.data;
}

export async function getRamUsage(): Promise<any> {
  const response = await axiosInstance.get('/programs/ramUsage');
  if (response.data.get("error")) {
    throw new Error(response.data.get("error"));
  }
  return response.data;
}
