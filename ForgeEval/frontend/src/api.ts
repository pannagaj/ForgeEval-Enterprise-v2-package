const BASE=import.meta.env.VITE_API_URL || 'http://localhost:8000';
export function token(){return localStorage.getItem('forge_token')}
export async function api<T>(path:string,options:RequestInit={}):Promise<T>{
 const response=await fetch(BASE+path,{...options,headers:{'Content-Type':'application/json',...(token()?{Authorization:`Bearer ${token()}`}:{ } ),...options.headers}});
 const body=await response.json().catch(()=>({detail:'Unexpected server response'}));
 if(!response.ok) throw new Error(body.detail || `Request failed (${response.status})`);
 return body as T;
}
