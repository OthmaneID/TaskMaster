import axiosInstance from './axios';

export async function listPrograms(): Promise<any[]> {
  const response = await axiosInstance.get('/programs/list');
  return response.data.data
}



export async function getProgramStatus(serviceName: string): Promise<any[]> {
  const response = await axiosInstance.get(`/programs/status/${serviceName}`);

  return response.data;
}


export async function startProgram(serviceName: string): Promise<{ success: boolean; message: string }> {
  const response = await axiosInstance.post(`/programs/start/${serviceName}`);
  return response.data;
}

export async function stopProgram(serviceName: string): Promise<{ success: boolean; message: string }> {
  const response = await axiosInstance.post(`/programs/stop/${serviceName}`);
  console.log(serviceName , " stoped ?: ", response.data)
  return response.data.data;
}

export async function restartProgram(serviceName: string): Promise<{ success: boolean; message: string }> {
  const response = await axiosInstance.post(`/programs/restart/${serviceName}`);
  return response.data;
}

export async function getRamUsage(): Promise<any> { // returns ram usage for each program
  const response = await axiosInstance.get('/programs/ramUsage');
  // console.log("ramUsage : ", response.data)
  return response.data;
}
