import { API_BASE_URL, POLL_INTERVAL_MS } from './config';

/**
 * Thin client for the backend proxy. Each function maps to one HTTP endpoint.
 */

/** Submit an image + instruction. Returns { job_id, status, ... }. */
export async function createJob(imageUri, prompt) {
  const form = new FormData();
  form.append('prompt', prompt);

  // React Native's FormData accepts a { uri, name, type } file descriptor.
  const name = imageUri.split('/').pop() || 'upload.jpg';
  const match = /\.(\w+)$/.exec(name);
  const type = match ? `image/${match[1].toLowerCase()}` : 'image/jpeg';
  form.append('image', { uri: imageUri, name, type });

  const resp = await fetch(`${API_BASE_URL}/jobs`, {
    method: 'POST',
    body: form,
    headers: { Accept: 'application/json' },
  });
  if (!resp.ok) {
    throw new Error(await readError(resp, 'Failed to start the edit'));
  }
  return resp.json();
}

/** Fetch a job's current status/progress. */
export async function getJob(jobId) {
  const resp = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
  if (!resp.ok) {
    throw new Error(await readError(resp, 'Failed to read job status'));
  }
  return resp.json();
}

/** URL of the finished image — use directly as an <Image> source. */
export function jobImageUrl(jobId) {
  // Cache-bust so a re-run with the same id always reloads.
  return `${API_BASE_URL}/jobs/${jobId}/image?t=${Date.now()}`;
}

/**
 * Poll a job until it completes or fails.
 * @param {(progress:number)=>void} onProgress
 * @returns the final job object (status === 'completed').
 */
export async function pollJob(jobId, onProgress, signal) {
  while (true) {
    if (signal?.aborted) throw new Error('Cancelled');
    const job = await getJob(jobId);
    onProgress?.(job.progress ?? 0);

    if (job.status === 'completed') return job;
    if (job.status === 'failed') {
      throw new Error(job.error || 'The edit failed on the server');
    }
    await delay(POLL_INTERVAL_MS);
  }
}

async function readError(resp, fallback) {
  try {
    const data = await resp.json();
    return data.detail || fallback;
  } catch {
    return `${fallback} (HTTP ${resp.status})`;
  }
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
